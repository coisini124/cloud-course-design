from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("WordCount").getOrCreate()

# 读取示例文本（OBS 路径需替换为老师提供的真实路径，或暂不运行此测试直接进入A-1）
lines = spark.sparkContext.textFile("s3a://coisini-spark-data/douban_movies.csv")

word_counts = (
    lines.flatMap(lambda line: line.split())
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: x[1], ascending=False)
)

print("Top 10 words:", word_counts.take(10))
spark.stop()