import os
import shutil
from style_finetuning.const import FINAL_DIR, TRIGGER_WORD


def create_copies():
    for file in os.listdir(FINAL_DIR):
        if file.endswith('.png'):
            base_name = os.path.splitext(file)[0]
            txt_file = f"{base_name}.txt"
            if os.path.exists(os.path.join(FINAL_DIR, txt_file)):
                # Create copy of the .png file
                png_copy_file = f"{base_name}_copy.png"
                shutil.copy(os.path.join(FINAL_DIR, file), os.path.join(FINAL_DIR, png_copy_file))

                # Create new .txt file with the specified content
                txt_copy_file = f"{base_name}_copy.txt"
                with open(os.path.join(FINAL_DIR, txt_copy_file), 'w') as f:
                    f.write(f"{TRIGGER_WORD} illustration")