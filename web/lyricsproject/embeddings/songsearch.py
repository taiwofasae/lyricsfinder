from . import database
from . import settings
from . import embeddings
from . import models
import logging
import datetime
from . import similarity

def ping_db():
    return database.ping()

def execute_pending_search_phrases():
    for search_id in get_pending_searches():
        execute_search(search_id)

def execute_search(search_id):

    
    # get search
    search = get_search(search_id)

    if not search:
        logging.error("search phrase not found")
        return

    # update search status to RUNNING
    logging.info("updating search status for phrase: '{0}'; id: {1} to RUNNING"
                 .format(search.search_phrase, search_id))

    update_search(search_id, api_version=embeddings.api_version(), status=models.Search.STATUS.RUNNING)
    

    num_songs = get_num_songs()
    num_songs_batch = 10

    start_song_id = get_first_todo_song(search_id) or 0

    logging.info("songs search starting at id: {0}".format(start_song_id))


    
    
    for start in range(0, (num_songs // num_songs_batch) + 1):
        
        logging.info("batch no: {0}; batch size: {1}".format(start, num_songs_batch))

        batch = get_songs(offset_id=start_song_id, page_no=start, batch_size=num_songs_batch)

        logging.info("successfully fetched songs for batch no: {0}".format(start))

        for song in batch:
            # execute similarity score between search phrase and song
            score = similarity.similarity_score(search.id, song.song_id)

            logging.info("successfully computed score for song id: {0}; title: {1}  ".format(song.song_id, song.title))

            # update/insert similarity score into database
            update_or_insert_songsearch(song.song_id, search_id, score)

            logging.info("score updated or inserted")


    logging.info("updating search status for phrase: '{0}'; id: {1} to DONE"
                 .format(search.search_phrase, search_id))
    
    # update search status to DONE
    update_search(search_id, api_version=embeddings.api_version(), status=models.Search.STATUS.DONE)


## SONG SEARCH

def get_pending_searches():
    results = database.fetch(models.Search.MysqlCommands.get_pending())

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
    else:
        database.execute(models.SongSearch.MysqlCommands.update(song_id, search_id, similarity_score, significant))
        

## SEARCH

def get_search(search_id):
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



if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    if ping_db():
        print("mysql database connection OK")
    else:
        print("mysql db unreachable :(")

#execute_search(('7f227f9b1cc14777b6ed35603b963c5c'))
