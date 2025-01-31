import functools
import os
import shutil

import replicate
import concurrent.futures
from supabase import create_client, Client
from style_finetuning.const import UPSCALED_DIR, FINAL_DIR, SCALE_FACTOR, REMOTE_DIR_PATH, BUCKET_PATH
from style_finetuning.download import download_from_url
from style_finetuning.file import get_base_file_name
from style_finetuning.image_utils import download_image_base_64, download_image_url, get_image_dimensions
from style_finetuning.upload import upload_file_to_supabase
from style_finetuning.url import get_file_name_from_url, clean_url

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def upscale_image(image_url: str, scale_factor=SCALE_FACTOR):
    try:
        output = replicate.run(
            "philz1337x/clarity-upscaler:dfad41707589d68ecdccd1dfa600d55a208f9310748e44bfe35b4a6291453d5e",
            input={
                "seed": 1337,
                "image": image_url,
                "prompt": "masterpiece, best quality, highres, <lora:more_details:0.5> <lora:SDXLrender_v2.0:1>",
                "dynamic": 6,
                "handfix": "disabled",
                "pattern": False,
                "sharpen": 0,
                "sd_model": "juggernaut_reborn.safetensors [338b85bc4f]",
                "scheduler": "DPM++ 3M SDE Karras",
                "creativity": 0.2,
                "lora_links": "",
                "downscaling": False,
                "resemblance": 3,
                "scale_factor": scale_factor,
                "tiling_width": 112,
                "output_format": "png",
                "tiling_height": 144,
                "custom_sd_model": "",
                "negative_prompt": "(worst quality, low quality, normal quality:2) JuggernautNegative-neg",
                "num_inference_steps": 18,
                "downscaling_resolution": 768
            }
        )
        file_path = os.path.join(UPSCALED_DIR, get_file_name_from_url(image_url))
        file_output = output[0]
        with open(file_path, 'wb') as f:
            f.write(file_output.read())
            print(f"Downloaded - {file_path} to {UPSCALED_DIR}")

        final_file_path = os.path.join(FINAL_DIR, get_file_name_from_url(image_url))
        with open(final_file_path, 'wb') as f:
            f.write(file_output.read())
            print(f"Downloaded - {file_path} to {FINAL_DIR}")

        # upload image to supabase
        upload_file_to_supabase(final_file_path, "upscaled")

        return 1
    except Exception as e:
        print(f"Error during upscaling: {e}")
        return 0


def process_image(image_url):
    status = upscale_image(image_url)
    return (image_url, status)


def retry_failed_urls(failed_urls):
    print(f"Retrying failed urls: {len(failed_urls)} in total...")
    success_urls = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_image, failed_urls))
    for image_url, status in results:
        if status:
            print(f"Successfully upscaled - f{image_url}..")
            success_urls.append(image_url)
            failed_urls.remove(image_url)
        else:
            print(f"Failed to upscale again - f{image_url}...")

    return success_urls, failed_urls


def get_upscaled_images_stored(download=True, get_urls=False):
    upscale_remote_dir = f"{REMOTE_DIR_PATH}/upscaled"
    contents = supabase.storage.from_(BUCKET_PATH).list(upscale_remote_dir)
    files = [file['name'] for file in contents]
    if len(files):
        public_urls = [(file, supabase.storage.from_(BUCKET_PATH).get_public_url(f"{upscale_remote_dir}/{file}")) for file in files]
        public_urls = [clean_url(url, file_name) for (file_name, url) in public_urls]
        if download:
            partial_download_fn = functools.partial(download_from_url, local_dir=UPSCALED_DIR)
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(executor.map(partial_download_fn, public_urls))
        if get_urls:
            return public_urls

    # ensure all files downloaded
    if not all(results):
        raise ValueError("Failed to download all upscaled files; please check supabase status")

    for file_name in files:
        shutil.copy(f"{UPSCALED_DIR}/{file_name}", f"{FINAL_DIR}/{file_name}")
        print(f"Copied {file_name} from {UPSCALED_DIR} to {FINAL_DIR}...")
    return files


def upscale(image_urls):
    failed_urls = []
    success_urls = []

    # check if some of the images are already upscaled and stored to our db
    upscaled_remote_images = get_upscaled_images_stored()
    image_urls = [url for url in image_urls if get_file_name_from_url(url) not in upscaled_remote_images]
    print(f"Only upscaling - {len(image_urls)} images. Rest are already uploaded to storage.")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_image, image_urls))

    for image_url, status in results:
        if not status:
            failed_urls.append(image_url)
        else:
            print(f"Upscaled and downloaded - {image_url}")
            success_urls.append(image_url)

    success_indices = [int(get_file_name_from_url(url, with_extension=False)) for url in success_urls]

    for remote_image in upscaled_remote_images:
        success_indices.append(int(get_base_file_name(remote_image)))

    for i in success_indices:
        print(f"Upscaled Image {i}.png has dimensions - {get_image_dimensions(os.path.join(UPSCALED_DIR, f'{i}.png'))}")

    if len(failed_urls) > 0:
        MAX_TRIES = 3
        # retry failed urls
        for i in range(MAX_TRIES):
            retry_success_urls, failed_urls = retry_failed_urls(failed_urls)

    success_urls = get_upscaled_images_stored(download=False, get_urls=True)
    return success_urls, failed_urls
