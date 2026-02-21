# Troubleshooting Guide

Common issues and solutions when using the MGCI Deep Learning framework.

## Table of Contents

- [Google Earth Engine Issues](#google-earth-engine-issues)
- [Data Export Issues](#data-export-issues)
- [Training Issues](#training-issues)
- [Inference Issues](#inference-issues)
- [Memory Issues](#memory-issues)
- [File and Path Issues](#file-and-path-issues)

---

## Google Earth Engine Issues

### "Please sign up for Earth Engine"

**Symptom:** Error when running `ee.Initialize()`

**Solution:**
1. Go to https://earthengine.google.com/signup/
2. Sign up with your Google account
3. Wait for approval (24-48 hours)
4. Re-run the notebook

### "Invalid project ID"

**Symptom:** `ee.Initialize(project='...')` fails

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Earth Engine API
4. Use the project ID (not name) in `ee.Initialize()`

### Authentication Token Expired

**Symptom:** Previously working code now fails

**Solution:**
```python
ee.Authenticate(force=True)  # Force re-authentication
ee.Initialize()
```

### "User memory limit exceeded"

**Symptom:** GEE computation fails

**Solutions:**
1. Reduce region size or process in parts
2. Lower image resolution (20m instead of 10m)
3. Reduce date range
4. Add `.aside(print)` to debug which step fails

---

## Data Export Issues

### No Patches Exported

**Symptom:** Export completes but no files in Drive

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Wrong region name | Check spelling, use `aggregate_array()` to list regions |
| No mountain area | Lower `MOUNTAIN_THRESHOLD` or check region has mountains |
| All clouds | Increase `CLOUD_COVER_MAX` or change date range |
| Export path wrong | Check Drive folder exists and path is correct |

### Export Tasks Stuck at "READY"

**Symptom:** Tasks never start running

**Solutions:**
1. GEE may be busy; wait a few hours
2. Check [GEE status page](https://code.earthengine.google.com/tasks)
3. Cancel all tasks and restart
4. Reduce number of concurrent exports

### "Export too large" Error

**Symptom:** Individual export task fails

**Solutions:**
1. Reduce `PATCH_SIZE` (e.g., 1280 instead of 2560)
2. Lower resolution (20m)
3. Export to Google Cloud Storage instead of Drive

### Corrupted/Incomplete GeoTIFFs

**Symptom:** `rasterio.open()` fails or data looks wrong

**Solutions:**
1. Delete corrupted file and re-export
2. Check Drive sync is complete
3. Verify with `gdalinfo filename.tif`

---

## Training Issues

### CUDA Out of Memory

**Symptom:** `RuntimeError: CUDA out of memory`

**Solutions:**

| Solution | How |
|----------|-----|
| Reduce batch size | `Config.BATCH_SIZE = 4` or `2` |
| Use gradient accumulation | Accumulate over 2-4 steps |
| Use mixed precision | `torch.cuda.amp.autocast()` |
| Use smaller model | Try `resnet34` instead of `resnet50` |

### Loss is NaN

**Symptom:** Training loss becomes NaN

**Solutions:**
1. Lower learning rate: `Config.LR = 1e-5`
2. Add gradient clipping (already included)
3. Check for NaN in data:
```python
for f in files[:10]:
    data = rasterio.open(f).read()
    if np.isnan(data).any():
        print(f"NaN in {f}")
```
4. Increase epsilon in NDVI calculation: `(nir - red) / (nir + red + 1e-6)`

### Model Not Learning (Flat Loss)

**Symptom:** Loss doesn't decrease

**Solutions:**
1. Check labels are correct (0 and 1, not 0 and 255)
2. Increase learning rate
3. Check data augmentation isn't too aggressive
4. Verify data loading:
```python
img, label = train_dataset[0]
print(f"Image range: [{img.min()}, {img.max()}]")
print(f"Label unique: {torch.unique(label)}")
```

### Poor Validation Metrics

**Symptom:** High training metrics, low validation

**Causes:**
- Overfitting
- Data leakage in split
- Domain shift between train/val regions

**Solutions:**
1. Increase data augmentation
2. Add dropout or weight decay
3. Ensure spatial split (not random)
4. Early stopping (already included)

---

## Inference Issues

### Model Loading Fails

**Symptom:** `torch.load()` error

**Solutions:**

```python
# For PyTorch 2.6+, use weights_only=False for your own models
checkpoint = torch.load(path, map_location=device, weights_only=False)

# If "CUDA not available" when loading GPU model on CPU:
checkpoint = torch.load(path, map_location='cpu')
```

### Predictions All Same Value

**Symptom:** Model outputs all 0s or all 1s

**Solutions:**
1. Ensure normalization matches training:
```python
MEANS = checkpoint['means']  # Use saved stats
STDS = checkpoint['stds']
```
2. Check model is in eval mode:
```python
model.eval()
```
3. Verify input data range

### MGCI Values Unrealistic

**Symptom:** MGCI > 100% or negative

**Solutions:**
1. Check mountain mask is correct
2. Verify area calculations
3. Check for division issues:
```python
if mountain_area > 0:
    mgci = green_area / mountain_area * 100
else:
    mgci = 0
```

---

## Memory Issues

### Google Colab RAM Crash

**Symptom:** "Your session crashed after using all available RAM"

**Solutions:**
1. Process patches in batches:
```python
for i in range(0, len(files), 100):
    batch = files[i:i+100]
    process(batch)
    gc.collect()  # Force garbage collection
```
2. Don't load all patches into memory
3. Use generators instead of lists
4. Clear unused variables:
```python
del large_variable
import gc
gc.collect()
```

### "Unable to allocate" Array Error

**Symptom:** NumPy memory allocation fails

**Solutions:**
1. Process smaller regions
2. Use float32 instead of float64
3. Load and process one patch at a time

---

## File and Path Issues

### "No .tif files found"

**Symptom:** Notebook can't find exported patches

**Solutions:**
1. Check Google Drive mount:
```python
!ls /content/drive/MyDrive/
```
2. Verify folder name exactly matches
3. Wait for Drive sync to complete
4. Re-mount Drive:
```python
drive.flush_and_unmount()
drive.mount('/content/drive', force_remount=True)
```

### Permission Denied

**Symptom:** Can't write to directory

**Solutions:**
1. Don't write to `/content/drive/` root
2. Create output directory first:
```python
os.makedirs(output_dir, exist_ok=True)
```
3. Check folder permissions in Drive

### "File exists" Error

**Symptom:** Can't overwrite existing file

**Solution:**
```python
import os
if os.path.exists(filepath):
    os.remove(filepath)
# Then save
```

---

## Getting More Help

### Debug Information to Collect

When reporting issues, please include:

```python
import sys
import torch
print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Where to Ask

1. **GitHub Issues**: For bugs and feature requests
2. **GEE Forum**: For Earth Engine questions
3. **PyTorch Forums**: For deep learning questions
4. **Stack Overflow**: For general Python/coding issues

### Quick Checklist

Before asking for help, verify:

- [ ] Running latest version of notebooks
- [ ] All cells run in order (don't skip)
- [ ] Paths are correct
- [ ] GPU runtime enabled (for training)
- [ ] GEE authenticated
- [ ] Sufficient storage space
