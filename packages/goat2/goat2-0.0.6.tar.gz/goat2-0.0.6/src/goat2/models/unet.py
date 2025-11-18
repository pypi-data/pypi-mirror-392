"""
UNet implementation based on "U-Net: Convolutional Networks for Biomedical Image Segmentation"
https://arxiv.org/abs/1505.04597
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Union, Dict


class DoubleConv(nn.Module):
    """Double convolution block: conv -> bn -> relu -> conv -> bn -> relu"""
    
    def __init__(
        self, 
        in_channels: int, 
        out_channels: int, 
        mid_channels: Optional[int] = None,
        kernel_size: int = 3,
        padding: int = 1,
        bias: bool = False
    ) -> None:
        super().__init__()
        if mid_channels is None:
            mid_channels = out_channels
            
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=kernel_size, padding=padding, bias=bias),
            nn.BatchNorm2d(mid_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_channels, out_channels, kernel_size=kernel_size, padding=padding, bias=bias),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x)


class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    
    def __init__(
        self, 
        in_channels: int, 
        out_channels: int, 
        pooling_size: int = 2
    ) -> None:
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(pooling_size),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.maxpool_conv(x)


class Up(nn.Module):
    """Upscaling then double conv"""
    
    def __init__(
        self, 
        in_channels: int, 
        out_channels: int, 
        bilinear: bool = True
    ) -> None:
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        x1 = self.up(x1)
        
        # Adjust dimensions if needed
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        
        # Concatenate along the channel dimension
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class OutConv(nn.Module):
    """Final 1x1 convolution layer"""
    
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class UNet(nn.Module):
    """UNet architecture for image segmentation tasks"""
    
    def __init__(
        self, 
        in_channels: int = 3, 
        out_channels: int = 1,
        depth: int = 5,
        base_features: int = 64, 
        bilinear: bool = True,
        features: Optional[List[int]] = None
    ) -> None:
        """
        Args:
            in_channels: Number of input channels (e.g., 3 for RGB)
            out_channels: Number of output channels (e.g., 1 for binary segmentation)
            depth: Depth of the UNet (number of down/up operations)
            base_features: Number of features in the first layer
            bilinear: Whether to use bilinear upsampling (True) or transposed convolutions (False)
            features: List of feature dimensions for each layer (if None, generated based on depth and base_features)
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.bilinear = bilinear
        
        # Generate feature dimensions for each level if not provided
        if features is None:
            features = [base_features * (2 ** i) for i in range(depth)]
        
        # Initial double convolution
        self.inc = DoubleConv(in_channels, features[0])
        
        # Downsampling path
        self.downs = nn.ModuleList()
        for i in range(len(features) - 1):
            self.downs.append(Down(features[i], features[i + 1]))
        
        # Upsampling path
        self.ups = nn.ModuleList()
        for i in reversed(range(1, len(features))):
            in_feat = features[i]
            out_feat = features[i - 1]
            self.ups.append(Up(in_feat, out_feat, bilinear))
        
        # Final convolution
        self.outc = OutConv(features[0], out_channels)
        
        # Initialize weights
        self._init_weights()
        
    def _init_weights(self) -> None:
        """Initialize model weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Initial feature extraction
        x1 = self.inc(x)
        
        # Contracting path with skip connections
        skip_connections = [x1]
        for down in self.downs:
            x = down(skip_connections[-1])
            skip_connections.append(x)
        
        # Remove the last feature map (bottom of the U)
        x = skip_connections.pop()
        
        # Expansive path
        for up in self.ups:
            skip = skip_connections.pop()
            x = up(x, skip)
            
        # Final convolution
        return self.outc(x)

def train_unet(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    val_loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    num_epochs: int = 100,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    early_stopping_patience: Optional[int] = None,
    save_path: Optional[str] = None,
) -> Dict[str, List[float]]:
    """
    Train the UNet model with validation
    
    Args:
        model: The UNet model to train
        train_loader: DataLoader for training data
        val_loader: DataLoader for validation data
        criterion: Loss function
        optimizer: Optimizer for training
        device: Device to train on (cuda/cpu)
        num_epochs: Number of epochs to train
        scheduler: Learning rate scheduler (optional)
        early_stopping_patience: Number of epochs to wait before early stopping (optional)
        save_path: Path to save the best model (optional)
        
    Returns:
        Dictionary containing training history
    """
    model.to(device)
    history = {
        'train_loss': [],
        'val_loss': [],
        'best_val_loss': float('inf'),
        'best_epoch': 0
    }
    
    no_improve_count = 0
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        for images, masks in train_loader:
            images, masks = images.to(device), masks.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, masks)
            
            # Backward pass and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * images.size(0)
        
        train_loss /= len(train_loader.dataset)
        history['train_loss'].append(train_loss)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, masks in val_loader:
                images, masks = images.to(device), masks.to(device)
                outputs = model(images)
                loss = criterion(outputs, masks)
                val_loss += loss.item() * images.size(0)
                
        val_loss /= len(val_loader.dataset)
        history['val_loss'].append(val_loss)
        
        # Print progress
        print(f'Epoch {epoch+1}/{num_epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}')
        
        # Learning rate scheduling
        if scheduler is not None:
            scheduler.step(val_loss)
            
        # Save best model
        if val_loss < history['best_val_loss']:
            history['best_val_loss'] = val_loss
            history['best_epoch'] = epoch
            no_improve_count = 0
            
            if save_path:
                torch.save(model.state_dict(), save_path)
                print(f"Model saved to {save_path}")
        else:
            no_improve_count += 1
        
        # Early stopping
        if early_stopping_patience and no_improve_count >= early_stopping_patience:
            print(f"Early stopping at epoch {epoch+1}")
            break
    
    return history


# Example usage
if __name__ == "__main__":
    import torch.optim as optim
    from torch.utils.data import DataLoader, random_split
    from torchvision import transforms
    from torchvision.datasets import ImageFolder
    
    # Define device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Create the UNet model
    model = UNet(
        in_channels=3,        # RGB images
        out_channels=1,       # Binary segmentation
        depth=4,              # 4 down/up operations
        base_features=64,     # Start with 64 features
        bilinear=True         # Use bilinear upsampling
    )
    
    # Example dataset and transforms (replace with your actual dataset)
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Define loss function and optimizer
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)
    
    # Example code for dataset preparation (customize for your data)
    """
    # Load and split dataset
    dataset = YourDataset(root_dir='path/to/data', transform=transform)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False, num_workers=4)
    
    # Train the model
    history = train_unet(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        device=device,
        num_epochs=100,
        scheduler=scheduler,
        early_stopping_patience=10,
        save_path='best_unet_model.pth'
    )
    
    # Load best model for inference
    model.load_state_dict(torch.load('best_unet_model.pth'))
    model.eval()
    
    # Example inference
    with torch.no_grad():
        image = next(iter(val_loader))[0][0:1].to(device)  # Get a single image
        prediction = torch.sigmoid(model(image)) > 0.5     # Apply sigmoid and threshold
        # Save or visualize the prediction
    """
