import os


def create_dirs(*args):
    for directory in args:
        if not os.path.exists(directory):
            os.makedirs(directory)
