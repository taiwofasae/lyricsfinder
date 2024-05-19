from common import database, log, models
from embeddings import embeddings
import datetime
from semantic_search import linear_db, settings, nms_lib
import uuid

UPDATE_SCORES_EVERY_TIME = False

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

def execute_search_top10(search_id):

    _execute_search(search_id, _search_top10)


def execute_search_now(search_id):

    _execute_search(search_id, _search_now)


def execute_search(search_id):

    _execute_search(search_id, _search)

def _search_top10(search_id):
    
    song_ids, sim_scores = linear_db.top_10_similarity_scores(search_id)

    log.info("updating/inserting into db")
    update_or_insert_songsearches_by_search_id(search_id, song_ids, sim_scores)


def _search_now(search_id):
    
    song_ids, sim_scores = nms_lib.top_10_similarity_scores(search_id)

    log.info("updating/inserting into db")
    update_or_insert_songsearches_by_search_id(search_id, song_ids, sim_scores)

def _search(search_id):

    for (batch_no, song_ids, sim_scores, new_song_ids, new_sim_scores) in linear_db.similarity_scores_by_search_id(search_id):
        log.info("successfully fetched songs for batch no: {0}".format(batch_no))
        log.info("updating/inserting into db")

        if UPDATE_SCORES_EVERY_TIME:
            update_or_insert_songsearches_by_search_id(search_id, song_ids, sim_scores)
        else:
            update_or_insert_songsearches_by_search_id(search_id, new_song_ids, new_sim_scores)

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

def get_first_todo_song(search_id):
    results = database.fetch(models.SongSearch.MysqlCommands.get_first_unexecuted(search_id))
    
    return results and results[0] and results[0][0]

def update_or_insert_songsearch(song_id, search_id, similarity_score):

    significant = 1 if similarity_score > settings.SIMILARITY_SCORE_THRESHOLD else 0

    try:
        database.execute(models.SongSearch.MysqlCommands.insert(song_id, search_id, similarity_score, significant))
    except:
        pass
    finally:
        database.execute(models.SongSearch.MysqlCommands.update(song_id, search_id, similarity_score, significant))

def update_or_insert_songsearches_by_search_id(search_id, song_ids, similarity_scores):
    
    for (song_id, similarity_score) in zip(song_ids, similarity_scores):
        update_or_insert_songsearch(song_id, search_id, similarity_score)

def insert_songsearches_by_search_id(search_id, song_ids, similarity_scores):

    for (song_id, similarity_score) in zip(song_ids, similarity_scores):
        update_or_insert_songsearch(song_id, search_id, similarity_score)
        

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
    

    return [models.SongSearch(song_id=None, search_id=search_id, 
                              title=title, lyrics=lyrics, char_length=char_length,
                              sim_score=sim_score) 
            for (title, lyrics, char_length, sim_score) in results]

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
    

    return [models.Song(id, title=title) 
            for (id, title) in results]

def get_song(song_id):

    results = database.fetch(models.Song.MysqlCommands.get_song(song_id))
    
    return [models.Song(id, title=title, lyrics=lyrics) 
            for (id, title, lyrics) in results][0]
