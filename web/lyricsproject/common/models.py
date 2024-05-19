from common import database
import datetime

class Song:
    def __init__(self, song_id, title = "", lyrics = "") -> None:
        self.song_id = song_id
        self.title = title
        self.lyrics = lyrics

    def get_short_lyrics(self):
        return self.lyrics[0:100]

    def __str__(self) -> str:
        return f"song_id: {self.song_id}, title: {self.title}, lyrics: {self.get_short_lyrics()}"
    
    def serialize_to_json(self):
        return {
            'title': self.title,
            'lyrics': self.lyrics,
        }
    
    class MysqlCommands:
        table_properties = {
            'id': 'int PRIMARY KEY auto_increment',
            'title': 'varchar(50) unique NOT NULL',
            'lyrics': 'longtext NOT NULL',
            'char_length': 'int',
            'created_on': 'datetime(6) NOT NULL',
        }
        table_name = 'lyricsapp_song'
        
        def get_num_songs(offset_id = 0):
            return """
        SELECT COUNT(*) FROM lyricsapp_song WHERE id > {0};
    """.format(offset_id)
        
        def get_songs(offset_id = 0, offset=0, limit = 10):
            return """
    SELECT id, title FROM lyricsapp_song WHERE id > {0} limit {1} offset {2};
""".format(offset_id, limit, offset)
        
        def get_song(song_id):
            return """
    SELECT id, title, lyrics from lyricsapp_song where id = '{0}';
""".format(song_id)

class Search:
    def __init__(self, id, search_phrase, api_version, done_timestamp,status) -> None:
        self.id = id
        self.search_phrase = search_phrase
        self.api_version = api_version
        self.done_timestamp = done_timestamp
        self.status = status

    class STATUS:
        PENDING = 'PENDING'
        RUNNING = 'RUNNING'
        DONE = 'DONE'


    def __str__(self) -> str:
        return f"""id: {self.id}, search_phrase: {self.search_phrase}, api_version: {self.api_version}, done_timestamp: {self.done_timestamp}, status: {self.status}"""
    
    class MysqlCommands:
        table_properties = {
            'id': 'char(32) PRIMARY KEY',
            'phrase': 'varchar(50) UNIQUE NOT NULL',
            'api_version': 'varchar(20) NOT NULL',
            'done_timestamp': 'datetime(6)',
            'status': 'varchar(10) NOT NULL',
            'created_on': 'datetime(6) NOT NULL'
        }
        table_name = 'lyricsapp_search'

        def get_search(search_id):
            return """
    SELECT phrase, api_version, done_timestamp, status FROM lyricsapp_search WHERE BINARY id = '{0}';
""".format(search_id)
        
        def get_pending():
            return "SELECT id, phrase FROM lyricsapp_search WHERE status = 'PENDING';"
        
        def get_undone():
            return "SELECT id, phrase FROM lyricsapp_search WHERE status != 'DONE';"
        
        def update_search(search_id, api_version, status, done_timestamp):
            return """
            UPDATE lyricsapp_search SET api_version = '{1}', done_timestamp = {3}, status = '{2}' WHERE id = '{0}';
        """.format(search_id, api_version, status, database.to_db_time_format_str(done_timestamp) if done_timestamp else 'NULL')

        def get_songs(search_id, offset=0, limit = 10):
            return """
            SELECT title, lyrics, char_length, sim_score FROM lyricsapp_song 
            INNER JOIN lyricsapp_songsearch ON lyricsapp_song.id = lyricsapp_songsearch.song_id
            WHERE search_id = '{0}' ORDER BY sim_score desc
            limit {1} offset {2};
        """.format(search_id, limit, offset)

        def get_scores(search_id, offset=0, limit = 10):
            return """
            SELECT  song.id, sim_score FROM lyricsapp_song as song
            INNER JOIN lyricsapp_songsearch as search 
            ON song.id = search.song_id
            WHERE search_id = '{0}' ORDER BY sim_score desc
            limit {1} offset {2};
        """.format(search_id, limit, offset)

        def get_scores_by_song_id_range(search_id, start_song_id, end_song_id):
            return """
            SELECT  song.id, sim_score FROM lyricsapp_song as song
            LEFT JOIN lyricsapp_songsearch as search 
            ON song.id = search.song_id
            WHERE search_id = '{0}' and song.id >= {1} and song.id <= {2}
            ORDER BY song.id asc;
        """.format(search_id, start_song_id, end_song_id)
    
class SongSearch:

    def __init__(self, song_id, search_id, title, lyrics, char_length, sim_score) -> None:
        self.song_id = song_id
        self.search_id = search_id
        self.title = title
        self.lyrics = lyrics
        self.char_length = char_length
        self.sim_score = sim_score

    def serialize_to_json(self):
        return {
            'title': self.title,
            'lyrics': self.lyrics,
            'char_length': self.char_length,
            'sim_score': self.sim_score
        }

    class MysqlCommands:
        table_properties = {
            'id': 'bigint PRIMARY auto_increment',
            'significant': 'tinyint(1) NOT NULL',
            'sim_score': 'double NOT NULL',
            'search_id': 'char(32) NOT NULL',
            'song_id': 'int NOT NULL',
            'created_on': 'datetime(6) NOT NULL'
        }
        table_name = 'lyricsapp_songsearch'

        def get_first_unexecuted(search_id):
            return """
    SELECT song_id FROM lyricsapp_songsearch WHERE search_id = '{0}' 
                             ORDER BY song_id desc
                             LIMIT 1;
""".format(search_id)
        
        def insert(song_id, search_id, similarity_score, significant):
            return """
                INSERT INTO lyricsapp_songsearch (song_id, search_id, sim_score, significant, created_on) VALUES ({0},'{1}',{2},{3},{4});
            """.format(song_id, search_id, similarity_score, significant, database.to_db_time_format_str(datetime.datetime.now()))

        def update(song_id, search_id, similarity_score, significant):
            return """
                UPDATE lyricsapp_songsearch SET sim_score = {2}, significant = {3} WHERE song_id = {0} and search_id = '{1}';
            """.format(song_id, search_id, similarity_score, significant)
