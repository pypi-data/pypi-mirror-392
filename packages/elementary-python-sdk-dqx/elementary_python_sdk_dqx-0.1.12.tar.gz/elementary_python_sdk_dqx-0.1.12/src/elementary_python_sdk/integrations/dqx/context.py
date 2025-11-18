import sys
import traceback
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

import pytz
from databricks.labs.dqx.rule import Criticality, DQRule
from elementary_python_sdk.core.cloud.request import ElementaryObject
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.test_context import TestContext
from elementary_python_sdk.core.types.asset import TableAsset
from elementary_python_sdk.core.types.test import (
    Test,
    TestExecution,
    TestExecutionStatus,
    TestSeverity,
    TestType,
)
from pyspark.sql import DataFrame
from pyspark.sql.column import Column
from pyspark.sql.functions import col, count, explode
from pyspark.sql.functions import max as spark_max

logger = get_logger()

DQX_ERROR_FIELD_TO_STATUS = {
    "_errors": TestExecutionStatus.FAIL,
    "_warnings": TestExecutionStatus.WARN,
}

DATABASE_TYPE = "databricks"


class DQXTestContext(TestContext):
    def __init__(self, asset: TableAsset, dqx_rules: list[DQRule]):
        self.start_time = datetime.now(pytz.utc)
        self.sql_code_per_test: dict[str, str | None] = {}
        self.asset = asset
        self.tests = self._get_tests(dqx_rules)
        self.test_executions: dict[str, TestExecution] = {}
        self.test_to_subtype = {
            rule.name: rule.check_func.__name__ for rule in dqx_rules
        }

    def get_elementary_objects(self) -> list[ElementaryObject]:
        objects: list[ElementaryObject] = []
        objects.append(self.asset)
        objects.extend([*self.tests.values()])
        objects.extend([*self.test_executions.values()])
        return objects

    def record_results(self, validated_df: DataFrame):
        self.validated_df = validated_df

        for error_field, status in DQX_ERROR_FIELD_TO_STATUS.items():
            aggregated_errors = (
                validated_df.withColumn("dqx_error", explode(col(error_field)))
                .groupBy("dqx_error.name")
                .agg(
                    count("dqx_error.name").alias("failure_count"),
                    spark_max("dqx_error.message").alias("message"),
                )
            )

            for test_name, failure_count, message in aggregated_errors.collect():
                test = self.tests[test_name]
                self.test_executions[test_name] = TestExecution(
                    test_id=test.id,
                    test_sub_unique_id=test.id,
                    sub_type=self.test_to_subtype[test_name],
                    failure_count=failure_count,
                    status=status,
                    code=self.sql_code_per_test[test_name],
                    start_time=self.start_time,
                    duration_seconds=(
                        datetime.now(pytz.utc) - self.start_time
                    ).total_seconds(),
                    description=message,
                )

        for test in self.tests.values():
            if test.name not in self.test_executions:
                self.test_executions[test.name] = TestExecution(
                    test_id=test.id,
                    test_sub_unique_id=test.id,
                    sub_type=self.test_to_subtype[test.name],
                    failure_count=0,
                    status=TestExecutionStatus.PASS,
                    code=self.sql_code_per_test[test.name],
                    start_time=self.start_time,
                    duration_seconds=(
                        datetime.now(pytz.utc) - self.start_time
                    ).total_seconds(),
                    description="Yay test succeeded",
                )

    def record_exception_results(self):
        _, exc_value, _ = sys.exc_info()

        for test in self.tests.values():
            self.test_executions[test.name] = TestExecution(
                test_id=test.id,
                test_sub_unique_id=test.id,
                failure_count=0,
                status=TestExecutionStatus.ERROR,
                code=self.sql_code_per_test[test.name],
                start_time=self.start_time,
                duration_seconds=(
                    datetime.now(pytz.utc) - self.start_time
                ).total_seconds(),
                exception=str(exc_value),
                traceback=traceback.format_exc(),
                description="Something horrible happened",
            )

    def _get_sql_code(self, dqx_rule: DQRule) -> str | None:
        if hasattr(dqx_rule, "check"):
            check = dqx_rule.check
            if isinstance(check, tuple):
                check = check[0]
            return str(check._expr) if hasattr(check, "_expr") else None
        return None

    def _get_tests(self, dqx_rules: list[DQRule]) -> dict[str, Test]:
        tests = {}
        for dqx_rule in dqx_rules:
            config = dqx_rule.to_dict()["check"]
            sql_code = self._get_sql_code(dqx_rule)
            test = Test(
                name=dqx_rule.name,
                test_type=TestType.DQX,
                asset_id=self.asset.id,
                column_name=self._parse_column_name(dqx_rule.column),
                severity=(
                    TestSeverity.ERROR
                    if dqx_rule.criticality == Criticality.ERROR.value
                    else TestSeverity.WARNING
                ),
                config=config,
                meta=dqx_rule.user_metadata,
            )
            self.sql_code_per_test[test.name] = sql_code
            tests[test.name] = test
        return tests

    @staticmethod
    def _parse_column_name(column: str | Column | None) -> str | None:
        if isinstance(column, str):
            return column
        elif isinstance(column, Column):
            # NOTE - apparently there isn't an easy way to get the column SQL from a Column object.
            # to get around it I used the code below.

            # Spark Connect (Python client -> remote Spark)
            if hasattr(column, "_expr") and isinstance(column._expr, str):
                return column._expr

            # Classic PySpark (JVM-backed)
            if hasattr(column, "_jc") and column._jc is not None:
                return str(column._jc)

            return None
        else:
            return None


@contextmanager
def dqx_test_context(
    asset: TableAsset, dqx_rules: list[DQRule]
) -> Generator[DQXTestContext, None, None]:
    if asset.db_type is None:
        asset.db_type = DATABASE_TYPE
    test_context = DQXTestContext(asset, dqx_rules)
    try:
        yield test_context
    except Exception as e:
        logger.exception(f"Error in dqx test context: {e}")
        test_context.record_exception_results()
        raise e
    finally:
        print("All tests:")
        print(test_context.tests)
        print("All test executions:")
        print(test_context.test_executions)
