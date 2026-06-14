import time
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DoubanA3Performance").getOrCreate()

# 强制屏蔽 INFO 刷屏，只看耗时和结果
spark.sparkContext.setLogLevel("WARN")

# 你真实的 OBS 路径
file_path = "s3a://coisini-spark-data/douban_movies.csv"

print("开始 PySpark 分布式性能测试...")
start_time = time.time()

df = spark.read.csv(file_path, header=True, inferSchema=True)
# 必须使用英文真实列名进行过滤
df = df.dropna(subset=['year'])
df.createOrReplaceTempView("movies")

# 执行相同的 SQL 查询，使用 AS 别名汉化表头
sql_query = """
    SELECT year as `年份`, COUNT(*) as `电影数量` 
    FROM movies 
    GROUP BY year 
    ORDER BY `电影数量` DESC 
    LIMIT 10
"""
# 调用 collect() 强制触发 action 计算
result = spark.sql(sql_query).collect()

for row in result:
    print(row)

end_time = time.time()
spark_time = end_time - start_time
print(f"【PySpark 执行耗时】: {spark_time:.4f} 秒")

spark.stop()