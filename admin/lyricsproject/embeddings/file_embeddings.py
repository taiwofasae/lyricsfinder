import json
import logging
import os
from lyricsproject import settings


embeddings_folder = os.path.join(settings.BASE_DIR, 'embeddings/embeds/')
song_folder = embeddings_folder+'song/'
phrase_folder = embeddings_folder+'phrase/'
search_folder = embeddings_folder+'search/'


def save_to_file(file_name, json_data):
    logging.info("writing to file: {0}".format(file_name))
    try:
        with open(file_name, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False)
    except Exception as e:
        logging.error(e)
        logging.info("file writing failed.")

def load_from_file(file_name):
    json_data = None
    try:
        with open(file_name, 'r') as f:
            json_data = json.load(f)
    except Exception as e:
        logging.error(e)
        logging.info("file reading failed.")
    
    return json_data

def save_song_embedding(song_id, embeddings):
    
    save_to_file("{0}{1}.csv".format(song_folder, song_id), embeddings)

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

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
