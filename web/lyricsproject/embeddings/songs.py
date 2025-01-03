from embeddings import embeddings, persistence
from common import songsearch, log

def get_embeddings_for_song(song_id):
    return get_embeddings_for_songs([song_id])

def get_embeddings_for_songs(song_ids):
    embedding = [None for song_id in song_ids]

    if embeddings.PERSIST:
        log.info("loading embedding from file")
        for i in range(len(song_ids)):
            embedding[i] = persistence.Storage().load_song_embedding(song_ids[i])
    
    null_idx = [i for i in range(len(song_ids)) if not embedding[i]]

    if null_idx:
        null_ids = [song_ids[i] for i in null_idx]
        log.info("fetching embedding from api")
        null_embedding = fetch_embeddings_for_song_ids(null_ids)

        for j in range(len(null_idx)):
            i = null_idx[j]
            embedding[i] = null_embedding[j]

    return embedding


def get_song_details(song_ids):
    songs = []
    for song_id in song_ids:
        songs.append(songsearch.get_song(song_id))
    return [(song.song_id, song.artist, song.title, song.lyrics) for song in songs]

def fetch_embeddings_for_song_id(song_id):

    return fetch_embeddings_for_song_ids([song_id])[0]

def fetch_embeddings_for_song_ids(song_ids):
    """
    Fetches embeddings for each song or updates it
    """
    log.info("getting song details for {0} song_ids".format(len(song_ids)))

    if len(song_ids) < 5:
        log.info("song_ids: {0}'"
                    .format(','.join([str(song_id) for song_id in song_ids])))

    songs = [songsearch.get_song(song_id) for song_id in song_ids]

    return fetch_embeddings_for_songs(songs)

def fetch_embeddings_for_song(song):
    return fetch_embeddings_for_songs([song])[0]

def fetch_embeddings_for_songs(songs):
    """
    Fetches embeddings for each song or updates it
    """
    embeddings = []
    if songs and len(songs) > 0:
        if embeddings.PERSIST:
            log.info("making sure folder is accessible before calling api")
            persistence.Storage().save_song_embedding(song_id=songs[0].song_id, embeddings=[])

        
        if len(songs) < 5:
            titles = [song.title for song in songs]
            log.info("Titles: {0}".format('\n'.join(titles)))

        embeddings = embeddings.get_embeddings_for_phrases([song.lyrics for song in songs])

        if embeddings.PERSIST:
            log.info("inserting/updating song embeddings")
            for song_id, e in zip([song.song_id for song in songs], embeddings):
                persistence.Storage().save_song_embedding(song_id, e)

    return embeddings


def task_fetch_embeddings_for_all_songs(batch_size = 100):
    # fetch songs without embeddings

    if not embeddings.PERSIST:
        log.info("PERSIST not True. Skipping embeddings fetch.")
        return
    
    num_songs = songsearch.get_num_songs()
    batches = (num_songs + batch_size - 1) // batch_size

    existing_song_ids = persistence.Storage().all_song_statuses()

    
    for batch_id in range(0, batches):
        
        batch_no = batch_id + 1
        log.info("Fetching for batch {0}/{1}".format(batch_no, batches))

        songs = songsearch.get_songs(page_no=batch_id, batch_size=batch_size)
        song_ids = [song.song_id for song in songs]

        new_songs = [songsearch.get_song(song_id) for song_id in song_ids if song_id not in existing_song_ids]

        fetch_embeddings_for_songs(new_songs)

    log.info("Batch fetching done")