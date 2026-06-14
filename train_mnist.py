import os
import time
import socket
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # 动态 IP 广播，绕过 DNS
    if rank == 0:
        master_ip = socket.gethostbyname(socket.gethostname())
    else:
        master_ip = None
    master_ip = comm.bcast(master_ip, root=0)

    os.environ['MASTER_ADDR'] = master_ip
    os.environ['MASTER_PORT'] = '29500'
    os.environ['RANK'] = str(rank)
    os.environ['WORLD_SIZE'] = str(size)
    os.environ['GLOO_SOCKET_IFNAME'] = 'eth0'

    dist.init_process_group(backend='gloo')
    print(f"==> 进程 {rank}/{size} 初始化成功！Master IP: {master_ip}", flush=True)

    class SimpleCNN(nn.Module):
        def __init__(self):
            super(SimpleCNN, self).__init__()
            self.conv = nn.Conv2d(1, 10, kernel_size=5)
            self.fc = nn.Linear(10 * 12 * 12, 10)
        def forward(self, x):
            x = torch.relu(torch.max_pool2d(self.conv(x), 2))
            x = x.view(-1, 10 * 12 * 12)
            return self.fc(x)

    model = SimpleCNN()
    model = DDP(model)

    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    criterion = nn.CrossEntropyLoss()

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # 彻底断网运行！直接读取镜像里打包好的 /opt/data
    dist.barrier()
    dataset = datasets.MNIST('/opt/data', train=True, download=False, transform=transform)
    sampler = torch.utils.data.distributed.DistributedSampler(dataset, num_replicas=size, rank=rank)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, sampler=sampler)

    if rank == 0:
        print(f"==> 进程 {rank} 开始基于【真实的离线 MNIST 数据集】训练...", flush=True)
        
    start_time = time.time()
    model.train()
    
    for epoch in range(1):
        sampler.set_epoch(epoch)
        for batch_idx, (data, target) in enumerate(dataloader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            if batch_idx % 50 == 0 and rank == 0:
                print(f"Train Epoch: 1 [{batch_idx * len(data)}/{len(dataloader.dataset)}] Loss: {loss.item():.6f}", flush=True)

    end_time = time.time()
    if rank == 0:
        print(f"==> 进程 0 真实 MNIST 训练完成！总耗时: {end_time - start_time:.2f} 秒", flush=True)

if __name__ == '__main__':
    main()