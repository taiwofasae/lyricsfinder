from embeddings import s3
from embeddings import file as file_embeddings
from embeddings import ondemand as embed_api
from common import songsearch, log
from lyricsproject import settings

if not settings.DEBUG:
    file_embeddings = s3


def api_version():
    return embed_api.API_VERSION
   
def get_embeddings_for_song(song_id):
    embedding = []

    log.info("loading embedding from file")

    embedding = file_embeddings.load_song_embedding(song_id)
    
    if not embedding:
        log.info("fetching embedding from api")
        embedding = fetch_embeddings_for_songs([song_id])[0]

    return embedding

def get_embeddings_for_songs(song_ids):
    return [get_embeddings_for_song(song_id) for song_id in song_ids]

def get_embeddings_for_search_phrase(search_id):

    log.info("loading embedding from file")
    embedding = file_embeddings.load_search_phrase_embedding(search_id)
    
    if not embedding:
        log.info("fetching embedding from api")
        embedding = fetch_embeddings_for_search_phrases([search_id])[0]

    return embedding

def get_song_details(song_ids):
    songs = []
    for song_id in song_ids:
        songs.append(songsearch.get_song(song_id))
    return [(song.id, song.title, song.lyrics) for song in songs]

def fetch_embeddings_for_song(song_id):

    return fetch_embeddings_for_songs([song_id])[0]

def fetch_embeddings_for_songs(song_ids):

    log.info("getting openai embeddings")

    log.info("getting song details for {0} song_ids".format(len(song_ids)))

    if len(song_ids) < 5:
        log.info("song_ids: {0}'"
                    .format(','.join([str(song_id) for song_id in song_ids])))

    songs = get_song_details(song_ids)

    log.info("making sure folder is accessible before calling api")
    file_embeddings.save_song_embedding(song_id=song_ids[0], embeddings=[])

    
    if len(song_ids) < 5:
        titles = [song[1] for song in songs]
        log.info("Titles: {0}".format('\n'.join(titles)))

    embeddings = embed_api.get_embeddings_for_phrases([song.lyrics for song in songs])[0]

    log.info("inserting/updating song embeddings")
    for song_id, e in zip(song_ids, embeddings):
        file_embeddings.save_song_embedding(song_id, e)

    return embeddings

def get_search_phrases(search_ids):
    searches = []
    for search_id in search_ids:
        searches.append(songsearch.get_search(search_id))
    return [search.search_phrase for search in searches]

    
def fetch_embeddings_for_search_phrases(search_ids):

    log.info("getting openai embeddings")

    log.info("getting search phrases for {0} search_ids".format(len(search_ids)))

    if len(search_ids) < 5:
        log.info("search_ids: {0}'"
                    .format(','.join([str(search_id) for search_id in search_ids])))

    searches = get_search_phrases(search_ids)

    log.info("making sure file location is writable before calling api")
    file_embeddings.save_search_phrase_embedding(search_ids[0], [])


    log.info("getting openai embeddings for {0} phrases".format(len(search_ids)))
    embeddings = embed_api.get_embeddings_for_phrases(searches)

    log.info("saving embeddings")
    for search_id, embed in zip(search_ids, embeddings):
        file_embeddings.save_search_phrase_embedding(search_id, embed)

    return embeddings

def fetch_embeddings_for_search_phrase(search_id):

    return fetch_embeddings_for_search_phrases([search_id])[0]
