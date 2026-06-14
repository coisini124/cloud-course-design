from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan, when, count

# 初始化 SparkSession
spark = SparkSession.builder.appName("DoubanDataCleaning").getOrCreate()

# 真实 OBS 路径保持不变
file_path = "s3a://coisini-spark-data/douban_movies.csv"

print("========== 1. 读取数据与 Schema ==========")
df = spark.read.csv(file_path, header=True, inferSchema=True)
df.printSchema()

print("========== 2. 前 5 行数据 ==========")
df.show(5)

original_count = df.count()
print(f"【原始数据总行数】: {original_count}")

print("========== 3. 各字段缺失值比例 ==========")
missing_exprs = [count(when(col(c).isNull() | isnan(c), c)).alias(c) for c in df.columns]
missing_counts = df.select(*missing_exprs).collect()[0].asDict()
for c, m_count in missing_counts.items():
    ratio = (m_count / original_count) * 100
    print(f"字段 '{c}' 缺失比例: {ratio:.2f}% ({m_count} 行)")

print("========== 4. 执行数据清洗 (2种策略) ==========")
# 策略 1：修改为真实的英文列名 (movie_id, title)
df_clean = df.dropna(subset=['movie_id', 'title'])

# 策略 2：修改为真实的英文列名 (rating_score, year)
df_clean = df_clean.fillna({'rating_score': 0.0, 'year': '未知'})

print("========== 5. 清洗前后行数对比 ==========")
cleaned_count = df_clean.count()
print(f"【清洗前总行数】: {original_count}")
print(f"【清洗后总行数】: {cleaned_count}")
print(f"【共剔除缺失数据】: {original_count - cleaned_count} 行")

print("========== 6. 清洗后数据基本统计信息 ==========")
df_clean.drop("summary").describe().show()

spark.stop()