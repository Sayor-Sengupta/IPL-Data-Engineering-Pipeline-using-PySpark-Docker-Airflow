from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .master("local[*]") \
    .appName("IPL Silver Layer") \
    .getOrCreate()
    

df = spark.read.parquet('data/bronze/ipl')


df = df.withColumn("match_type",col("match_type").cast("string"))


df = df.withColumn("is_boundary",when(col("runs_batter")> 4 , 1).otherwise(0))


df = df.withColumn("is_wicket",when(col("wicket_kind").isNotNull(),1).otherwise(0))


df = df.filter(col("valid_ball") == 1)


df_silver = df.select(
    "match_id",
    "batting_team",
    "bowling_team",
    "batter",
    "bowler",
    "over",
    "ball",
    "runs_batter",
    "runs_total",
    "is_boundary",
    "is_wicket",
    "venue",
    "year"
) 


df_silver.write.mode("overwrite")\
                    .parquet("data/silver/ipl_cleaned")