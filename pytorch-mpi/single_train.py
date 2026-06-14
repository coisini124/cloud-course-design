import time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv = nn.Conv2d(1, 10, kernel_size=5)
        self.fc = nn.Linear(10 * 12 * 12, 10)
    def forward(self, x):
        x = torch.relu(torch.max_pool2d(self.conv(x), 2))
        x = x.view(-1, 10 * 12 * 12)
        return self.fc(x)

def main():
    print("==> 开始单机跑真实 MNIST 数据集...")
    model = SimpleCNN()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    criterion = nn.CrossEntropyLoss()

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    # 直接读取本地 ./data 目录下的真实数据
    dataset = datasets.MNIST('./data', train=True, download=False, transform=transform)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=True)

    start_time = time.time()
    model.train()
    
    for epoch in range(1):
        for batch_idx, (data, target) in enumerate(dataloader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

    end_time = time.time()
    print(f"==> 单机真实 MNIST 训练完成！总耗时: {end_time - start_time:.2f} 秒")

if __name__ == '__main__':
    main()