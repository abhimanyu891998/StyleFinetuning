import sys

from style_finetuning.caption import caption
from style_finetuning.consolidate import create_results_dfr
from style_finetuning.const import RAW_DIR, PREPROCESSED_DIR, UPSCALED_DIR, FINAL_DIR, IS_SELECTION_NEEDED
from style_finetuning.create_copies import create_copies
from style_finetuning.os_utils import create_dirs
from style_finetuning.preprocess import preprocess
from style_finetuning.select_images import get_random_images_from_data
from style_finetuning.upload import upload
from style_finetuning.upscale import upscale

import logging

logging.basicConfig(
    level=logging.INFO,  # Set the log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Set the log format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)


def check_status(success_items, failed_items, key):
    if failed_items:
        for failed_item in failed_items:
            print(f"Failed to {key}: ", failed_item)
        sys.exit()

    if len(success_items) == len(failed_items):
        print(f"All images {key}ed successfully, beginning next step...")


if __name__ == '__main__':
    create_dirs(RAW_DIR, PREPROCESSED_DIR, UPSCALED_DIR, FINAL_DIR)
    if IS_SELECTION_NEEDED:
        get_random_images_from_data(target_images=30)
    images_length = preprocess()
    print(f"Preprocessed {images_length} images")
    print(f"Uploading images to supabase...")
    uploaded_urls = upload(images_length, dir_name='raw', clean_up=False)
    success_urls, failed_urls = upscale(uploaded_urls)
    check_status(success_urls, failed_urls, "upscale")
    success_urls, failed_urls = caption(uploaded_urls)
    check_status(success_urls, failed_urls, "caption")
    # create_copies()
    create_results_dfr()
    print("All done :D")

# 1. Check if upscale needed or not - test with upscale and without
# 2. Check fal vs replicate training - which one better, if its comparable then use fal
# 3. Repkicate training and auto storing of loras in supbase
# 4. Create config file for that automatically laso
