import requests

from style_finetuning.url import get_file_name_from_url


def download_from_url(remote_url, local_dir):
    file_name = get_file_name_from_url(remote_url, with_extension=True)
    try:
        response = requests.get(remote_url)
        response.raise_for_status()
        with open(f"{local_dir}/{file_name}", "wb") as image_file:
            image_file.write(response.content)
            print(f"Downloaded - {file_name} to {local_dir}/{file_name}")
            return True
    except Exception as e:
        print(f"Error downloading file - {e}")
        return False
