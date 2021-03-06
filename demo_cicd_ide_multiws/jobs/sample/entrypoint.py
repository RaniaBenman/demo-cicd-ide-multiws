from demo_cicd_ide_multiws.common import Job

#once the data is ready, we can train a model
from datetime import date
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
        self.logger.info("******** Launching CICD Demo job ********")
        listing = self.dbutils.fs.ls("dbfs:/")

        for l in listing:
            self.logger.info(f"DBFS directory: {l}")

        print("******** My random print ********")
        df = self.spark.range(0, 1000)

        df.write.format(self.conf["output_format"]).mode("overwrite").save(
            self.conf["output_path"]
        )
# Added comment
        model_name = "demo_cicd_ide_multiws"
        model_reg_name = "demo_cicd_ide_multiws"#TODO change with spaces
        experiment_workspace_dir = "/demo/cicd/ide_multiws"

        tag_label_model = "model"
        tag_label_training_date = "training_date"
        tag_value_model = "turbine_gbt"
        tag_value_training_date = date.today().strftime("%Y-%m-%d")

        #-----------------1 - READ turbine data from PRE-EXISTING table------------------------------
        #-------table name in conf file : conf/test/sample.yml
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

            #-----------------2-TRAIN model for turbine status prediction, based on data-----------
            pipelineTrained = pipeline.fit(training)
            mlflow.spark.log_model(pipelineTrained, model_name)

            #-----------------3-TEST model and log these eval metrics w MLFlow---------------------
            predictions = pipelineTrained.transform(test)
            metrics = BinaryClassificationMetrics(predictions.select(['prediction', 'label']).rdd)

            # Area under precision-recall curve
            mlflow.log_metric("PRAOC", metrics.areaUnderPR)

            # Area under ROC curve
            mlflow.log_metric("AUROC", metrics.areaUnderROC)

            mlflow.set_tag(tag_label_model, tag_value_model)
            mlflow.set_tag(tag_label_training_date, tag_value_training_date)

            print(metrics.areaUnderPR)#***Focus point : simulate error by renaming var to metrics_extra and watching local output
            print(metrics.areaUnderROC)#***Focus point : print output is viewable locally upon execution

        #-----------------------4-Check if BEST model---------------------------------------------
        #skipped for unit tests 'cause no history':
        if self.conf["run_mode"] == "main":
            #if in prod (main run, not unit tests, nor integ tests)
            #less restritive way: allow model registry on integration, with: != "unit":

            #finding BEST run for our model
            best_model_filter = ' and metrics.AUROC > 0.7'#TODO criteria can be in conf file, and differ from env to another
            best_model = mlflow.search_runs(filter_string='tags.'+tag_label_model+'="'+tag_value_model+'" and attributes.status = "FINISHED"' + best_model_filter, order_by=['metrics.AUROC DESC'], max_results=1).iloc[0]

            '''
            #extra sauce - today ranked at the top but had same performance as previous run -> don't register (TODO test & clean up )
            best_models = mlflow.search_runs(filter_string='tags.'+tag_label_model+'="'+tag_value_model+'" and attributes.status = "FINISHED"' + best_model_filter, order_by=['metrics.AUROC DESC'], max_results=2)
            if best_modelS.iloc[0].get("metrics.AUROC"+tag_label_training_date) == best_modelS.iloc[1].get("metrics.AUROC"+tag_label_training_date) && ( best_models.iloc[0].get("tags."+tag_label_training_date) == tag_value_training_date || best_models.iloc[1].get("tags."+tag_label_training_date) == tag_value_training_date )
                #saving model
                model_uri = best_model.artifact_uri
                model_registered = mlflow.register_model(model_uri+"/"+model_name, model_reg_name)
            else:
                print("********Not your best work...
            '''    

            #making sure TODAY's run turned out to be the BEST ever for our model!
            best_model_training_date = best_model.get("tags."+tag_label_training_date)
            if best_model_training_date == tag_value_training_date:

                #-----------------------5-REGISTER model-------------------------------------------
                #saving model
                model_uri = best_model.artifact_uri
                model_registered = mlflow.register_model(model_uri+"/"+model_name, model_reg_name)
            else:
                print("********Not your best work... Didn't register model.********")
                self.logger.info("********Didn't register model. Keep trying********")
        #------------------------------------------------------------------
        self.logger.info("********Sample job finished!********")

        #///////////////////////////


if __name__ == "__main__":
    job = SampleJob()
    job.launch()
