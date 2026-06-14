FROM python:3.9-slim

# 替换为国内 APT 源加速下载
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources || true
RUN apt-get update && apt-get install -y openssh-server openmpi-bin libopenmpi-dev && rm -rf /var/lib/apt/lists/*

# 解决 Worker Pod 找不到 sshd 的错误
RUN mkdir -p /var/run/sshd

# 安装 PyTorch 和 mpi4py
RUN pip install --no-cache-dir torch torchvision mpi4py -i https://pypi.tuna.tsinghua.edu.cn/simple

# 把刚才下载好的真实数据烤进镜像
COPY ./data /opt/data
