# Example Configuration: Jizan Province, Saudi Arabia
# This configuration was used for the original study

"""
Jizan Province Configuration

Region: Jizan Province, Saudi Arabia
Area: ~11,671 km²
Terrain: Coastal to mountainous (0-2,600m)
Climate: Tropical/semi-arid
"""

class Config:
    # Region
    COUNTRY = 'Saudi Arabia'
    REGION = 'Jizan'
    
    # Temporal
    YEAR = 2024
    START_DATE = '2024-01-01'
    END_DATE = '2024-12-31'
    
    # Cloud filtering
    CLOUD_COVER_MAX = 20
    
    # MGCI parameters
    MOUNTAIN_THRESHOLD = 300
    NDVI_THRESHOLD = 0.30
    
    # Export parameters
    PATCH_SIZE = 2560
    RESOLUTION = 10
    PATCH_MOUNTAIN_MIN = 1.0
    
    # Paths
    DATA_DIR = '/content/drive/MyDrive/MGCI_Jizan_2024'
    OUTPUT_DIR = '/content/outputs'
    MODEL_PATH = '/content/drive/MyDrive/MGCI_Jizan_2024/model_best.pth'
    
    # Bands
    BAND_NAMES = ['Blue', 'Green', 'Red', 'NIR', 'Elevation', 'Slope', 'VegLabel']
    BLUE_BAND = 0
    GREEN_BAND = 1
    RED_BAND = 2
    NIR_BAND = 3
    ELEV_BAND = 4
    SLOPE_BAND = 5
    LABEL_BAND = 6
    INPUT_BANDS = [0, 1, 2, 3, 4, 5]
    N_CHANNELS = 6
    
    # Model
    MODEL = 'Unet'
    ENCODER = 'resnet50'
    ENCODER_WEIGHTS = 'imagenet'
    
    # Training
    BATCH_SIZE = 8
    EPOCHS = 80
    LR = 3e-4
    WEIGHT_DECAY = 1e-4
    PATIENCE = 15
    TRAIN_RATIO = 0.70
    VAL_RATIO = 0.15
    TEST_RATIO = 0.15
    SEED = 42


# Expected Results (from original study):
# - Total patches: 878
# - Mountain area: 4,286 km² (planimetric)
# - Surface area correction: +12.95%
# - MGCI (Model, True Surface): 19.36%
# - Test IoU: 0.8475
# - Test Dice: 0.9263
