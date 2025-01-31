import os
import shutil

from style_finetuning.const import RAW_DIR, PREPROCESSED_DIR, IMAGE_FORMATS
from style_finetuning.image_utils import convert_to_png, get_image_dimensions


def numerify_training_set():
    # List all image files in the input directory
    image_files = [f for f in os.listdir(RAW_DIR) if any(f.endswith(ext) for ext in IMAGE_FORMATS)]

    # Sort files to ensure consistent numbering
    image_files.sort()
    # Rename and save each file to the output directory
    for idx, file_name in enumerate(image_files, start=1):
        input_file_path = os.path.join(RAW_DIR, file_name)
        new_file_name = f"{idx}.png"
        output_file_path = os.path.join(PREPROCESSED_DIR, new_file_name)

        # Convert to PNG if not already a PNG
        if not file_name.endswith('.png'):
            temp_output_path = os.path.join(PREPROCESSED_DIR, f"temp_{file_name}.png")
            convert_to_png(input_file_path, temp_output_path)
            shutil.copy(input_file_path, output_file_path)
        else:
            shutil.copy(input_file_path, output_file_path)

    return len(image_files)


def preprocess():
    no_of_images = numerify_training_set()

    for i in range(1, no_of_images+1):
        print(f"Image {i}.png has dimensions - {get_image_dimensions(os.path.join(PREPROCESSED_DIR, f'{i}.png'))}")

    return no_of_images