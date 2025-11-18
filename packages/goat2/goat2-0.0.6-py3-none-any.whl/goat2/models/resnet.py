"""
ResNet implementations based on "Deep Residual Learning for Image Recognition"
https://arxiv.org/abs/1512.03385
"""

import torch
import torch.nn as nn
from typing import Type, Union, List, Optional, Callable


class BasicBlock(nn.Module):
    expansion = 1
    
    def __init__(
        self, 
        in_channels: int, 
        out_channels: int, 
        stride: int = 1, 
        downsample: Optional[nn.Module] = None,
        norm_layer: Optional[Callable[..., nn.Module]] = None
    ) -> None:
        super().__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
            
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = norm_layer(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = norm_layer(out_channels)
        self.downsample = downsample
        self.stride = stride
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        if self.downsample is not None:
            identity = self.downsample(x)
            
        out += identity
        out = self.relu(out)
        
        return out


class Bottleneck(nn.Module):
    expansion = 4
    
    def __init__(
        self, 
        in_channels: int, 
        out_channels: int, 
        stride: int = 1, 
        downsample: Optional[nn.Module] = None,
        norm_layer: Optional[Callable[..., nn.Module]] = None
    ) -> None:
        super().__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
            
        width = out_channels  # No bottleneck width reduction by default
        
        self.conv1 = nn.Conv2d(in_channels, width, kernel_size=1, bias=False)
        self.bn1 = norm_layer(width)
        self.conv2 = nn.Conv2d(width, width, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = norm_layer(width)
        self.conv3 = nn.Conv2d(width, out_channels * self.expansion, kernel_size=1, bias=False)
        self.bn3 = norm_layer(out_channels * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        
        out = self.conv3(out)
        out = self.bn3(out)
        
        if self.downsample is not None:
            identity = self.downsample(x)
            
        out += identity
        out = self.relu(out)
        
        return out


class ResNet(nn.Module):
    def __init__(
        self,
        block: Type[Union[BasicBlock, Bottleneck]],
        layers: List[int],
        num_classes: int = 1000,
        zero_init_residual: bool = False,
        norm_layer: Optional[Callable[..., nn.Module]] = None
    ) -> None:
        super().__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        self._norm_layer = norm_layer
        
        self.in_channels = 64
        self.conv1 = nn.Conv2d(3, self.in_channels, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = norm_layer(self.in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)
        
        # Initialize weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
        
        # Zero-initialize the last BN in each residual branch
        if zero_init_residual:
            for m in self.modules():
                if isinstance(m, Bottleneck):
                    nn.init.constant_(m.bn3.weight, 0)
                elif isinstance(m, BasicBlock):
                    nn.init.constant_(m.bn2.weight, 0)
    
    def _make_layer(
        self,
        block: Type[Union[BasicBlock, Bottleneck]],
        out_channels: int,
        blocks: int,
        stride: int = 1
    ) -> nn.Sequential:
        norm_layer = self._norm_layer
        downsample = None
        
        if stride != 1 or self.in_channels != out_channels * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.in_channels, 
                    out_channels * block.expansion, 
                    kernel_size=1, 
                    stride=stride, 
                    bias=False
                ),
                norm_layer(out_channels * block.expansion),
            )
            
        layers = []
        layers.append(block(self.in_channels, out_channels, stride, downsample, norm_layer))
        self.in_channels = out_channels * block.expansion
        
        for _ in range(1, blocks):
            layers.append(block(self.in_channels, out_channels, norm_layer=norm_layer))
            
        return nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x


def resnet18(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNet-18 model"""
    model = ResNet(BasicBlock, [2, 2, 2, 2], num_classes=num_classes)
    if pretrained:
        # Load pretrained weights if available
        state_dict = torch.hub.load_state_dict_from_url(
            "https://download.pytorch.org/models/resnet18-f37072fd.pth",
            progress=True
        )
        model.load_state_dict(state_dict)
    return model


def resnet34(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNet-34 model"""
    model = ResNet(BasicBlock, [3, 4, 6, 3], num_classes=num_classes)
    if pretrained:
        state_dict = torch.hub.load_state_dict_from_url(
            "https://download.pytorch.org/models/resnet34-b627a593.pth",
            progress=True
        )
        model.load_state_dict(state_dict)
    return model


def resnet50(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNet-50 model"""
    model = ResNet(Bottleneck, [3, 4, 6, 3], num_classes=num_classes)
    if pretrained:
        state_dict = torch.hub.load_state_dict_from_url(
            "https://download.pytorch.org/models/resnet50-11ad3fa6.pth",
            progress=True
        )
        model.load_state_dict(state_dict)
    return model


def resnet101(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNet-101 model"""
    model = ResNet(Bottleneck, [3, 4, 23, 3], num_classes=num_classes)
    if pretrained:
        state_dict = torch.hub.load_state_dict_from_url(
            "https://download.pytorch.org/models/resnet101-cd907fc2.pth",
            progress=True
        )
        model.load_state_dict(state_dict)
    return model


def resnet152(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNet-152 model"""
    model = ResNet(Bottleneck, [3, 8, 36, 3], num_classes=num_classes)
    if pretrained:
        state_dict = torch.hub.load_state_dict_from_url(
            "https://download.pytorch.org/models/resnet152-f82ba261.pth",
            progress=True
        )
        model.load_state_dict(state_dict)
    return model


def resnext50_32x4d(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNeXt-50 32x4d model"""
    raise NotImplementedError("ResNeXt models not included in this implementation")


def resnext101_32x8d(num_classes: int = 1000, pretrained: bool = False) -> ResNet:
    """ResNeXt-101 32x8d model"""
    raise NotImplementedError("ResNeXt models not included in this implementation")
