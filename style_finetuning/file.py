def get_base_file_name(file_name):
    return file_name.split('.')[0]


def get_remote_file_name_from_url(url, with_extension=False):
    if with_extension:
        return url.split('/')[-1]
    else:
        return get_base_file_name(url.split('/')[-1])
