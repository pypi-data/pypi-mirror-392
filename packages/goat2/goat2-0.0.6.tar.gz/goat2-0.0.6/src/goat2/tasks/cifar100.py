import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms.v2 as transforms
from tqdm import tqdm

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)

transform = transforms.Compose([
    transforms.ToImage(), 
    transforms.ToDtype(torch.float32, scale=True),
    transforms.Resize((224,224), interpolation=transforms.InterpolationMode.BICUBIC),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(30),
    transforms.AutoAugment(),
    transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))
    ])

batch_size = 512
train_dataset = torchvision.datasets.CIFAR100(root="./data", train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.CIFAR100(root="./data", train=False, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, shuffle=True, num_workers=2)

class Block(nn.Module):
    expansion = 1
    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super().__init__()
        self.relu = nn.ReLU(inplace=True)
        
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)

        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        skip = x
        
        out = self.bn1(x)
        out = self.relu(out)

        if self.downsample is not None: skip = self.downsample(out)

        out = self.conv1(out)
        
        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv2(out)

        out += skip
        return out

class BottleNeck(nn.Module):
    expansion = 4
    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super().__init__()
        width = out_channels
        self.relu = nn.ReLU(inplace=True)

        self.bn1 = nn.BatchNorm2d(in_channels)
        self.conv1 = nn.Conv2d(in_channels, width, kernel_size=1, bias=False)

        self.bn2 = nn.BatchNorm2d(width)
        self.conv2 = nn.Conv2d(width, width, kernel_size=3, stride=stride, padding=1, bias=False)

        self.bn3 = nn.BatchNorm2d(width)
        self.conv3 = nn.Conv2d(width, out_channels * self.expansion, kernel_size=3, padding=1, bias=False)

        self.downsample = downsample
        self.stride = stride
    
    def forward(self, x):
        skip = x
        
        out = self.bn1(x)
        out = self.relu(out)

        if self.downsample is not None: skip = self.downsample(out)
        
        out = self.conv1(out)

        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv2(out)

        out = self.bn3(out)
        out = self.relu(out)
        out = self.conv3(out)

        out += skip
        return out
        

class ResNet(nn.Module):
    def __init__(self, block, num_classes, layers):
        super().__init__()
        self.width = 64
        self.conv1 = nn.Conv2d(3, self.width, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.width)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(2)

        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)

        self.bn_final = nn.BatchNorm2d(512 * block.expansion)
        self.relu_final = nn.ReLU(inplace=True)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)
        
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.bn_final(x)
        x = self.relu_final(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x
        
    def _make_layer(self, block, out_channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.width != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.width, 
                    out_channels * block.expansion, 
                    kernel_size=1, 
                    stride=stride, 
                    bias=False
                )
            )

        layers = []
        layers.append(block(self.width, out_channels, stride, downsample))
        self.width = out_channels * block.expansion
        
        for _ in range(1, blocks):
            layers.append(block(self.width, out_channels))

        return nn.Sequential(*layers)


model = ResNet(Block, 100, [2,2,2,2]).to(device)
load = False
if load:
    state_dict = torch.load('models/cifar100model1.pth', map_location='cuda')
    model.load_state_dict(state_dict)

criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)
# optimizer = optim.AdamW(model.parameters(), lr=0.01)
# scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
def lr_lambda(epoch):
    if epoch < 20:  
        return 0.1
    elif epoch < 40:
        return 0.01
    elif epoch < 60:  
        return 0.001
    else:
        return 3e-4
scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

EPOCH = 40
for epoch in range(EPOCH):
    print(f"\nEpoch {epoch + 1}/{EPOCH}")
    model.train()  # set model to training mode
    running_loss, correct, total = 0.0, 0, 0

    for i, (inputs, labels) in enumerate(tqdm(train_loader, total=len(train_loader))):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_loss = running_loss / len(train_loader)
    train_acc = 100 * correct / total

    model.eval() 
    val_loss, val_correct, val_total = 0.0, 0, 0

    with torch.no_grad():  # disable gradient computation
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()

            _, predicted = torch.max(outputs, 1)
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()

    val_loss /= len(test_loader)
    val_acc = 100 * val_correct / val_total

    print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
    print(f"Val   Loss: {val_loss:.4f} | Val   Acc: {val_acc:.2f}%")

    # scheduler.step()

PATH = 'models/cifar100model1.pth'
torch.save(model.state_dict(), PATH)

correct = 0
total = 0
with torch.no_grad():
    for data in test_loader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f'Accuracy: {100 * correct // total} %')

