from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("IPL Gold Layer Job") \
    .getOrCreate()

# Read Silver Data
df = spark.read.parquet("data/silver/ipl_cleaned")

# Optimization
df = df.repartition(8, "year")
df.cache()

# Batter Stats

batter_stats = df.groupBy("year","batter").agg(
    sum("runs_batter").alias("total_runs"),
    count("*").alias("balls"),
    sum("is_boundary").alias("boundaries")
)

batter_stats = batter_stats.withColumn(
    "strike_rate",
    round((col("total_runs") / col("balls")) * 100, 2)
)

window_spec = Window.partitionBy("year").orderBy(desc("total_runs"))

batter_stats = batter_stats.withColumn(
    "rank",
    dense_rank().over(window_spec)
)

batter_stats.write.mode("overwrite") \
    .partitionBy("year") \
    .parquet("data/gold/batter_stats")

#  Bowler Stats 

bowler_stats = df.groupBy("year","bowler").agg(
    sum("runs_total").alias("runs_conceded"),
    count("*").alias("balls"),
    sum("is_wicket").alias("wickets")
)

bowler_stats = bowler_stats.withColumn(
    "economy",
    round(col("runs_conceded") / (col("balls") / 6), 2)
)

window_spec2 = Window.partitionBy("year").orderBy(desc("wickets"))

bowler_stats = bowler_stats.withColumn(
    "rank",
    dense_rank().over(window_spec2)
)

bowler_stats.write.mode("overwrite") \
    .partitionBy("year") \
    .parquet("data/gold/bowler_stats")

#  Match Summary 

match_summary = df.groupBy("match_id","year","venue").agg(
    sum("runs_total").alias("match_total_runs"),
    sum("is_wicket").alias("total_wickets")
)

match_summary.write.mode("overwrite") \
    .partitionBy("year") \
    .parquet("data/gold/match_summary")

#  Venue Stats 

venue_stats = df.groupBy("venue","year").agg(
    avg("runs_total").alias("avg_runs"),
    countDistinct("match_id").alias("matches")
)

venue_stats.write.mode("overwrite") \
    .partitionBy("year") \
    .parquet("data/gold/venue_stats")

spark.stop()