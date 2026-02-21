# Example Region Configuration Template
# Copy this file and modify for your region

"""
Configuration template for MGCI analysis.

Instructions:
1. Copy this file to your working directory
2. Modify the parameters for your region
3. Copy the Config class to the notebook
"""

class Config:
    """
    Configuration class for MGCI analysis.
    Modify these parameters for your specific region.
    """
    
    # =========================================================================
    # REGION IDENTIFICATION
    # =========================================================================
    
    # Country name (must match FAO GAUL exactly)
    # Use ee.FeatureCollection('FAO/GAUL/2015/level0').aggregate_array('ADM0_NAME').distinct()
    # to find exact country names
    COUNTRY = 'Your Country Name'
    
    # Region/Province name (must match FAO GAUL exactly)
    # Use ee.FeatureCollection('FAO/GAUL/2015/level1').filter(...).aggregate_array('ADM1_NAME')
    # to find exact region names
    REGION = 'Your Region Name'
    
    # =========================================================================
    # TEMPORAL PARAMETERS
    # =========================================================================
    
    # Year of analysis
    YEAR = 2024
    
    # Date range for satellite imagery
    # Adjust based on your region's characteristics:
    # - Temperate: Use growing season (May-September)
    # - Tropical: Avoid monsoon season
    # - Arid: After rainy season
    # - Alpine: Snow-free period (June-August)
    START_DATE = '2024-01-01'
    END_DATE = '2024-12-31'
    
    # =========================================================================
    # CLOUD FILTERING
    # =========================================================================
    
    # Maximum cloud cover percentage for Sentinel-2 scenes
    # - 10%: Very strict, for arid regions with clear skies
    # - 20%: Default, works for most regions
    # - 30-50%: For tropical/cloudy regions
    CLOUD_COVER_MAX = 20
    
    # =========================================================================
    # MGCI PARAMETERS
    # =========================================================================
    
    # Minimum elevation to consider as "mountain" (meters)
    # Standard Kapos classification starts at 300m
    # Adjust if your region has different characteristics
    MOUNTAIN_THRESHOLD = 300
    
    # NDVI threshold for vegetation classification
    # FAO recommends 0.3 for standard MGCI
    # - 0.2: Include sparse vegetation (arid regions)
    # - 0.3: Default (FAO standard)
    # - 0.4: Only dense vegetation
    NDVI_THRESHOLD = 0.30
    
    # =========================================================================
    # EXPORT PARAMETERS
    # =========================================================================
    
    # Patch size in meters (determines export tile size)
    # 2560m = 256 pixels at 10m resolution
    # Reduce if exports fail (memory issues)
    PATCH_SIZE = 2560
    
    # Pixel resolution in meters
    # 10m: Full Sentinel-2 resolution
    # 20m: Faster processing, less storage
    RESOLUTION = 10
    
    # Minimum mountain coverage to export a patch (%)
    # Patches with less mountain area are skipped
    PATCH_MOUNTAIN_MIN = 1.0
    
    # =========================================================================
    # OUTPUT PATHS (for Google Colab)
    # =========================================================================
    
    # Google Drive output folder
    # Will be created at: /content/drive/MyDrive/{DATA_DIR}
    DATA_DIR = f'/content/drive/MyDrive/MGCI_{REGION.replace(" ", "_")}_{YEAR}'
    
    # Local output directory (temporary)
    OUTPUT_DIR = '/content/outputs'
    
    # Model save path
    MODEL_PATH = f'{DATA_DIR}/model_best.pth'
    
    # =========================================================================
    # BAND CONFIGURATION (DO NOT MODIFY)
    # =========================================================================
    
    # Band indices in exported GeoTIFF
    BAND_NAMES = ['Blue', 'Green', 'Red', 'NIR', 'Elevation', 'Slope', 'VegLabel']
    BLUE_BAND = 0
    GREEN_BAND = 1
    RED_BAND = 2
    NIR_BAND = 3
    ELEV_BAND = 4
    SLOPE_BAND = 5
    LABEL_BAND = 6
    
    # Model input bands (all except label)
    INPUT_BANDS = [0, 1, 2, 3, 4, 5]
    N_CHANNELS = 6
    
    # =========================================================================
    # MODEL ARCHITECTURE (for training)
    # =========================================================================
    
    MODEL = 'Unet'
    ENCODER = 'resnet50'
    ENCODER_WEIGHTS = 'imagenet'
    
    # =========================================================================
    # TRAINING HYPERPARAMETERS
    # =========================================================================
    
    BATCH_SIZE = 8
    EPOCHS = 80
    LR = 3e-4
    WEIGHT_DECAY = 1e-4
    PATIENCE = 15
    
    # Data split ratios
    TRAIN_RATIO = 0.70
    VAL_RATIO = 0.15
    TEST_RATIO = 0.15
    
    # Random seed for reproducibility
    SEED = 42


# =========================================================================
# USAGE EXAMPLE
# =========================================================================

if __name__ == '__main__':
    # Print configuration summary
    print("MGCI Configuration")
    print("=" * 50)
    print(f"Region: {Config.REGION}, {Config.COUNTRY}")
    print(f"Year: {Config.YEAR}")
    print(f"Date range: {Config.START_DATE} to {Config.END_DATE}")
    print(f"Mountain threshold: {Config.MOUNTAIN_THRESHOLD}m")
    print(f"NDVI threshold: {Config.NDVI_THRESHOLD}")
    print(f"Output: {Config.DATA_DIR}")
    print("=" * 50)
