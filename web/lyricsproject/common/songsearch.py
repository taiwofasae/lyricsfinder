from common import database, log, models, embeddings
import datetime
from searcher import linear_db
import uuid

def ping_db():
    return database.ping()

def execute_pending_search_phrases():
    for search_id in get_pending_searches():
        execute_search(search_id)

def execute_undone_search_phrases():
    for search_id in get_undone_searches():
        execute_search(search_id)

def search_on_demand(search_phrase):
    song_ids, sim_scores = linear_db.top_10_similarity_scores_by_search_phrase(search_phrase)

    output = []
    for id, score in zip(song_ids, sim_scores):
        song = get_song(id).serialize_to_json()
        song['sim_score'] = score
        output.append(song)

    return output

def execute_revolving_search(search_id):

    _execute_search(search_id, _revolving_search)

def _revolving_search(search_id):
    batch_size = 1000
    for batch_no, song_ids, scores in linear_db.top_10_similarity_scores_yield(search_id, batch_size = batch_size):
        log.info("Batch {}/{}".format(batch_no, batch_size))
        bulk_update_songsearch(search_id, song_ids, scores)

    log.info("Revolving search done in {} batches".format(batch_size))
        

def execute_search(search_id):

    _execute_search(search_id, _search)

def _search(search_id):
    
    song_ids, sim_scores = linear_db.top_10_similarity_scores(search_id)

    log.info("inserting into db")
    bulk_update_songsearch(search_id, song_ids, sim_scores)



def _execute_search(search_id, delegate = None):

    if isinstance(search_id, uuid.UUID):
        search_id = search_id.hex
    
    # get search
    search = get_search(search_id)

    if not search:
        log.error("search phrase not found")
        return

    # update search status to RUNNING
    log.info("updating search status for phrase: '{0}'; id: {1} to RUNNING"
                 .format(search.search_phrase, search_id))

    update_search(search_id, api_version=embeddings.api_version(), status=models.Search.STATUS.RUNNING)
    

    if delegate:
        delegate(search_id)


    log.info("updating search status for phrase: '{0}'; id: {1} to DONE"
                 .format(search.search_phrase, search_id))
    
    # update search status to DONE
    update_search(search_id, api_version=embeddings.api_version(), status=models.Search.STATUS.DONE)


## SONG SEARCH

def get_pending_searches():
    results = database.fetch(models.Search.MysqlCommands.get_pending())

    return [id for id, phrase in results]

def get_undone_searches():
    results = database.fetch(models.Search.MysqlCommands.get_undone())

    return [id for id, phrase in results]

def insert_songsearch(song_id, search_id, similarity_score):

    significant = 0

    database.execute(models.SongSearch.MysqlCommands.insert(song_id, search_id, similarity_score, significant))

def insert_songsearches_by_search_id(search_id, song_ids, similarity_scores):
    
    for (song_id, similarity_score) in zip(song_ids, similarity_scores):
        insert_songsearch(song_id, search_id, similarity_score)
        
def bulk_insert_songsearch(song_ids, search_id, similarity_scores):
    database.execute(models.SongSearch.MysqlCommands.bulk_insert(song_ids, [search_id for id in song_ids],
                                                                 similarity_scores, 
                                                                 [0 for id in song_ids]))
    
def _bulk_delete_songsearch(search_id, song_ids = None, delete_all = False):
    if song_ids:
        [database.execute(models.SongSearch.MysqlCommands.delete(song_id, search_id)) for song_id in song_ids]
    else:
        if delete_all:
            database.execute(models.SongSearch.MysqlCommands.bulk_delete(search_id))

def update_songsearch(song_id, search_id, similarity_score):
    database.execute(models.SongSearch.MysqlCommands.update(song_id, search_id, similarity_score, significant=0))

def bulk_update_songsearch(search_id, song_ids, similarity_scores):
    stale_song_ids, stale_scores = get_scores_for_song_id_range(search_id, min(song_ids), max(song_ids))

    new_song_ids = []
    new_scores = []
    updating = []
    for song_id, score in zip(song_ids, similarity_scores):
        if song_id in stale_song_ids:
            # update
            updating.append(song_id)
            update_songsearch(song_id, search_id, score)
            stale_song_ids.pop(song_id)
        else:
            # insert
            new_song_ids.append(song_id)
            new_scores.append(score)

    bulk_insert_songsearch(new_song_ids, search_id, new_scores)
    # delete stale. Thread safe
    _bulk_delete_songsearch(search_id, stale_song_ids)
    

    

## SEARCH

def get_search(search_id):
    if isinstance(search_id, uuid.UUID):
        search_id = search_id.hex
    results = database.fetch(models.Search.MysqlCommands.get_search(search_id))
    
    if results:
        (search_phrase, api_version, done_timestamp, status) = results[0]


        return models.Search(search_id,
            search_phrase,
            api_version,
            done_timestamp,
            status)

    return None

def update_search(search_id, api_version, status):

    done_timestamp = None
    if status == models.Search.STATUS.DONE:
        done_timestamp = datetime.datetime.now()
    

    database.execute(models.Search.MysqlCommands.update_search(search_id, api_version, status, done_timestamp))

def get_songs_for_search(search_id, page_no=0, batch_size = 10):

    offset = page_no * batch_size
    limit = batch_size

    results = database.fetch(models.Search.MysqlCommands.get_songs(search_id, offset, limit))
    

    return [models.SongSearch(song_id=None, search_id=search_id, artist=artist, 
                              title=title, lyrics=lyrics, char_length=char_length,
                              sim_score=sim_score) 
            for (title, artist, lyrics, char_length, sim_score) in results]

def get_scores_for_searchs(search_id, page_no=0, batch_size = 10):

    offset = page_no * batch_size
    limit = batch_size

    results = database.fetch(models.Search.MysqlCommands.get_scores(search_id, offset, limit))
    
    song_ids = [_[0] for _ in results]
    scores = [_[1] for _ in results]
    return song_ids, scores

def get_scores_for_song_id_range(search_id, start_id, end_id):

    results = database.fetch(models.Search.MysqlCommands.get_scores_by_song_id_range(search_id, start_id, end_id))
    
    song_ids = [_[0] for _ in results]
    scores = [_[1] for _ in results]
    return song_ids, scores


# SONGS

def get_num_songs(offset_id = 0):
    results = database.fetch(models.Song.MysqlCommands.get_num_songs(offset_id))

    return results[0][0]



def get_songs(offset_id = 0, page_no=0, batch_size = 10):

    offset = page_no * batch_size
    limit = batch_size

    results = database.fetch(models.Song.MysqlCommands.get_songs(offset_id, offset, limit))
    

    return [models.Song(id, artist=artist, title=title) 
            for (id, artist, title) in results]

def get_song(song_id):

    results = database.fetch(models.Song.MysqlCommands.get_song(song_id))
    
    return [models.Song(id, artist=artist, title=title, lyrics=lyrics) 
            for (id, artist, title, lyrics) in results][0]
