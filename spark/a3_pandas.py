import pandas as pd
import time

print("开始 Pandas 单机性能测试...")
start_time = time.time()

# 读取本地 CSV 文件
df = pd.read_csv('douban_movies.csv', low_memory=False)

# 清理空值并进行 GROUP BY 和排序 (使用真实的英文列名 year)
df = df.dropna(subset=['year'])

# 按照 year 分组，并重命名列名以美化输出
top_years = df.groupby('year').size().reset_index(name='电影数量')
top_years = top_years.rename(columns={'year': '年份'})
top_years = top_years.sort_values(by='电影数量', ascending=False).head(10)

# 强制触发计算并打印
print(top_years)

end_time = time.time()
pandas_time = end_time - start_time
print(f"【Pandas (单机) 执行耗时】: {pandas_time:.4f} 秒")