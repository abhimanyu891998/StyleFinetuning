import os.path

import fal_client
import concurrent.futures
from style_finetuning.const import FINAL_DIR, TRIGGER_WORD, CAPTION_PRE_APPEND
from style_finetuning.file import get_base_file_name
from style_finetuning.url import get_file_name_from_url


def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(log["message"])


def caption_image(image_url, local_file_name):
    base_file_name = get_base_file_name(local_file_name)
    result = fal_client.subscribe(
        "fal-ai/any-llm/vision",
        arguments={
            "prompt": "Describe the content of this image in three sentences but do not describe style.",
            "image_url": image_url,
            "system_prompt": "Only answer the question, do not provide any additional information or add any prefix/suffix other than the answer of the original question. Don't use markdown.",
            "model": "anthropic/claude-3.5-sonnet",
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    if len(result['output']):
        image_caption = CAPTION_PRE_APPEND + " " + result['output']
        print(f"Image Caption: {image_caption} and will be stored as - {base_file_name}.txt")
        caption_file_path = os.path.join(FINAL_DIR, f"{base_file_name}.txt")
        with open(caption_file_path, 'w') as f:
            f.write(image_caption)
        return 1
    else:
        print(f"Failed to caption image - {local_file_name}")
        return 0


def process_image(image_url):
    status = caption_image(image_url, get_file_name_from_url(image_url))
    return (image_url, status)


def caption(image_urls):
    failed_urls = []
    success_urls = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_image, image_urls))

    for image_url, status in results:
        if not status:
            failed_urls.append(image_url)
        else:
            print(f"Captioned and downloaded - {image_url}")
            success_urls.append(image_url)

    return success_urls, failed_urls
