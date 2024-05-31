from embeddings import settings
from embeddings import persistence
from common import songsearch, log
import importlib
import numpy as np

PERSIST = settings.EMBEDDINGS_PERSISTENCE

## Search id

def get_embeddings_for_search_id(search_id):

    return get_embeddings_for_search_ids([search_id])

def get_embeddings_for_search_ids(search_ids):

    embedding = [None for song_id in search_ids]

    if PERSIST:
        log.info("loading embedding from file")
        for i in range(len(search_ids)):
            embedding[i] = persistence.Storage().get_embeddings_for_search_ids(search_ids[i])
    
    null_idx = [i for i in range(len(search_ids)) if not embedding[i]]

    if null_idx:
        null_ids = [search_ids[i] for i in null_idx]
        log.info("fetching embedding from api")
        null_embedding = fetch_embeddings_for_search_ids(null_ids)

        for j in range(len(null_idx)):
            i = null_idx[j]
            embedding[i] = null_embedding[j]

    return embedding



def get_search_phrases(search_ids):
    searches = []
    for search_id in search_ids:
        searches.append(songsearch.get_search(search_id))
    return [search.search_phrase for search in searches]

    
def fetch_embeddings_for_search_ids(search_ids):

    log.info("getting search phrases for {0} search_ids".format(len(search_ids)))

    if len(search_ids) < 5:
        log.info("search_ids: {0}'"
                    .format(','.join([str(search_id) for search_id in search_ids])))

    searches = get_search_phrases(search_ids)

    if PERSIST:
        log.info("making sure file location is writable before calling api")
        persistence.Storage().save_search_phrase_embedding(search_ids[0], [])


    embeddings = get_embeddings_for_phrases(searches)

    if PERSIST:
        log.info("saving embeddings")
        for search_id, embed in zip(search_ids, embeddings):
            persistence.Storage().save_search_phrase_embedding(search_id, embed)

    return embeddings

def fetch_embeddings_for_search_id(search_id):

    return fetch_embeddings_for_search_ids([search_id])[0]


def fetch_embeddings_for_search_phrase(search_phrase):

    return get_embeddings_for_phrases([search_phrase])[0]

