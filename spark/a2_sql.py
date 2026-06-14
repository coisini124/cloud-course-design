from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, avg, count, row_number, split, explode

# 初始化 SparkSession
spark = SparkSession.builder.appName("DoubanSQLAnalysis").getOrCreate()

# 强制屏蔽 INFO 刷屏，只看结果
spark.sparkContext.setLogLevel("WARN")

# 你的 OBS 路径
file_path = "s3a://coisini-spark-data/douban_movies.csv"
df = spark.read.csv(file_path, header=True, inferSchema=True)

df = df.dropna(subset=['rating_score', 'year', 'genres'])

# 注册为临时视图，方便直接写 SQL
df.createOrReplaceTempView("movies")

print("========== 查询 1：GROUP BY 聚合 + ORDER BY Top-N ==========")
top_years_sql = """
    SELECT year as `年份`, COUNT(*) as `电影数量` 
    FROM movies 
    GROUP BY year 
    ORDER BY `电影数量` DESC 
    LIMIT 10
"""
top_years_df = spark.sql(top_years_sql)
top_years_df.show()


print("========== 查询 2：时间维度趋势分析 ==========")
trend_sql = """
    SELECT year as `年份`, ROUND(AVG(rating_score), 2) as `平均评分` 
    FROM movies 
    WHERE year >= 2000 AND year <= 2020
    GROUP BY year 
    ORDER BY year ASC
"""
trend_df = spark.sql(trend_sql)
trend_df.show(21)


print("========== 查询 3：窗口函数 (Window Function) ==========")
window_sql = """
    SELECT `年份`, title as `片名`, rating_score as `评分`, `排名`
    FROM (
        SELECT year as `年份`, title, rating_score,
               ROW_NUMBER() OVER (PARTITION BY year ORDER BY rating_score DESC) as `排名`
        FROM movies
        WHERE year IN (2018.0, 2019.0, 2020.0)
    ) ranked_movies
    WHERE `排名` <= 2
    ORDER BY `年份` DESC, `排名` ASC
"""
window_df = spark.sql(window_sql)
window_df.show()


print("========== 查询 4：JOIN 操作 ==========")
mapping_data = [(9.0, "神作"), (8.0, "佳作"), (7.0, "良作"), (6.0, "及格")]
mapping_df = spark.createDataFrame(mapping_data, ["底线分数", "评级"])

movies_with_floor = df.withColumn("底线分数", (col("rating_score") - (col("rating_score") % 1.0)))

join_df = movies_with_floor.join(mapping_df, on="底线分数", how="inner") \
    .groupBy("评级").agg(count("*").alias("电影数量")) \
    .orderBy(col("电影数量").desc())
join_df.show()

spark.stop()