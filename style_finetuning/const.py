STYLE_NAME = "graffiti_text"
TRIGGER_WORD = "GRFT"
CAPTION_PRE_APPEND = f"An illustration in the style of {TRIGGER_WORD}."
SCALE_FACTOR = 2
IS_SELECTION_NEEDED = False

# derivatives
RAW_DIR = f"./train/{STYLE_NAME}/raw"
SELECTION_DIR = f"./train/{STYLE_NAME}/selection"
PREPROCESSED_DIR = f"./train/{STYLE_NAME}/preprocessed"
UPSCALED_DIR = f"./train/{STYLE_NAME}/upscaled"
FINAL_DIR = f"./train/{STYLE_NAME}/final"
BUCKET_PATH = "temp_storage"
DIR_NAME = "finetuning"
REMOTE_DIR_PATH = f"{DIR_NAME}/{STYLE_NAME}"
IMAGE_FORMATS = ['png', 'jpg', 'jpeg']
