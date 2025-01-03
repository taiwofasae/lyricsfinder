import json
from common import log
import os
import shutil
from lyricsproject import settings

storage_folder = os.path.join(settings.BASE_DIR, 'appdata')


def upload_file(file_name, json_data):
    file_name = os.path.join(storage_folder, file_name)

    log.info("writing to file: {0}".format(file_name))

    with open(file_name, 'w') as f:
        json.dump(json_data, f, ensure_ascii=False)

def download_file(file_name, json_deserialize=True):

    file_name = os.path.join(storage_folder, file_name)
    
    try:
        with open(file_name, 'r') as f:
            if json_deserialize:
                json_data = json.load(f)
                return json_data
            return f.read()
    except Exception as e:
        log.error(e)
        log.info("file reading failed.")
    
    return None

def copy(source, dest):
    shutil.copyfile(get_full_path(source), get_full_path(dest))

def file_exists(file_name):

    return os.path.exists(get_full_path(file_name))

def get_full_path(file_name):

    return os.path.join(storage_folder, file_name)

def make_directory(folder):

    folder = get_full_path(folder)
    if not os.path.exists(folder):
        os.makedirs(folder)

def make_directory_from_filepath(filepath):

    dir_path = os.path.dirname(filepath)
    make_directory(dir_path)

def delete_file(filepath):
    log.info("deleting file {}".format(filepath))
    os.remove(filepath)