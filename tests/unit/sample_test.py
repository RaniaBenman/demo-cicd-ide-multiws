import unittest
import tempfile
import os
import shutil

from demo_cicd_ide_multiws.jobs.sample.entrypoint import SampleJob
from pyspark.sql import SparkSession
from unittest.mock import MagicMock

class SampleJobUnitTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory().name
        self.spark = SparkSession.builder.master("local[1]").getOrCreate()
        self.test_config = {
            "output_format": "parquet",
            "output_path": os.path.join(self.test_dir, "output"),
            "input_table_name": "turbines",
            "run_mode":"unit",
        }
        self.job = SampleJob(spark=self.spark, init_conf=self.test_config)

    def test_sample(self):
        # feel free to add new methods to this magic mock to mock some particular functionality
        self.job.dbutils = MagicMock()
        print("****Loading test dataset")
        df = self.spark.read.option("delimiter", ",")\
            .option("header", "true")\
            .option("inferSchema" , "true").\
            csv(os.path.join(os.path.dirname(__file__), 'data/turbines_sample.csv'))\
            .createOrReplaceTempView(self.test_config["input_table_name"])

        self.job.launch()

        import mlflow
        from mlflow import spark as mlflow_spark
        from mlflow.models.signature import infer_signature
        from datetime import date
        tag_label_model = "model"
        tag_label_training_date = "training_date"
        tag_value_model = "turbine_gbt"
        tag_value_training_date = date.today().strftime("%Y-%m-%d")

        #finding successful run for our model
        working_model_filter = ' and metrics.AUROC >= 0'#TODO criteria can be in conf file, and differ from env to another
        working_model = mlflow.search_runs(filter_string='tags.'+tag_label_model+'="'+tag_value_model+'" and attributes.status = "FINISHED" and tags.'+tag_label_training_date+'="'+tag_value_training_date+'"'+working_model_filter, order_by=['metrics.AUROC DESC'], max_results=1)#.iloc[0]
        
        self.assertGreater(working_model.size, 0)


    def tearDown(self):
        shutil.rmtree(self.test_dir)


if __name__ == "__main__":
    unittest.main()
