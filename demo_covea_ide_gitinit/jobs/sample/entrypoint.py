from demo_covea_ide_gitinit.common import Job

#once the data is ready, we can train a model
import mlflow
from mlflow import spark as mlflow_spark

import pandas as pd
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.mllib.evaluation import BinaryClassificationMetrics

from pyspark.ml.classification import GBTClassifier
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
from pyspark.mllib.evaluation import MulticlassMetrics
from mlflow.models.signature import infer_signature

class SampleJob(Job):

    def launch(self):
        self.logger.info("********Launching sample job")
        listing = self.dbutils.fs.ls("dbfs:/")

        for l in listing:
            self.logger.info(f"DBFS directory: {l}")

        print("*********My random print")
        df = self.spark.range(0, 1000)

        df.write.format(self.conf["output_format"]).mode("overwrite").save(
            self.conf["output_path"]
        )

        #-----------------------Added!-----------------------------
        client_model_tag = "turbine_gbt_covea"
        experiment_workspace_dir = "/covea/demo_covea_ide/dbxgitinit"

        print(self.conf["input_table_name"])
        dataset = self.spark.read.table(self.conf["input_table_name"])

        mlflow.set_experiment(experiment_workspace_dir) #not needed in notebook
        mlflow.autolog(exclusive=False)

        with mlflow.start_run():

            # Split dataset into training and test set
            training, test = dataset.limit(1000).randomSplit([0.9, 0.1], seed = 5)
          
            gbt = GBTClassifier(labelCol="label", featuresCol="features").setMaxIter(5)
            grid = ParamGridBuilder().addGrid(gbt.maxDepth, [3,4,5,10,15,25,30]).build()

            mcEvaluator = MulticlassClassificationEvaluator(metricName="f1")
            cv = CrossValidator(estimator=gbt, estimatorParamMaps=grid, evaluator=mcEvaluator, numFolds=2)

            featureCols = ["AN3", "AN4", "AN5", "AN6", "AN7", "AN8", "AN9", "AN10"]
            stages = [
                VectorAssembler(inputCols=featureCols, outputCol="va"), 
                StandardScaler(inputCol="va", outputCol="features"),
                StringIndexer(inputCol="status", outputCol="label"), 
                cv
            ]
            pipeline = Pipeline(stages=stages)

            pipelineTrained = pipeline.fit(training)

            predictions = pipelineTrained.transform(test)
            metrics = BinaryClassificationMetrics(predictions.select(['prediction', 'label']).rdd)

            # Area under precision-recall curve
            mlflow.log_metric("PRAOC", metrics.areaUnderPR)

            # Area under ROC curve
            mlflow.log_metric("AUROC", metrics.areaUnderROC)
            mlflow.log_param("custom_loggable_param", "dummy value")#***Focus point : Last. Custom tags. (why tags? TODO)

            mlflow.set_tag("model", client_model_tag)
            print(metrics.areaUnderPR)#***Focus point : simulate error by renaming var to metrics_extra and watching local output
            print(metrics.areaUnderROC)#***Focus point : print output is viewable locally upon execution

        #----------------------------------------------------

        self.logger.info("*******Sample job finished!")


if __name__ == "__main__":
    job = SampleJob()
    job.launch()
