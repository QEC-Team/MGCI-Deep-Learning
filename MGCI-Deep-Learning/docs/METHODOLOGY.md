# Methodology

This document describes the technical methodology used in the MGCI Deep Learning framework.

## 1. Mountain Green Cover Index (MGCI)

### SDG Indicator 15.4.2

The Mountain Green Cover Index (MGCI) is the official indicator for monitoring progress toward **UN Sustainable Development Goal Target 15.4**:

> "By 2030, ensure the conservation of mountain ecosystems, including their biodiversity, in order to enhance their capacity to provide benefits that are essential for sustainable development."

### MGCI Formula

$$\text{MGCI} = \frac{\text{Green Cover in Mountain Area}}{\text{Total Mountain Area}} \times 100\%$$

Where:
- **Green Cover**: Vegetated land (forests, shrubs, grasslands, croplands)
- **Mountain Area**: Land above 300m elevation (Kapos classification)

### Kapos Mountain Classification

The framework uses the Kapos et al. (2000) classification system:

| Class | Elevation | Local Elevation Range | Name |
|-------|-----------|----------------------|------|
| 6 | 300–1,000 m | AND LER > 300m within 7km | Foothills |
| 5 | 1,000–1,500 m | OR slope > 5° | Lower Montane |
| 4 | 1,500–2,500 m | — | Montane |
| 3 | 2,500–3,500 m | — | Upper Montane |
| 2 | 3,500–4,500 m | — | Alpine |
| 1 | > 4,500 m | — | Nival |

**Note:** This implementation uses a simplified threshold of 300m elevation.

## 2. Data Sources

### Sentinel-2 Multispectral Imagery

| Property | Value |
|----------|-------|
| Satellite | Sentinel-2A/B |
| Product | Level-2A (Surface Reflectance) |
| Resolution | 10m (bands used) |
| Revisit Time | 5 days |
| Bands Used | B2 (Blue), B3 (Green), B4 (Red), B8 (NIR) |

### Copernicus GLO-30 DEM

| Property | Value |
|----------|-------|
| Source | Copernicus Programme |
| Resolution | 30m (resampled to 10m) |
| Vertical Accuracy | < 4m (RMSE) |
| Coverage | Global (80°N to 80°S) |

### Derived Products

| Product | Derivation | Purpose |
|---------|------------|---------|
| Slope | `arctan(gradient(DEM))` | Surface area correction |
| NDVI | `(NIR - Red) / (NIR + Red)` | Vegetation detection |
| VegLabel | `NDVI > 0.3` | Training labels |

## 3. Deep Learning Architecture

### U-Net with ResNet-50 Encoder

The model uses the U-Net architecture with a pre-trained ResNet-50 encoder:

```
Input (6 channels)
    │
    ▼
┌─────────────────────────────────────┐
│         ResNet-50 Encoder           │
│  (ImageNet pre-trained, modified    │
│   first conv for 6 channels)        │
├─────────────────────────────────────┤
│  Conv1: 64 filters                  │
│  Stage 1: 256 filters (3 blocks)    │
│  Stage 2: 512 filters (4 blocks)    │
│  Stage 3: 1024 filters (6 blocks)   │
│  Stage 4: 2048 filters (3 blocks)   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│          U-Net Decoder              │
├─────────────────────────────────────┤
│  Decoder 1: 256 filters + skip      │
│  Decoder 2: 128 filters + skip      │
│  Decoder 3: 64 filters + skip       │
│  Decoder 4: 32 filters + skip       │
│  Final: 1 channel (sigmoid)         │
└─────────────────────────────────────┘
    │
    ▼
Output (1 channel, vegetation prob.)
```

### Why U-Net?

1. **Skip Connections**: Preserve spatial details
2. **Encoder-Decoder**: Capture multi-scale features
3. **Pre-trained Encoder**: Leverage ImageNet features
4. **Proven Architecture**: State-of-the-art for segmentation

### Input Channels

| Channel | Source | Normalization |
|---------|--------|---------------|
| 0: Blue | Sentinel-2 B2 | Standardized (mean/std) |
| 1: Green | Sentinel-2 B3 | Standardized |
| 2: Red | Sentinel-2 B4 | Standardized |
| 3: NIR | Sentinel-2 B8 | Standardized |
| 4: Elevation | Copernicus DEM | Standardized |
| 5: Slope | Derived | Standardized |

## 4. Loss Function

### Combined Focal + Dice Loss

$$\mathcal{L} = 0.5 \times \mathcal{L}_{Focal} + 0.5 \times \mathcal{L}_{Dice}$$

### Focal Loss

Addresses class imbalance by down-weighting easy examples:

$$\mathcal{L}_{Focal} = -\alpha (1 - p_t)^\gamma \log(p_t)$$

Where:
- $\alpha = 0.25$ (balancing factor)
- $\gamma = 2.0$ (focusing parameter)
- $p_t$ = model confidence for true class

### Dice Loss

Directly optimizes spatial overlap:

$$\mathcal{L}_{Dice} = 1 - \frac{2|P \cap G| + \epsilon}{|P| + |G| + \epsilon}$$

Where:
- $P$ = predicted pixels
- $G$ = ground truth pixels
- $\epsilon$ = smoothing term (1.0)

## 5. Training Strategy

### Data Split

Spatial split to prevent data leakage:

```
Sorted by Longitude (West → East)
├── Train (70%): Western patches
├── Val (15%): Middle patches
└── Test (15%): Eastern patches
```

### Data Augmentation

| Augmentation | Parameters | Purpose |
|--------------|------------|---------|
| Horizontal Flip | p=0.5 | Spatial invariance |
| Vertical Flip | p=0.5 | Spatial invariance |
| Rotate 90° | p=0.5 | Rotational invariance |
| Shift/Scale/Rotate | shift=0.1, scale=0.15, rotate=45° | Geometric robustness |
| Gaussian Noise | var=(10,50) | Noise robustness |
| Brightness/Contrast | ±0.2 | Radiometric robustness |

### Learning Rate Schedule

Cosine Annealing with Warm Restarts:

$$\eta_t = \eta_{min} + \frac{1}{2}(\eta_{max} - \eta_{min})(1 + \cos(\frac{T_{cur}}{T_i}\pi))$$

Where:
- $T_0 = 10$ epochs (initial period)
- $T_{mult} = 2$ (period multiplier)
- $\eta_{min} = 10^{-6}$

## 6. True Surface Area Calculation

### Why Surface Area Matters

On sloped terrain, the actual surface area is larger than the map (planimetric) area:

```
Flat terrain:        Sloped terrain:
┌──────────┐        ╱╲
│ 100 m²   │       ╱  ╲
└──────────┘      ╱    ╲
                 ╱ 141 m² ╲
                ╱   (45°)   ╲
```

### Surface Area Formula

$$A_{surface} = \frac{A_{planimetric}}{\cos(\theta)}$$

Where $\theta$ is the slope angle in degrees.

### Impact on MGCI

| Slope | Area Correction |
|-------|-----------------|
| 0° | ×1.00 |
| 15° | ×1.04 |
| 30° | ×1.15 |
| 45° | ×1.41 |
| 60° | ×2.00 |

**Note:** Our study found ~13% average correction for Jizan's mountainous terrain.

## 7. Evaluation Metrics

### Per-Pixel Metrics

| Metric | Formula | Range |
|--------|---------|-------|
| Accuracy | $(TP + TN) / (TP + TN + FP + FN)$ | 0–1 |
| Precision | $TP / (TP + FP)$ | 0–1 |
| Recall | $TP / (TP + FN)$ | 0–1 |
| F1 Score | $2 \times (P \times R) / (P + R)$ | 0–1 |

### Spatial Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| IoU (Jaccard) | $\|P \cap G\| / \|P \cup G\|$ | Spatial overlap |
| Dice (F1) | $2\|P \cap G\| / (\|P\| + \|G\|)$ | Similar to IoU, less harsh |

## 8. References

1. Kapos, V., et al. (2000). Developing a map of the world's mountain forests.
2. Ronneberger, O., et al. (2015). U-Net: Convolutional Networks for Biomedical Image Segmentation.
3. He, K., et al. (2016). Deep Residual Learning for Image Recognition.
4. Lin, T.-Y., et al. (2017). Focal Loss for Dense Object Detection.
5. FAO (2022). Mountain Green Cover Index (SDG Indicator 15.4.2): Methodology.
