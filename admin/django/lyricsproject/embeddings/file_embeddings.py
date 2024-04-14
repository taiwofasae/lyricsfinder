import json
import logging
import os
from lyricsproject import settings


embeddings_folder = os.path.join(settings.BASE_DIR, 'embeddings/embeds/')
song_folder = embeddings_folder+'song/'
phrase_folder = embeddings_folder+'phrase/'
search_folder = embeddings_folder+'search/'
def save_song_embedding(song_id, embeddings):
    
    with open("{0}{1}.csv".format(song_folder, song_id), 'w') as f:
        json.dump(embeddings, f, ensure_ascii=False)

def load_song_embedding(song_id):
    
    embeddings = []
    try:
        with open("{0}{1}.csv".format(song_folder, song_id), 'r') as f:
            embeddings = json.load(f)
    except Exception as e:
        logging.error(e)

    return embeddings

def save_phrase_embedding(phrase_id, embeddings):
    
    with open("{0}{1}.csv".format(phrase_folder, phrase_id), 'w') as f:
        json.dump(embeddings, f, ensure_ascii=False)


def load_phrase_embedding(phrase_id):
    
    embeddings = []

    try:
        with open("{0}{1}.csv".format(phrase_folder, phrase_id), 'r') as f:
            embeddings = json.load(f)
    except Exception as e:
        logging.error(e)
    return embeddings

def save_search_phrase_embedding(search_id, embeddings):
    
    with open("{0}{1}.csv".format(search_folder, search_id), 'w') as f:
        json.dump(embeddings, f, ensure_ascii=False)

def load_search_phrase_embedding(search_id):
    
    embeddings = []

    try:
        with open("{0}{1}.csv".format(search_folder, search_id), 'r') as f:
            embeddings = json.load(f)
    except Exception as e:
        logging.error(e)
    return embeddings

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
