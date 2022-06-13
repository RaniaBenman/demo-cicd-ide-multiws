import unittest

from demo_cicd_ide_multiws.jobs.sample.entrypoint import SampleJob
from uuid import uuid4
from pyspark.dbutils import DBUtils  # noqa


class SampleJobIntegrationTest(unittest.TestCase):#Job?
    def setUp(self):

        self.test_dir = "dbfs:/tmp/tests/sample/%s" % str(uuid4())
        self.test_config = {
            "output_format": "delta",
            "output_path": self.test_dir,
            "input_table_name": "hive_metastore.default.turbines",
            "run_mode": "integration",
        }#self.conf["input_table_name"]}

        self.job = SampleJob(init_conf=self.test_config)
        self.dbutils = DBUtils(self.job.spark)
        self.spark = self.job.spark


    def test_sample(self):

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
        
        self.assertGreater(working_model.size, 0.7)

    def tearDown(self):
        self.dbutils.fs.rm(self.test_dir, True)


if __name__ == "__main__":
    # please don't change the logic of test result checks here
    # it's intentionally done in this way to comply with jobs run result checks
    # for other tests, please simply replace the SampleJobIntegrationTest with your custom class name
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(SampleJobIntegrationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    if not result.wasSuccessful():
        raise RuntimeError(
            "One or multiple tests failed. Please check the job logs for additional information."
        )
