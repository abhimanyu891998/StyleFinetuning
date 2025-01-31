from style_finetuning.file import get_base_file_name


def clean_url(url: str, file_name: str):
    """
    Clean URL - remove unwanted chars after extension
    :param url: URL
    :param file_name: filename
    :return: cleaned URL
    """
    if url.endswith(f"{file_name}?"):
        return url[:-1]


def get_base_upload_url(url, with_last_slash=True):
    base_url = url.rsplit('/', 1)[0]
    if with_last_slash:
        return base_url + '/'
    return base_url


def get_file_name_from_url(url, with_extension=True):
    if with_extension:
        return url.rsplit('/', 1)[-1]
    else:
        return get_base_file_name(url.rsplit('/', 1)[-1])