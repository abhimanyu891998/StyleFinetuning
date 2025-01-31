import concurrent.futures
import os
from supabase import create_client, Client
from const import REMOTE_DIR_PATH, BUCKET_PATH, PREPROCESSED_DIR, DIR_NAME, STYLE_NAME, RAW_DIR
from style_finetuning.url import get_base_upload_url, clean_url
import functools

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

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


def upload_file_to_supabase(image_path, dir_name):
    file_name = os.path.basename(image_path)
    remote_file_path = f"{REMOTE_DIR_PATH}/{dir_name}/{file_name}"
    with open(image_path, 'rb') as f:
        try:
            supabase.storage.from_(BUCKET_PATH).upload(file=f, path=remote_file_path,
                                                       file_options={"content-type": "image/png"})
        except Exception as e:
            if e.status == '409':
                logger.error(f"File already exists on supabase: {remote_file_path}")
                remote_url = supabase.storage.from_(BUCKET_PATH).get_public_url(
                    remote_file_path)
                return clean_url(remote_url, file_name)

            logger.error(f"Error saving image to database: {str(e)}")

        uploaded_url = supabase.storage.from_(BUCKET_PATH).get_public_url(remote_file_path)
        uploaded_url = clean_url(uploaded_url, file_name)
        logger.info(f"Uploaded file to supabase: {uploaded_url}")
        return uploaded_url


def delete_remote_dir(remote_dir):
    contents_to_delete = supabase.storage.from_(BUCKET_PATH).list(remote_dir)
    contents_to_delete = [f"{remote_dir}/{file['name']}" for file in contents_to_delete]
    # Delete the files
    if len(contents_to_delete):
        delete_response = supabase.storage.from_(BUCKET_PATH).remove(contents_to_delete)
        if len(delete_response) != len(contents_to_delete):
            logger.error(f"Failed to delete remote files: {delete_response}")
            return []
        else:
            print(f"Remote files cleared successfully")
    else:
        print(f"No files to delete")


def upload(images_length, dir_name='raw', clean_up=True):
    if clean_up:
        # delete the supabase dir
        try:
            delete_remote_dir(f"{REMOTE_DIR_PATH}/raw")
        except Exception as e:
            print(f"Failed to delete remote dir path - {e}")
            return []

    image_paths = [os.path.join(PREPROCESSED_DIR, f"{i}.png") for i in range(1, images_length + 1)]
    uploaded_urls = []

    partial_upload_fn = functools.partial(upload_file_to_supabase, dir_name=dir_name)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(partial_upload_fn, image_paths)
        uploaded_urls = list(results)

    base_url = get_base_upload_url(uploaded_urls[0], with_last_slash=False)
    if len(uploaded_urls) != images_length:
        logger.error(f"Failed to upload all images to supabase: {len(uploaded_urls)} uploaded out of {images_length}")
        return []

    remote_urls = [f"{base_url}/{i}.png" for i in range(1, images_length + 1)]
    return remote_urls
