# Databricks notebook source
# MAGIC %sql
# MAGIC select * from hive_metastore.default.turbines

# COMMAND ----------

# MAGIC 
# MAGIC %sql
# MAGIC show tables hive_metastore.default;

# COMMAND ----------

from demo_cicd_ide_multiws.common import Job

# COMMAND ----------

class SampleNotebookJob(Job):
        print("******** Launching notebook ********")


# COMMAND ----------

from demo_cicd_ide_multiws.common_dummy import SampleCommonClass
scc = SampleCommonClass()
print(scc.add(a=1,b=2))
print(SampleCommonClass.addstat(1,2))

# COMMAND ----------
