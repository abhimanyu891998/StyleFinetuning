import os
import pandas as pd
from style_finetuning.const import FINAL_DIR
from style_finetuning.image_utils import get_image_dimensions

def extract_numeric_index(base_name):
    return int(base_name.split('_')[0])

def create_results_dfr():
    indices = []
    data = []

    # Collect all indices
    for file in os.listdir(FINAL_DIR):
        if file.endswith('.png'):
            base_name = os.path.splitext(file)[0]
            txt_file = f"{base_name}.txt"
            if os.path.exists(os.path.join(FINAL_DIR, txt_file)):
                indices.append(base_name)

    # Sort indices numerically
    indices.sort(key=extract_numeric_index)

    # Collect data based on sorted indices
    for base_name in indices:
        txt_file = f"{base_name}.txt"
        png_file = f"{base_name}.png"
        txt_path = os.path.join(FINAL_DIR, txt_file)
        png_path = os.path.join(FINAL_DIR, png_file)

        with open(txt_path, 'r') as f:
            caption = f.read().replace(',', '|').strip()

        resolution = get_image_dimensions(png_path)
        resolution_str = f"{resolution[0]}, {resolution[1]}"
        data.append({"Image": png_file, "Caption": caption, "Resolution": resolution_str})

    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(FINAL_DIR, "results.csv"), index=False)
    return df