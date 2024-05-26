import json
from common import log
import os
import ast
from lyricsproject import settings


embeddings_folder = os.path.join(settings.BASE_DIR, 'embeddings/embeds/')
song_folder = embeddings_folder+'song/'
phrase_folder = embeddings_folder+'phrase/'
search_folder = embeddings_folder+'search/'

status_file = song_folder + 'status.txt'


def save_to_file(file_name, json_data):
    log.info("writing to file: {0}".format(file_name))

    with open(file_name, 'w') as f:
        json.dump(json_data, f, ensure_ascii=False)

def load_from_file(file_name):
    json_data = None
    try:
        with open(file_name, 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        log.error(e)
        log.info("file reading failed.")
    
    return json_data


def save_song_embedding(song_id, embeddings):
    
    save_to_file("{0}{1}.csv".format(song_folder, song_id), embeddings)
    _update_status(song_id)

def load_song_embedding(song_id):
    
    return load_from_file("{0}{1}.csv".format(song_folder, song_id)) or []

def save_phrase_embedding(phrase_id, embeddings):
    
    save_to_file("{0}{1}.csv".format(phrase_folder, phrase_id), embeddings)


def load_phrase_embedding(phrase_id):
    
    return load_from_file("{0}{1}.csv".format(phrase_folder, phrase_id)) or []

def save_search_phrase_embedding(search_id, embeddings):
    
    save_to_file("{0}{1}.csv".format(search_folder, search_id), embeddings)

def load_search_phrase_embedding(search_id):
    
    return load_from_file("{0}{1}.csv".format(search_folder, search_id)) or []


## status management

def _load_status():
    log.info("loading status set from s3")
    return ast.literal_eval(load_from_file(status_file) or '') or set()

def _save_status(status_set):
    log.info("saving status set to s3")
    save_to_file(status_file, str(status_set))


def _update_status(song_id):
    status_set = _load_status()
    if song_id not in status_set:
        status_set.add(song_id)
        _save_status(status_set)

def song_embedding_exists(song_id):
    try:
        status_set = _load_status()
    except:
        _save_status(set())
        status_set = _load_status()
        
    if isinstance(song_id, list):
        return [id in status_set for id in song_id]
    
    return song_id in status_set

def all_song_statuses():
    return _load_status()