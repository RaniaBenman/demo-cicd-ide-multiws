import unittest
import tempfile
import os
import shutil

from demo_covea_ide_gitinit.jobs.sample.entrypoint import SampleJob
from pyspark.sql import SparkSession
from unittest.mock import MagicMock

class SampleJobUnitTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory().name
        self.spark = SparkSession.builder.master("local[1]").getOrCreate()
        self.test_config = {
            "output_format": "parquet",
            "output_path": os.path.join(self.test_dir, "output"),
        }
        self.job = SampleJob(spark=self.spark, init_conf=self.test_config)

    def test_sample(self):
        # feel free to add new methods to this magic mock to mock some particular functionality
        self.job.dbutils = MagicMock()
        print("******")
        print(os.path.join(os.path.dirname(__file__), '../tests/unit/data/turbines_sample.csv'))
        df = self.spark.read.option("delimiter", ";").option("header", "true").csv(os.path.join(os.path.dirname(__file__), '../tests/unit/data/turbines_sample.csv')).createOrReplaceTempView("hive_metastore.default.turbines")

        self.job.launch()

        output_count = (
            self.spark.read.format(self.test_config["output_format"])
            .load(self.test_config["output_path"])
            .count()
        )

        self.assertGreater(output_count, 0)

    def tearDown(self):
        shutil.rmtree(self.test_dir)


if __name__ == "__main__":
    unittest.main()
