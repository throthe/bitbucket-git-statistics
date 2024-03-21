import os
from datetime import datetime


def create_dir(dir):
    try:
        os.makedirs(dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Unable to create directory '{dir}': {e}")


def is_subdir(parent, *dirs):
    # Construct the full path to the subfolder
    full_path = os.path.join(parent, *dirs)
    # Check if the path exists and is a directory
    return os.path.isdir(full_path)


def get_subdirs(dir):
    """
    Return a list of names of all sub-directories in the given directory.

    :param directory: The path to the directory whose sub-directory you want to list.
    :return: A list of sub-directory names.
    """
    subdirs = []

    # Make sure the provided directory exists
    if not os.path.exists(dir):
        print(f"The directory {dir} does not exist.")
        return subdirs  # Returns an empty list if directory does not exist

    # List all entries in the directory
    for entry in os.listdir(dir):
        # Construct the full path to the entry
        full_path = os.path.join(dir, entry)
        # If the entry is a directory, add it to the list
        if os.path.isdir(full_path):
            subdirs.append(entry)

    return subdirs


def create_report_file_name(project_name, repo_name, file_extension="md"):
    now = datetime.now()
    return f"{now.strftime('%Y%m%d')}_{project_name}_{repo_name}.{file_extension}"


def get_datetime(format):
    now = datetime.now()
    return now.strftime(format)
