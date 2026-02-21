# Pre-trained Model Weights

This directory contains instructions for downloading the pre-trained model weights.

## Model Information

| Property | Value |
|----------|-------|
| Architecture | U-Net + ResNet-50 |
| Input Channels | 6 (Blue, Green, Red, NIR, Elevation, Slope) |
| Output | Binary vegetation mask |
| Training Region | Jazan, Saudi Arabia |
| Training Patches | 878 |
| Best Epoch | 68 |
| Validation IoU | 0.8475 |
| Test Dice | 0.9263 |
| File Size | ~125 MB |

## Download option

### Google Drive

Download the pre-trained weights from Google Drive:

📥 **[Download model_best.pth](https://drive.google.com/file/d/1FXqu42tDVVubW_Tr5jFTkpp3X6fagTXN/view?usp=drivesdk)**

After downloading, place the file in your Google Drive or local directory and update the path in Notebook 3:

```python
Config.MODEL_PATH = '/path/to/model_best.pth'
```


## Checkpoint Contents

The saved checkpoint (`model_best.pth`) contains:

```python
{
    'epoch': 67,                    # Best epoch (0-indexed)
    'model_state_dict': {...},      # Model weights
    'optimizer_state_dict': {...},  # Optimizer state
    'val_loss': 0.0585,             # Validation loss
    'val_iou': 0.8475,              # Validation IoU
    'means': [...],                 # Normalization means (6 values)
    'stds': [...]                   # Normalization stds (6 values)
}
```

## Loading the Model

```python
import torch
import segmentation_models_pytorch as smp

# Load checkpoint
checkpoint = torch.load('model_best.pth', map_location='cuda', weights_only=False)

# Get normalization statistics
MEANS = checkpoint['means']
STDS = checkpoint['stds']

# Create model
model = smp.Unet(
    encoder_name='resnet50',
    encoder_weights=None,  # We'll load our own weights
    in_channels=6,
    classes=1,
    activation=None
)

# Load weights
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(f"Model loaded from epoch {checkpoint['epoch']+1}")
print(f"Validation IoU: {checkpoint['val_iou']:.4f}")
```

## Transfer Learning

If you want to fine-tune the model for your region:

```python
# Load pre-trained weights
model.load_state_dict(checkpoint['model_state_dict'])

# Optionally freeze encoder
for param in model.encoder.parameters():
    param.requires_grad = False

# Train with lower learning rate
optimizer = torch.optim.AdamW(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=1e-5  # Lower than initial training
)
```

## Normalization Statistics

The model was trained with the following normalization (computed from Jazan training data):

| Band | Mean | Std |
|------|------|-----|
| Blue | 902.17 | 359.13 |
| Green | 1267.60 | 482.97 |
| Red | 1530.71 | 611.29 |
| NIR | 2268.74 | 792.12 |
| Elevation | 710.20 | 489.45 |
| Slope | 19.79 | 13.22 |

**Note:** These statistics are automatically loaded from the checkpoint. You don't need to specify them manually.

## Expected Input Format

The model expects input tensors with:
- Shape: `[batch, 6, height, width]`
- Channels: Blue, Green, Red, NIR, Elevation (m), Slope (degrees)
- Normalized using the statistics above

## License

The pre-trained weights are released under the same license as this repository (CC BY-NC-ND 4.0). See [LICENSE](../LICENSE) for details.

If you use these weights in your research, please cite the original paper (see [CITATION.cff](../CITATION.cff)).
