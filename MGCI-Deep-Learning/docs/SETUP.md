# Setup Guide

This guide provides detailed instructions for setting up the MGCI Deep Learning framework.

## Prerequisites

### Required Accounts

1. **Google Account** — For Google Colab and Google Drive
2. **Google Earth Engine Account** — For satellite data access
   - Sign up at: https://earthengine.google.com/signup/
   - Approval may take 24-48 hours

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16+ GB |
| GPU | Not required (but slow) | NVIDIA GPU with 8+ GB VRAM |
| Storage | 10 GB | 50+ GB (depends on region size) |

**Note:** Google Colab provides free GPU access, which is sufficient for this project.

## Setup Options

### Option A: Google Colab (Recommended)

This is the easiest way to run the notebooks with GPU support.

#### Step 1: Open Notebooks in Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click `File` → `Upload notebook`
3. Upload the notebooks from `notebooks/` directory

Or use the direct links:
- [Notebook 1: Data Export](https://colab.research.google.com/github/YOUR_USERNAME/MGCI-Deep-Learning/blob/main/notebooks/MGCI_1_DataExport.ipynb)
- [Notebook 2: Training](https://colab.research.google.com/github/YOUR_USERNAME/MGCI-Deep-Learning/blob/main/notebooks/MGCI_2_Training.ipynb)
- [Notebook 3: Inference](https://colab.research.google.com/github/YOUR_USERNAME/MGCI-Deep-Learning/blob/main/notebooks/MGCI_3_Inference.ipynb)

#### Step 2: Enable GPU (for Notebooks 2 & 3)

1. Click `Runtime` → `Change runtime type`
2. Select `GPU` under Hardware accelerator
3. Click `Save`

#### Step 3: Mount Google Drive

The notebooks will prompt you to mount Google Drive. Click the authorization link and follow the instructions.

```python
from google.colab import drive
drive.mount('/content/drive')
```

### Option B: Local Installation

For running on your own machine with a GPU.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MGCI-Deep-Learning.git
cd MGCI-Deep-Learning
```

#### Step 2: Create Virtual Environment

```bash
# Using conda (recommended)
conda create -n mgci python=3.10
conda activate mgci

# Or using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### Step 3: Install PyTorch with CUDA

```bash
# Check your CUDA version first
nvidia-smi

# Install PyTorch (adjust CUDA version as needed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### Step 4: Install Other Dependencies

```bash
pip install -r requirements.txt
```

#### Step 5: Authenticate Google Earth Engine

```bash
earthengine authenticate
```

This will open a browser window. Log in with your GEE-registered Google account.

## Google Earth Engine Setup

### First-Time Authentication

When running Notebook 1 for the first time:

```python
import ee

# Trigger authentication flow
ee.Authenticate()

# Initialize with your project
ee.Initialize(project='your-project-id')
```

### Creating a GEE Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Earth Engine API:
   - Go to `APIs & Services` → `Enable APIs and Services`
   - Search for "Earth Engine API"
   - Click `Enable`

### Common Authentication Issues

| Issue | Solution |
|-------|----------|
| "Please sign up for Earth Engine" | Register at https://earthengine.google.com/signup/ |
| "Invalid project" | Create a Cloud project and enable Earth Engine API |
| Token expired | Re-run `ee.Authenticate()` |

## Directory Structure

After setup, your Google Drive should have:

```
My Drive/
└── MGCI_YOUR_REGION_YEAR/
    ├── *.tif                    # Exported patches
    ├── model_best.pth           # Trained model (after Notebook 2)
    ├── training_summary.json    # Training results
    └── mgci_results.json        # Final MGCI results
```

## Verification

### Verify PyTorch Installation

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Verify Earth Engine

```python
import ee
ee.Initialize()
print(ee.Image("NASA/NASADEM_HGT/001").bandNames().getInfo())
```

### Verify Segmentation Models

```python
import segmentation_models_pytorch as smp
model = smp.Unet(encoder_name='resnet50', in_channels=6, classes=1)
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
```

## Next Steps

Once setup is complete:

1. Read [DATA_PREPARATION.md](DATA_PREPARATION.md) to prepare data for your region
2. Run the notebooks in order (1 → 2 → 3)
3. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues

## Getting Help

- **GitHub Issues**: Report bugs or ask questions
- **Google Earth Engine Forum**: For GEE-specific questions
- **PyTorch Forums**: For deep learning questions
