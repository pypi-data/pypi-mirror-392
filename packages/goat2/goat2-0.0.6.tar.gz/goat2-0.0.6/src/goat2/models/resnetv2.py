"""
ResNet V2 (pre-activation) implementations based on "Identity Mappings in Deep Residual Networks"
https://arxiv.org/abs/1603.05027
"""

import torch
import torch.nn as nn
from typing import Type, Union, List, Optional, Callable


class BasicBlockV2(nn.Module):
    """Pre-activation version of the BasicBlock."""
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
            
        # Pre-activation layers
        self.bn1 = norm_layer(in_channels)
        self.relu = nn.ReLU(inplace=True)
        
        # Convolution layers
        self.conv1 = nn.Conv2d(
            in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn2 = norm_layer(out_channels)
        self.conv2 = nn.Conv2d(
            out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False
        )
        
        # Shortcut connection
        self.downsample = downsample
        self.stride = stride
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x
        
        # Pre-activation
        out = self.bn1(x)
        out = self.relu(out)
        
        # Shortcut should be applied to pre-activated input
        if self.downsample is not None:
            identity = self.downsample(out)
            
        # First convolution block
        out = self.conv1(out)
        
        # Second pre-activation and convolution
        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv2(out)
        
        # Residual connection
        out += identity
        
        return out


class BottleneckV2(nn.Module):
    """Pre-activation version of the Bottleneck block."""
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
        
        # Pre-activation layers
        self.bn1 = norm_layer(in_channels)
        self.relu = nn.ReLU(inplace=True)
        
        # Convolution layers
        self.conv1 = nn.Conv2d(in_channels, width, kernel_size=1, bias=False)
        self.bn2 = norm_layer(width)
        self.conv2 = nn.Conv2d(
            width, width, kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn3 = norm_layer(width)
        self.conv3 = nn.Conv2d(
            width, out_channels * self.expansion, kernel_size=1, bias=False
        )
        
        # Shortcut connection
        self.downsample = downsample
        self.stride = stride
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        identity = x
        
        # Pre-activation
        out = self.bn1(x)
        out = self.relu(out)
        
        # Shortcut should be applied to pre-activated input
        if self.downsample is not None:
            identity = self.downsample(out)
            
        # First convolution block
        out = self.conv1(out)
        
        # Second convolution block
        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv2(out)
        
        # Third convolution block
        out = self.bn3(out)
        out = self.relu(out)
        out = self.conv3(out)
        
        # Residual connection
        out += identity
        
        return out


class ResNetV2(nn.Module):
    """
    ResNet V2 Model (pre-activation)
    """
    def __init__(
        self,
        block: Type[Union[BasicBlockV2, BottleneckV2]],
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
        
        # First layer is a standard convolution, no pre-activation
        self.conv1 = nn.Conv2d(3, self.in_channels, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = norm_layer(self.in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        # Create residual layers
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2)
        
        # Final layers
        self.bn_final = norm_layer(512 * block.expansion)
        self.relu_final = nn.ReLU(inplace=True)
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
                if isinstance(m, BottleneckV2):
                    nn.init.constant_(m.bn3.weight, 0)
                elif isinstance(m, BasicBlockV2):
                    nn.init.constant_(m.bn2.weight, 0)
    
    def _make_layer(
        self,
        block: Type[Union[BasicBlockV2, BottleneckV2]],
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
                )
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
        
        # Final activation
        x = self.bn_final(x)
        x = self.relu_final(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x


def resnetv2_18(num_classes: int = 1000, pretrained: bool = False) -> ResNetV2:
    """ResNet V2-18 model"""
    model = ResNetV2(BasicBlockV2, [2, 2, 2, 2], num_classes=num_classes)
    if pretrained:
        # Pretrained weights not available for V2 variants, would need custom implementation
        pass
    return model


def resnetv2_34(num_classes: int = 1000, pretrained: bool = False) -> ResNetV2:
    """ResNet V2-34 model"""
    model = ResNetV2(BasicBlockV2, [3, 4, 6, 3], num_classes=num_classes)
    if pretrained:
        pass
    return model


def resnetv2_50(num_classes: int = 1000, pretrained: bool = False) -> ResNetV2:
    """ResNet V2-50 model"""
    model = ResNetV2(BottleneckV2, [3, 4, 6, 3], num_classes=num_classes)
    if pretrained:
        pass
    return model


def resnetv2_101(num_classes: int = 1000, pretrained: bool = False) -> ResNetV2:
    """ResNet V2-101 model"""
    model = ResNetV2(BottleneckV2, [3, 4, 23, 3], num_classes=num_classes)
    if pretrained:
        pass
    return model


def resnetv2_152(num_classes: int = 1000, pretrained: bool = False) -> ResNetV2:
    """ResNet V2-152 model"""
    model = ResNetV2(BottleneckV2, [3, 8, 36, 3], num_classes=num_classes)
    if pretrained:
        pass
    return model
