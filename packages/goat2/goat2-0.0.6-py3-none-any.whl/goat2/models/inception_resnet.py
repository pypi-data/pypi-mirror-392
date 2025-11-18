"""
Inception-ResNet implementations based on "Inception-v4, Inception-ResNet and the Impact of Residual Connections on Learning"
https://arxiv.org/abs/1602.07261
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List, Callable


class BasicConv2d(nn.Module):
    """Basic convolution module: Conv2d + BN + ReLU"""
    def __init__(
        self, 
        in_channels: int, 
        out_channels: int, 
        **kwargs
    ) -> None:
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, bias=False, **kwargs)
        self.bn = nn.BatchNorm2d(out_channels, eps=0.001)
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        return x


class Stem(nn.Module):
    """Stem for both Inception-ResNet v1 and v2"""
    def __init__(self, in_channels: int = 3) -> None:
        super().__init__()
        self.conv2d_1a = BasicConv2d(in_channels, 32, kernel_size=3, stride=2, padding=0)
        self.conv2d_2a = BasicConv2d(32, 32, kernel_size=3, stride=1, padding=0)
        self.conv2d_2b = BasicConv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.maxpool_3a = nn.MaxPool2d(kernel_size=3, stride=2, padding=0)
        self.conv2d_3b = BasicConv2d(64, 80, kernel_size=1, stride=1, padding=0)
        self.conv2d_4a = BasicConv2d(80, 192, kernel_size=3, stride=1, padding=0)
        self.conv2d_4b = BasicConv2d(192, 256, kernel_size=3, stride=2, padding=0)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv2d_1a(x)
        x = self.conv2d_2a(x)
        x = self.conv2d_2b(x)
        x = self.maxpool_3a(x)
        x = self.conv2d_3b(x)
        x = self.conv2d_4a(x)
        x = self.conv2d_4b(x)
        return x


class InceptionResnetA(nn.Module):
    """Inception-ResNet-A block for Inception-ResNet v1 and v2"""
    def __init__(self, in_channels: int, scale: float = 1.0) -> None:
        super().__init__()
        self.scale = scale
        
        self.branch0 = BasicConv2d(in_channels, 32, kernel_size=1, stride=1, padding=0)
        
        self.branch1_0 = BasicConv2d(in_channels, 32, kernel_size=1, stride=1, padding=0)
        self.branch1_1 = BasicConv2d(32, 32, kernel_size=3, stride=1, padding=1)
        
        self.branch2_0 = BasicConv2d(in_channels, 32, kernel_size=1, stride=1, padding=0)
        self.branch2_1 = BasicConv2d(32, 48, kernel_size=3, stride=1, padding=1)
        self.branch2_2 = BasicConv2d(48, 64, kernel_size=3, stride=1, padding=1)
        
        self.conv = nn.Conv2d(128, in_channels, kernel_size=1, stride=1, padding=0, bias=False)
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x0 = self.branch0(x)
        
        x1 = self.branch1_0(x)
        x1 = self.branch1_1(x1)
        
        x2 = self.branch2_0(x)
        x2 = self.branch2_1(x2)
        x2 = self.branch2_2(x2)
        
        mixed = torch.cat([x0, x1, x2], dim=1)
        up = self.conv(mixed)
        
        # Apply scaling to stabilize training
        x += self.scale * up
        x = self.relu(x)
        return x


class InceptionResnetB(nn.Module):
    """Inception-ResNet-B block for Inception-ResNet v1 and v2"""
    def __init__(self, in_channels: int, scale: float = 1.0) -> None:
        super().__init__()
        self.scale = scale
        
        self.branch0 = BasicConv2d(in_channels, 192, kernel_size=1, stride=1, padding=0)
        
        self.branch1_0 = BasicConv2d(in_channels, 128, kernel_size=1, stride=1, padding=0)
        self.branch1_1 = BasicConv2d(128, 160, kernel_size=(1, 7), stride=1, padding=(0, 3))
        self.branch1_2 = BasicConv2d(160, 192, kernel_size=(7, 1), stride=1, padding=(3, 0))
        
        self.conv = nn.Conv2d(384, in_channels, kernel_size=1, stride=1, padding=0, bias=False)
        self.relu = nn.ReLU(inplace=True)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x0 = self.branch0(x)
        
        x1 = self.branch1_0(x)
        x1 = self.branch1_1(x1)
        x1 = self.branch1_2(x1)
        
        mixed = torch.cat([x0, x1], dim=1)
        up = self.conv(mixed)
        
        # Apply scaling to stabilize training
        x += self.scale * up
        x = self.relu(x)
        return x


class InceptionResnetC(nn.Module):
    """Inception-ResNet-C block for Inception-ResNet v1 and v2"""
    def __init__(self, in_channels: int, scale: float = 1.0, activation: bool = True) -> None:
        super().__init__()
        self.scale = scale
        self.activation = activation
        
        self.branch0 = BasicConv2d(in_channels, 192, kernel_size=1, stride=1, padding=0)
        
        self.branch1_0 = BasicConv2d(in_channels, 192, kernel_size=1, stride=1, padding=0)
        self.branch1_1 = BasicConv2d(192, 224, kernel_size=(1, 3), stride=1, padding=(0, 1))
        self.branch1_2 = BasicConv2d(224, 256, kernel_size=(3, 1), stride=1, padding=(1, 0))
        
        self.conv = nn.Conv2d(448, in_channels, kernel_size=1, stride=1, padding=0, bias=False)
        if self.activation:
            self.relu = nn.ReLU(inplace=True)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x0 = self.branch0(x)
        
        x1 = self.branch1_0(x)
        x1 = self.branch1_1(x1)
        x1 = self.branch1_2(x1)
        
        mixed = torch.cat([x0, x1], dim=1)
        up = self.conv(mixed)
        
        # Apply scaling to stabilize training
        x += self.scale * up
        if self.activation:
            x = self.relu(x)
        return x


class ReductionA(nn.Module):
    """Reduction-A block for Inception-ResNet v1 and v2"""
    def __init__(self, in_channels: int, k: int, l: int, m: int, n: int) -> None:
        super().__init__()
        self.branch0 = BasicConv2d(in_channels, n, kernel_size=3, stride=2, padding=0)
        
        self.branch1_0 = BasicConv2d(in_channels, k, kernel_size=1, stride=1, padding=0)
        self.branch1_1 = BasicConv2d(k, l, kernel_size=3, stride=1, padding=1)
        self.branch1_2 = BasicConv2d(l, m, kernel_size=3, stride=2, padding=0)
        
        self.branch2 = nn.MaxPool2d(kernel_size=3, stride=2, padding=0)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x0 = self.branch0(x)
        x1 = self.branch1_0(x)
        x1 = self.branch1_1(x1)
        x1 = self.branch1_2(x1)
        x2 = self.branch2(x)
        return torch.cat([x0, x1, x2], dim=1)


class ReductionB(nn.Module):
    """Reduction-B block for Inception-ResNet v1 and v2"""
    def __init__(self, in_channels: int) -> None:
        super().__init__()
        self.branch0_0 = BasicConv2d(in_channels, 256, kernel_size=1, stride=1, padding=0)
        self.branch0_1 = BasicConv2d(256, 384, kernel_size=3, stride=2, padding=0)
        
        self.branch1_0 = BasicConv2d(in_channels, 256, kernel_size=1, stride=1, padding=0)
        self.branch1_1 = BasicConv2d(256, 288, kernel_size=3, stride=2, padding=0)
        
        self.branch2_0 = BasicConv2d(in_channels, 256, kernel_size=1, stride=1, padding=0)
        self.branch2_1 = BasicConv2d(256, 288, kernel_size=3, stride=1, padding=1)
        self.branch2_2 = BasicConv2d(288, 320, kernel_size=3, stride=2, padding=0)
        
        self.branch3 = nn.MaxPool2d(kernel_size=3, stride=2, padding=0)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x0 = self.branch0_0(x)
        x0 = self.branch0_1(x0)
        
        x1 = self.branch1_0(x)
        x1 = self.branch1_1(x1)
        
        x2 = self.branch2_0(x)
        x2 = self.branch2_1(x2)
        x2 = self.branch2_2(x2)
        
        x3 = self.branch3(x)
        
        return torch.cat([x0, x1, x2, x3], dim=1)


class InceptionResNetV1(nn.Module):
    """Inception-ResNet-v1 model"""
    def __init__(self, num_classes: int = 1000, dropout_prob: float = 0.2) -> None:
        super().__init__()
        # Stem
        self.stem = Stem()
        
        # Inception-ResNet-A
        self.mixed_5a = nn.Sequential(*[InceptionResnetA(256, scale=0.17) for _ in range(5)])
        
        # Reduction-A
        self.mixed_6a = ReductionA(256, 192, 192, 256, 384)
        
        # Inception-ResNet-B
        self.mixed_6b = nn.Sequential(*[InceptionResnetB(896, scale=0.10) for _ in range(10)])
        
        # Reduction-B
        self.mixed_7a = ReductionB(896)
        
        # Inception-ResNet-C
        self.mixed_8a = nn.Sequential(*[InceptionResnetC(1792, scale=0.20) for _ in range(5)])
        
        # Classification block
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(1792, num_classes)
        
        # Initialize weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Stem
        x = self.stem(x)
        
        # Inception-ResNet-A and Reduction-A
        x = self.mixed_5a(x)
        x = self.mixed_6a(x)
        
        # Inception-ResNet-B and Reduction-B
        x = self.mixed_6b(x)
        x = self.mixed_7a(x)
        
        # Inception-ResNet-C
        x = self.mixed_8a(x)
        
        # Classification block
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


class InceptionResNetV2(nn.Module):
    """Inception-ResNet-v2 model"""
    def __init__(self, num_classes: int = 1000, dropout_prob: float = 0.2) -> None:
        super().__init__()
        # Stem
        self.stem = Stem()
        
        # Inception-ResNet-A
        self.mixed_5a = nn.Sequential(*[InceptionResnetA(256, scale=0.17) for _ in range(10)])
        
        # Reduction-A
        self.mixed_6a = ReductionA(256, 256, 256, 384, 384)
        
        # Inception-ResNet-B
        self.mixed_6b = nn.Sequential(*[InceptionResnetB(896, scale=0.10) for _ in range(20)])
        
        # Reduction-B
        self.mixed_7a = ReductionB(896)
        
        # Inception-ResNet-C
        self.mixed_8a = nn.Sequential(*[
            InceptionResnetC(1792, scale=0.20, activation=True) for _ in range(9)
        ])
        # Last block doesn't have activation
        self.mixed_8b = InceptionResnetC(1792, scale=0.20, activation=False)
        
        # Classification block
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(1792, num_classes)
        
        # Initialize weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Stem
        x = self.stem(x)
        
        # Inception-ResNet-A and Reduction-A
        x = self.mixed_5a(x)
        x = self.mixed_6a(x)
        
        # Inception-ResNet-B and Reduction-B
        x = self.mixed_6b(x)
        x = self.mixed_7a(x)
        
        # Inception-ResNet-C
        x = self.mixed_8a(x)
        x = self.mixed_8b(x)
        
        # Classification block
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        
        return x


def inception_resnet_v1(num_classes: int = 1000, pretrained: bool = False) -> InceptionResNetV1:
    """Inception-ResNet-v1 model"""
    model = InceptionResNetV1(num_classes=num_classes)
    if pretrained:
        # Pretrained weights are not officially available
        pass
    return model


def inception_resnet_v2(num_classes: int = 1000, pretrained: bool = False) -> InceptionResNetV2:
    """Inception-ResNet-v2 model"""
    model = InceptionResNetV2(num_classes=num_classes)
    if pretrained:
        # Pretrained weights are not officially available
        pass
    return model
