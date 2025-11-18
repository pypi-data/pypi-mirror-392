import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data import DataLoader
from torchvision import transforms
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple, List, Optional, Union


class VAE(nn.Module):
    """
    Variational Autoencoder for image generation.
    
    This implementation follows the original VAE paper (Kingma & Welling, 2014)
    with architectural improvements for image processing.
    """
    
    def __init__(
        self, 
        input_shape: Tuple[int, int, int], 
        latent_dim: int = 128,
        hidden_dims: List[int] = None,
        beta: float = 1.0
    ):
        """
        Initialize the VAE model.
        
        Args:
            input_shape: Tuple of (channels, height, width)
            latent_dim: Dimension of the latent space
            hidden_dims: List of hidden dimensions for the encoder/decoder networks
            beta: Weight for the KL divergence term in the loss (β-VAE)
        """
        super().__init__()
        
        self.latent_dim = latent_dim
        self.beta = beta
        self.input_shape = input_shape
        channels, height, width = input_shape
        
        # Default architecture if not specified
        if hidden_dims is None:
            hidden_dims = [32, 64, 128, 256, 512]
            
        # Build Encoder
        modules = []
        in_channels = channels
        
        for h_dim in hidden_dims:
            modules.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, h_dim, kernel_size=3, stride=2, padding=1),
                    nn.BatchNorm2d(h_dim),
                    nn.LeakyReLU()
                )
            )
            in_channels = h_dim
            
        self.encoder = nn.Sequential(*modules)
        
        # Calculate the size of the feature maps before flattening
        self.feature_size = self._get_encoder_output_size(input_shape)
        
        # Projection to latent space
        self.fc_mu = nn.Linear(hidden_dims[-1] * self.feature_size[0] * self.feature_size[1], latent_dim)
        self.fc_var = nn.Linear(hidden_dims[-1] * self.feature_size[0] * self.feature_size[1], latent_dim)
        
        # Build Decoder
        self.decoder_input = nn.Linear(latent_dim, hidden_dims[-1] * self.feature_size[0] * self.feature_size[1])
        
        modules = []
        hidden_dims.reverse()
        
        for i in range(len(hidden_dims) - 1):
            modules.append(
                nn.Sequential(
                    nn.ConvTranspose2d(
                        hidden_dims[i], hidden_dims[i + 1],
                        kernel_size=3, stride=2, padding=1, output_padding=1
                    ),
                    nn.BatchNorm2d(hidden_dims[i + 1]),
                    nn.LeakyReLU()
                )
            )
        
        self.decoder = nn.Sequential(*modules)
        
        # Final layer
        self.final_layer = nn.Sequential(
            nn.ConvTranspose2d(
                hidden_dims[-1], hidden_dims[-1],
                kernel_size=3, stride=2, padding=1, output_padding=1
            ),
            nn.BatchNorm2d(hidden_dims[-1]),
            nn.LeakyReLU(),
            nn.Conv2d(hidden_dims[-1], channels, kernel_size=3, padding=1),
            nn.Sigmoid()  # For images in [0, 1] range
        )
        
    def _get_encoder_output_size(self, input_shape: Tuple[int, int, int]) -> Tuple[int, int]:
        """Calculate the size of the encoder output feature maps."""
        x = torch.zeros(1, *input_shape)
        for module in self.encoder:
            x = module(x)
        return x.shape[2], x.shape[3]
        
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode input to mean and log-variance in latent space.
        
        Args:
            x: Input tensor [B, C, H, W]
            
        Returns:
            mu: Mean in latent space
            log_var: Log variance in latent space
        """
        x = self.encoder(x)
        x = torch.flatten(x, start_dim=1)
        
        mu = self.fc_mu(x)
        log_var = self.fc_var(x)
        
        return mu, log_var
    
    def reparameterize(self, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        """
        Reparameterization trick to sample from latent space.
        
        Args:
            mu: Mean in latent space
            log_var: Log variance in latent space
            
        Returns:
            z: Sampled point in latent space
        """
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        z = mu + eps * std
        return z
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """
        Decode from latent space to image space.
        
        Args:
            z: Latent vector [B, latent_dim]
            
        Returns:
            Reconstructed image [B, C, H, W]
        """
        z = self.decoder_input(z)
        z = z.view(-1, z.shape[1] // (self.feature_size[0] * self.feature_size[1]), 
                  self.feature_size[0], self.feature_size[1])
        
        z = self.decoder(z)
        z = self.final_layer(z)
        return z
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through the VAE.
        
        Args:
            x: Input tensor [B, C, H, W]
            
        Returns:
            x_recon: Reconstructed input
            mu: Mean in latent space
            log_var: Log variance in latent space
        """
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        x_recon = self.decode(z)
        
        return x_recon, mu, log_var
    
    def loss_function(self, recon_x: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        """
        VAE loss function: reconstruction loss + KL divergence.
        
        Args:
            recon_x: Reconstructed input
            x: Original input
            mu: Mean in latent space
            log_var: Log variance in latent space
            
        Returns:
            total_loss: Combined loss
        """
        # Reconstruction loss
        recon_loss = F.mse_loss(recon_x, x, reduction='sum')
        
        # KL divergence: -0.5 * sum(1 + log(σ^2) - μ^2 - σ^2)
        kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        
        # Total loss with beta weighting for KL term
        total_loss = recon_loss + self.beta * kl_loss
        
        return total_loss


class VAETrainer:
    """Handler for training and using a VAE model."""
    
    def __init__(
        self, 
        model: VAE,
        device: torch.device = None,
        learning_rate: float = 1e-3
    ):
        """
        Initialize the VAE trainer.
        
        Args:
            model: VAE model
            device: Device to use for training (will use CUDA if available if None)
            learning_rate: Learning rate for optimization
        """
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        self.model = model.to(self.device)
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
    def train_epoch(self, dataloader: DataLoader) -> float:
        """
        Train the model for one epoch.
        
        Args:
            dataloader: DataLoader for training data
            
        Returns:
            avg_loss: Average loss for the epoch
        """
        self.model.train()
        total_loss = 0
        
        for batch_idx, (data, _) in enumerate(dataloader):
            data = data.to(self.device)
            
            self.optimizer.zero_grad()
            
            recon_batch, mu, log_var = self.model(data)
            loss = self.model.loss_function(recon_batch, data, mu, log_var)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader.dataset)
        return avg_loss
    
    def train(
        self, 
        train_loader: DataLoader, 
        num_epochs: int, 
        save_path: Optional[str] = None,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None
    ) -> List[float]:
        """
        Train the model for multiple epochs.
        
        Args:
            train_loader: DataLoader for training data
            num_epochs: Number of epochs to train
            save_path: Path to save the final model
            scheduler: Learning rate scheduler
            
        Returns:
            losses: List of losses per epoch
        """
        losses = []
        
        for epoch in range(num_epochs):
            avg_loss = self.train_epoch(train_loader)
            losses.append(avg_loss)
            
            if scheduler is not None:
                scheduler.step()
                
            print(f'Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.6f}')
            
        if save_path:
            torch.save(self.model.state_dict(), save_path)
            print(f"Model saved to {save_path}")
            
        return losses
    
    def generate_samples(self, num_samples: int) -> torch.Tensor:
        """
        Generate samples from the latent space.
        
        Args:
            num_samples: Number of samples to generate
            
        Returns:
            samples: Generated samples [num_samples, C, H, W]
        """
        self.model.eval()
        with torch.no_grad():
            # Sample from normal distribution
            z = torch.randn(num_samples, self.model.latent_dim).to(self.device)
            samples = self.model.decode(z)
        return samples
    
    def reconstruct(self, data: torch.Tensor) -> torch.Tensor:
        """
        Reconstruct data through the VAE.
        
        Args:
            data: Input data [B, C, H, W]
            
        Returns:
            recon: Reconstructed data [B, C, H, W]
        """
        self.model.eval()
        with torch.no_grad():
            data = data.to(self.device)
            recon, _, _ = self.model(data)
        return recon
    
    def interpolate(self, img1: torch.Tensor, img2: torch.Tensor, steps: int = 10) -> List[torch.Tensor]:
        """
        Interpolate between two images in latent space.
        
        Args:
            img1: First image [1, C, H, W]
            img2: Second image [1, C, H, W]
            steps: Number of interpolation steps
            
        Returns:
            interpolations: List of interpolated images
        """
        self.model.eval()
        with torch.no_grad():
            # Encode both images
            img1 = img1.to(self.device)
            img2 = img2.to(self.device)
            
            mu1, log_var1 = self.model.encode(img1)
            mu2, log_var2 = self.model.encode(img2)
            
            # Interpolate in the latent space
            interpolations = []
            for alpha in np.linspace(0, 1, steps):
                mu_interp = mu1 * (1 - alpha) + mu2 * alpha
                interp_img = self.model.decode(mu_interp)
                interpolations.append(interp_img.cpu())
                
        return interpolations


def visualize_vae(
    original_images: torch.Tensor, 
    reconstructed_images: torch.Tensor,
    generated_images: Optional[torch.Tensor] = None,
    figsize: Tuple[int, int] = (12, 6)
):
    """
    Visualize original, reconstructed, and generated images.
    
    Args:
        original_images: Original images tensor [B, C, H, W]
        reconstructed_images: Reconstructed images tensor [B, C, H, W]
        generated_images: Generated images tensor [B, C, H, W]
        figsize: Figure size (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Number of images to show
    n = min(5, original_images.size(0))
    
    if generated_images is not None:
        rows = 3
    else:
        rows = 2
        
    # Plot original images
    for i in range(n):
        plt.subplot(rows, n, i + 1)
        img = original_images[i].cpu().permute(1, 2, 0).numpy()
        if img.shape[2] == 1:  # Grayscale
            img = img.squeeze()
            plt.imshow(img, cmap='gray')
        else:
            plt.imshow(img)
        plt.title("Original")
        plt.axis('off')
    
    # Plot reconstructed images
    for i in range(n):
        plt.subplot(rows, n, n + i + 1)
        img = reconstructed_images[i].cpu().permute(1, 2, 0).numpy()
        if img.shape[2] == 1:  # Grayscale
            img = img.squeeze()
            plt.imshow(img, cmap='gray')
        else:
            plt.imshow(img)
        plt.title("Reconstructed")
        plt.axis('off')
        
    # Plot generated images if provided
    if generated_images is not None:
        for i in range(n):
            plt.subplot(rows, n, 2*n + i + 1)
            img = generated_images[i].cpu().permute(1, 2, 0).numpy()
            if img.shape[2] == 1:  # Grayscale
                img = img.squeeze()
                plt.imshow(img, cmap='gray')
            else:
                plt.imshow(img)
            plt.title("Generated")
            plt.axis('off')
    
    plt.tight_layout()
    plt.show()


def example_usage():
    """An example of how to use the VAE implementation."""
    # Define hyperparameters
    batch_size = 128
    latent_dim = 32
    num_epochs = 20
    learning_rate = 1e-3
    
    # Set up dataset (using MNIST as an example)
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    
    train_dataset = torchvision.datasets.MNIST(
        root='./data', 
        train=True, 
        transform=transform, 
        download=True
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4
    )
    
    # Create model (for MNIST: 1 channel, 28x28 images)
    model = VAE(
        input_shape=(1, 28, 28),
        latent_dim=latent_dim,
        hidden_dims=[32, 64, 128],
        beta=1.0
    )
    
    # Create trainer
    trainer = VAETrainer(model, learning_rate=learning_rate)
    
    # Train model
    losses = trainer.train(train_loader, num_epochs)
    
    # Plot loss curve
    plt.figure(figsize=(10, 5))
    plt.plot(losses)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training Loss')
    plt.grid(True)
    plt.show()
    
    # Visualize results
    # Get a batch of test images
    test_dataset = torchvision.datasets.MNIST(
        root='./data', 
        train=False, 
        transform=transform
    )
    test_loader = DataLoader(test_dataset, batch_size=5, shuffle=True)
    test_images, _ = next(iter(test_loader))
    
    # Reconstruct images
    reconstructed = trainer.reconstruct(test_images)
    
    # Generate random samples
    generated = trainer.generate_samples(5)
    
    # Visualize
    visualize_vae(test_images, reconstructed, generated)