# Databricks notebook source
# MAGIC %sql
# MAGIC select * from hive_metastore.default.turbines_original 

# COMMAND ----------

# MAGIC 
# MAGIC %sql
# MAGIC show tables hive_metastore.default;--todo

# COMMAND ----------

from demo_cicd_ide_multiws.common import Job

# COMMAND ----------

