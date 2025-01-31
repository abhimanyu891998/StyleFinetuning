import base64
import os

from PIL import Image
import requests
from style_finetuning.const import UPSCALED_DIR


def convert_to_png(input_path, output_path):
    with Image.open(input_path) as img:
        # Save the image in PNG format
        img.save(output_path, 'PNG')


def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        return img.size  #


def download_image_base_64(base_64_image_str, local_file_name):
    print(f"Downloading base 64 - {local_file_name}...")
    if base_64_image_str:
        image_bytes = base64.b64decode(base_64_image_str)
        file_path = os.path.join(UPSCALED_DIR, local_file_name)

        with open(file_path, "wb") as image_file:
            image_file.write(image_bytes)
            print(f"Downloaded - {local_file_name} to {file_path}")
    else:
        print("No image provided")


def download_image_url(image_url, local_file_name):
    print(f"Downloading Image URL - {local_file_name}...")
    response = requests.get(image_url)
    if response.status_code == 200:
        file_path = os.path.join(UPSCALED_DIR, local_file_name)
        with open(file_path, "wb") as image_file:
            image_file.write(response.content)
            print(f"Downloaded - {local_file_name} to {file_path}")
            return 1
    else:
        print(f"Failed to download image from {image_url}, status code: {response.status_code}")
        return 0