# 以你之前的 v9 镜像为基础环境
FROM swr.cn-southwest-2.myhuaweicloud.com/coisini/pyspark:v9
# 切换为 root 用户确保有权限
USER root
# 创建存放代码的目录（防止原本没有）
RUN mkdir -p /opt/spark/work/
# 将你刚才修改好的本地 wordcount.py 覆盖进镜像里
COPY wordcount.py /opt/spark/work/wordcount.py
