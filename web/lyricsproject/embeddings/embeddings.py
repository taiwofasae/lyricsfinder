from embeddings import s3, settings
from embeddings import file as file_embeddings
from embeddings import openai_api as embed_api
from common import songsearch, log

if settings.S3_NOT_FILE:
    file_embeddings = s3

PERSIST = settings.EMBEDDINGS_PERSISTENCE

def api_version():
    return embed_api.API_VERSION
   
def get_embeddings_for_song(song_id):
    return get_embeddings_for_songs([song_id])

def get_embeddings_for_songs(song_ids):
    embedding = [None for song_id in song_ids]

    if PERSIST:
        log.info("loading embedding from file")
        for i in range(len(song_ids)):
            embedding[i] = file_embeddings.load_song_embedding(song_ids[i])
    
    null_idx = [i for i in range(len(song_ids)) if not embedding[i]]

    if null_idx:
        null_ids = [song_ids[i] for i in null_idx]
        log.info("fetching embedding from api")
        null_embedding = fetch_embeddings_for_songs(null_ids)

        for j in range(len(null_idx)):
            i = null_idx[j]
            embedding[i] = null_embedding[j]

    return embedding

def get_embeddings_for_search_id(search_id):

    return get_embeddings_for_search_ids([search_id])

def get_embeddings_for_search_ids(search_ids):

    embedding = [None for song_id in search_ids]

    if PERSIST:
        log.info("loading embedding from file")
        for i in range(len(search_ids)):
            embedding[i] = file_embeddings.load_search_phrase_embedding(search_ids[i])
    
    null_idx = [i for i in range(len(search_ids)) if not embedding[i]]

    if null_idx:
        null_ids = [search_ids[i] for i in null_idx]
        log.info("fetching embedding from api")
        null_embedding = fetch_embeddings_for_search_ids(null_ids)

        for j in range(len(null_idx)):
            i = null_idx[j]
            embedding[i] = null_embedding[j]

    return embedding


def get_song_details(song_ids):
    songs = []
    for song_id in song_ids:
        songs.append(songsearch.get_song(song_id))
    return [(song.song_id, song.title, song.lyrics) for song in songs]

def fetch_embeddings_for_song(song_id):

    return fetch_embeddings_for_songs([song_id])[0]

def fetch_embeddings_for_songs(song_ids):

    log.info("getting song details for {0} song_ids".format(len(song_ids)))

    if len(song_ids) < 5:
        log.info("song_ids: {0}'"
                    .format(','.join([str(song_id) for song_id in song_ids])))

    songs = get_song_details(song_ids)

    if PERSIST:
        log.info("making sure folder is accessible before calling api")
        file_embeddings.save_song_embedding(song_id=song_ids[0], embeddings=[])

    
    if len(song_ids) < 5:
        titles = [song[1] for song in songs]
        log.info("Titles: {0}".format('\n'.join(titles)))

    embeddings = embed_api.get_embeddings_for_phrases([lyrics for (song_id, title, lyrics) in songs])

    if PERSIST:
        log.info("inserting/updating song embeddings")
        for song_id, e in zip(song_ids, embeddings):
            file_embeddings.save_song_embedding(song_id, e)

    return embeddings

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
        file_embeddings.save_search_phrase_embedding(search_ids[0], [])


    embeddings = fetch_embeddings_for_search_phrases(searches)

    if PERSIST:
        log.info("saving embeddings")
        for search_id, embed in zip(search_ids, embeddings):
            file_embeddings.save_search_phrase_embedding(search_id, embed)

    return embeddings

def fetch_embeddings_for_search_id(search_id):

    return fetch_embeddings_for_search_ids([search_id])[0]

def fetch_embeddings_for_search_phrases(search_phrases):

    log.info("getting openai embeddings")

    log.info("getting search phrases for {0} search_ids".format(len(search_phrases)))

    if len(search_phrases) < 5:
        log.info("search_phrases: {0}'"
                    .format('\n'.join([str(search_phrase) for search_phrase in search_phrases])))


    log.info("getting openai embeddings for {0} phrases".format(len(search_phrases)))
    embeddings = embed_api.get_embeddings_for_phrases(search_phrases)

    return embeddings

def fetch_embeddings_for_search_phrase(search_phrase):

    return fetch_embeddings_for_search_phrases([search_phrase])[0]