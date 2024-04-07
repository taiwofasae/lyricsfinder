import database
import settings
import embeddings
import models
import logging
import datetime

def ping_db():
    return database.ping()

def execute_search(search_id):

    
    # get search
    search = get_search(search_id)

    # update search status to RUNNING
    logging.info("updating search status for phrase: '{0}'; id: {1} to RUNNING"
                 .format(search.search_phrase, search_id))

    update_search(search_id, api_version=embeddings.api_version(), status=models.Search.STATUS.RUNNING)
    

    num_songs = get_num_songs()
    num_songs_batch = 10

    start_song_id = 0;get_first_todo_song(search_id)

    logging.info("songs search starting at id: {0}".format(start_song_id))


    
    
    for start in range(0, (num_songs // num_songs_batch) + 1):
        
        logging.info("batch no: {0}; batch size: {1}".format(start, num_songs_batch))

        batch = get_songs(offset_id=start_song_id, page_no=start, batch_size=num_songs_batch)

        logging.info("successfully fetched songs for batch no: {0}".format(start))

        for song in batch:
            # execute similarity score between search phrase and song
            score = embeddings.similarity_score(search.search_phrase, song.song_id)

            logging.info("successfully computed score for song id: {0}; title: {1}  ".format(song.song_id, song.title))

            # update/insert similarity score into database
            update_or_insert_songsearch(song.song_id, search_id, score)

            logging.info("score updated or inserted")


    logging.info("updating search status for phrase: '{0}'; id: {1} to DONE"
                 .format(search.search_phrase, search_id))
    
    # update search status to DONE
    update_search(search_id, api_version=embeddings.api_version(), status=models.Search.STATUS.DONE)


## SONG SEARCH

def get_first_todo_song(search_id):
    results = database.fetch("""
    SELECT song_id FROM lyricsapp_songsearch WHERE search_id = '{0}' 
                             ORDER BY song_id desc
                             LIMIT 1;
""".format(search_id))
    
    return results and results[0] and results[0][0]

def update_or_insert_songsearch(song_id, search_id, similarity_score):

    significant = 1 if similarity_score > settings.SIMILARITY_SCORE_THRESHOLD else 0

    try:
        database.execute("""
                INSERT INTO lyricsapp_songsearch (song_id, search_id, sim_score, significant, created_on) VALUES ({0},'{1}',{2},{3},{4});
            """.format(song_id, search_id, similarity_score, significant, database.to_db_time_format_str(datetime.datetime.now())))
    except:
        pass
    else:
        database.execute("""
                UPDATE lyricsapp_songsearch SET sim_score = {2}, significant = {3} WHERE song_id = {0} and search_id = '{1}';
            """.format(song_id, search_id, similarity_score, significant))
        

## SEARCH

def get_search(search_id):
    results = database.fetch("""
    SELECT phrase, api_version, done_timestamp, status FROM lyricsapp_search WHERE BINARY id = '{0}';
""".format(search_id))
    
    (search_phrase, api_version, done_timestamp, status) = results[0]


    return models.Search(id,
        search_phrase,
        api_version,
        done_timestamp,
        status)

def update_search(search_id, api_version, status):

    done_timestamp = None
    if status == models.Search.STATUS.DONE:
        done_timestamp = datetime.datetime.now()
    

    database.execute("""
            UPDATE lyricsapp_search SET api_version = '{1}', done_timestamp = {3}, status = '{2}' WHERE id = '{0}';
        """.format(search_id, api_version, status, database.to_db_time_format_str(done_timestamp) if done_timestamp else 'NULL'))


# SONGS

def get_num_songs(offset_id = 0):
    results = database.fetch("""
        SELECT COUNT(*) FROM lyricsapp_song WHERE id > {0};
    """.format(offset_id))

    return results[0][0]



def get_songs(offset_id = 0, page_no=0, batch_size = 10):

    offset = page_no * batch_size
    limit = batch_size

    results = database.fetch("""
    SELECT id, title FROM lyricsapp_song WHERE id > {0} limit {1} offset {2};
""".format(offset_id, limit, offset))
    

    return [models.Song(id, title=title) 
            for (id, title) in results]



if __name__ == "__main__":
    if ping_db():
        print("mysql database connection OK")
    else:
        print("mysql db unreachable :(")

#execute_search(('7f227f9b1cc14777b6ed35603b963c5c'))
