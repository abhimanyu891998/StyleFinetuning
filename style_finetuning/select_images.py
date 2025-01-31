import os
import random
from style_finetuning.const import FINAL_DIR, RAW_DIR, IMAGE_FORMATS, SELECTION_DIR
from style_finetuning.image_utils import convert_to_png


def get_random_images_from_data(target_images=15):
    # Get all image files in FINAL_DIR that match the formats in IMAGE_FORMATS
    image_files = [file for file in os.listdir(SELECTION_DIR) if file.split('.')[-1].lower() in IMAGE_FORMATS]

    # Randomly select target_images number of files
    selected_files = random.sample(image_files, min(target_images, len(image_files)))

    # Copy and convert selected files to RAW_DIR
    for file in selected_files:
        base_name = os.path.splitext(file)[0]
        source_path = os.path.join(SELECTION_DIR, file)
        destination_path = os.path.join(RAW_DIR, f"{base_name}.png")

        convert_to_png(source_path, destination_path)

    print(f"Selected {selected_files} from {SELECTION_DIR} and converted to png and copied to {RAW_DIR}....")
