# Data Preparation Guide

This guide explains how to prepare data for any region using the MGCI framework.

## Overview

The data pipeline exports 7-band GeoTIFF patches from Google Earth Engine:

```
For each patch:
├── Band 0: Blue (Sentinel-2 B2)
├── Band 1: Green (Sentinel-2 B3)
├── Band 2: Red (Sentinel-2 B4)
├── Band 3: NIR (Sentinel-2 B8)
├── Band 4: Elevation (Copernicus DEM)
├── Band 5: Slope (derived, in degrees)
└── Band 6: VegLabel (NDVI > threshold, binary)
```

## Step 1: Choose Your Region

### Using FAO GAUL Boundaries

The framework uses FAO Global Administrative Unit Layers (GAUL) for region selection.

#### Available Levels

| Level | Examples | GEE Asset |
|-------|----------|-----------|
| Country | Saudi Arabia, Switzerland, Nepal | `FAO/GAUL/2015/level0` |
| Admin Level 1 | Jizan (province), Colorado (state) | `FAO/GAUL/2015/level1` |
| Admin Level 2 | County, district | `FAO/GAUL/2015/level2` |

#### Finding Your Region Name

```python
import ee
ee.Initialize()

# List all countries
countries = ee.FeatureCollection('FAO/GAUL/2015/level0')
print(countries.aggregate_array('ADM0_NAME').distinct().getInfo())

# List regions in a country
regions = ee.FeatureCollection('FAO/GAUL/2015/level1')
regions = regions.filter(ee.Filter.eq('ADM0_NAME', 'Saudi Arabia'))
print(regions.aggregate_array('ADM1_NAME').distinct().getInfo())
```

### Custom Boundaries

For custom study areas, you can upload a shapefile to GEE Assets:

```python
# Use your uploaded asset
region = ee.FeatureCollection('users/YOUR_USERNAME/your_boundary')
```

## Step 2: Configure Parameters

### Essential Parameters

```python
class Config:
    # Region identification
    COUNTRY = 'Saudi Arabia'       # Country name (exact match)
    REGION = 'Jizan'               # Province/state name
    
    # Temporal parameters
    YEAR = 2024                    # Analysis year
    START_DATE = '2024-01-01'      # Start of date range
    END_DATE = '2024-12-31'        # End of date range
    
    # Cloud filtering
    CLOUD_COVER_MAX = 20           # Maximum cloud cover (%)
    
    # MGCI parameters
    MOUNTAIN_THRESHOLD = 300       # Minimum elevation for mountains (m)
    NDVI_THRESHOLD = 0.30          # Vegetation threshold
    
    # Export parameters
    PATCH_SIZE = 2560              # Patch size in meters
    RESOLUTION = 10                # Pixel resolution (m)
```

### Parameter Guidelines

#### Date Range

| Region Type | Recommended Period | Notes |
|-------------|-------------------|-------|
| Tropical | Year-round | Avoid monsoon for fewer clouds |
| Temperate | Growing season (May-Sep) | Peak vegetation period |
| Arid | After rainy season | Capture ephemeral vegetation |
| Alpine | Summer months (Jun-Aug) | Snow-free period |

#### Cloud Cover Threshold

| Value | Use Case |
|-------|----------|
| 10% | Arid regions, clear skies common |
| 20% | Default, most regions |
| 30% | Tropical regions, frequent clouds |
| 50% | Very cloudy regions (may need manual inspection) |

#### NDVI Threshold

| Value | Vegetation Type |
|-------|-----------------|
| 0.20 | Sparse vegetation, arid regions |
| 0.30 | Default (FAO recommendation) |
| 0.40 | Dense vegetation only |

#### Mountain Threshold

| Value | Classification |
|-------|----------------|
| 300m | Kapos standard (includes foothills) |
| 500m | Exclude low foothills |
| 1000m | Montane and above only |

## Step 3: Estimate Data Volume

### Calculating Patch Count

```python
# Approximate formula:
# patches ≈ (region_area_km2) / (patch_size_km)^2

# Example: Jizan Province (~11,671 km²)
region_area = 11671  # km²
patch_size = 2.56    # km (256 pixels × 10m)
patches_approx = region_area / (patch_size ** 2)
print(f"Estimated patches: {patches_approx:.0f}")  # ~1,768

# With mountain filtering (~50% coverage):
print(f"After filtering: {patches_approx * 0.5:.0f}")  # ~884
```

### Storage Requirements

| Patches | Approximate Size | Export Time |
|---------|------------------|-------------|
| 100 | ~500 MB | 2-4 hours |
| 500 | ~2.5 GB | 10-15 hours |
| 1000 | ~5 GB | 20-30 hours |
| 5000 | ~25 GB | 4-5 days |

## Step 4: Run Data Export

### Pre-flight Checks

1. ✅ GEE account authenticated
2. ✅ Google Drive has sufficient space
3. ✅ Region name is correct
4. ✅ Date range is appropriate
5. ✅ Parameters are configured

### Running Notebook 1

1. Open `MGCI_1_DataExport.ipynb` in Colab
2. Update the `Config` class with your parameters
3. Run all cells
4. Monitor export tasks in [GEE Task Manager](https://code.earthengine.google.com/tasks)

### Monitoring Export Progress

```python
# Check task status
import ee
ee.Initialize()

tasks = ee.batch.Task.list()
for task in tasks[:10]:
    print(f"{task.status()['state']}: {task.status()['description']}")
```

### Export States

| State | Meaning |
|-------|---------|
| READY | Task queued |
| RUNNING | Currently exporting |
| COMPLETED | Successfully exported |
| FAILED | Error occurred (check logs) |
| CANCELLED | Manually stopped |

## Step 5: Verify Exported Data

### Check File Count

```python
import glob
files = glob.glob('/content/drive/MyDrive/MGCI_*/patch_*.tif')
print(f"Exported patches: {len(files)}")
```

### Verify Band Structure

```python
import rasterio

with rasterio.open(files[0]) as src:
    print(f"Bands: {src.count}")
    print(f"Size: {src.width} x {src.height}")
    print(f"CRS: {src.crs}")
    print(f"Resolution: {src.res}")
```

### Visual Inspection

```python
import matplotlib.pyplot as plt
import numpy as np

with rasterio.open(files[0]) as src:
    data = src.read()

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
bands = ['Blue', 'Green', 'Red', 'NIR', 'Elevation', 'Slope', 'VegLabel']

for i, (ax, name) in enumerate(zip(axes.flat, bands)):
    ax.imshow(data[i], cmap='viridis' if i < 6 else 'Greens')
    ax.set_title(name)
    ax.axis('off')

plt.tight_layout()
plt.show()
```

## Common Issues

### No Imagery Found

**Symptom:** Empty or very few patches exported

**Solutions:**
1. Expand date range
2. Increase cloud cover threshold
3. Check region name spelling
4. Verify Sentinel-2 coverage for your region

### Export Tasks Failing

**Symptom:** Tasks show FAILED status

**Solutions:**
1. Reduce patch size
2. Export in smaller batches
3. Check GEE quota limits
4. Verify region geometry is valid

### Memory Errors

**Symptom:** "User memory limit exceeded"

**Solutions:**
1. Reduce image resolution (e.g., 20m instead of 10m)
2. Process in smaller time windows
3. Simplify region geometry

## Next Steps

After successful data export:

1. **Training (Option A):** Proceed to Notebook 2 to train a model
2. **Inference (Option B):** Use pre-trained weights and skip to Notebook 3

See [METHODOLOGY.md](METHODOLOGY.md) for technical details on the model and MGCI calculation.
