# utils.py

import os

def get_image_files(folder_path):
    #return a list of image filenames in a folder

    valid_extensions = ('.jpg', '.jpeg', '.png')
    return [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

def create_output_folder(folder_path):
    """Create output folder if it does not exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
