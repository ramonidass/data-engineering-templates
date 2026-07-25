from collections.abc import Iterator

import pytest
from _pytest.tmpdir import TempPathFactory
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark(tmp_path_factory: TempPathFactory) -> Iterator[SparkSession]:
    warehouse = tmp_path_factory.mktemp("spark-warehouse")
    with pytest.MonkeyPatch.context() as monkeypatch:
        # Containers and VPNs often expose an unresolvable hostname. Binding the
        # local test driver explicitly also prevents accidental network exposure.
        monkeypatch.setenv("SPARK_LOCAL_IP", "127.0.0.1")
        session = (
            SparkSession.builder.master("local[2]")
            .appName("tests")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.sql.warehouse.dir", str(warehouse))
            .getOrCreate()
        )
        yield session
        session.stop()
