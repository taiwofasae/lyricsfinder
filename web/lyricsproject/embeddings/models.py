from . import database
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

class SongEmbedding:
    def __init__(self, song_id, song_title, serialized_embeddings) -> None:
        self.song_id = song_id
        self.song_title = song_title
        self.serialized_json = serialized_embeddings

    class MysqlCommands:
        table_properties = {
            'song_id': 'int PRIMARY KEY',
            'song_title': 'varchar(50) NOT NULL',
            'serialized_embeddings': 'longtext',
        }
        table_name = 'lyricsapp_song_embeddings'

        def create_table():
            return """
    CREATE TABLE lyricsapp_song_embeddings (
                     song_id int PRIMARY KEY,
                     song_title varchar(50) NOT NULL,
                     serialized_embeddings longtext,
                     foreign key (song_id) references lyricsapp_song(id)
    );
"""
        def update_embedding(song_id, song_title, embeddings):
            return """
            UPDATE lyricsapp_song_embeddings SET song_title = '{1}', serialized_embeddings = '{2}' WHERE song_id = {0};;
        """.format(song_id, song_title, embeddings)
        
        def insert_embedding(song_id, song_title, embeddings):
            return """
    INSERT INTO lyricsapp_song_embeddings (song_id, song_title, serialized_embeddings) VALUES ({0},'{1}','{2}');
""".format(song_id, song_title, embeddings)
        
        def get_embedding(song_id):
            return """
    SELECT serialized_embeddings, song_title from lyricsapp_song_embeddings where song_id = {0};
""".format(song_id)
    
        

class PhraseEmbedding:
    def __init__(self, phrase, serialized_embeddings) -> None:
        self.phrase = phrase
        self.serialized_json = serialized_embeddings

    class MysqlCommands:

        def create_table():
            return """
    CREATE TABLE lyricsapp_phrase_embeddings (
                     id int(11) not null PRIMARY KEY auto_increment,
                     phrase varchar(50) NOT NULL,
                     serialized_embeddings longtext,
                     CONSTRAINT phrase_unique UNIQUE (phrase)
    );
"""

        def get_phrase_id_if_exists(phrase):
            return """
    SELECT id from lyricsapp_phrase_embeddings where phrase = "{0}";
""".format(phrase)
        
        def update_embedding(phrase, embeddings):
            return """
    UPDATE lyricsapp_phrase_embeddings SET serialized_embeddings = '{1}' WHERE phrase = '{0}';
""".format(phrase, embeddings)
        
        def insert_embedding(phrase, embeddings):
            return """
    INSERT INTO lyricsapp_phrase_embeddings (phrase, serialized_embeddings) VALUES ('{0}','{1}');
""".format(phrase, embeddings)
        
        def get_embedding(phrase):
            return """
    SELECT id, serialized_embeddings from lyricsapp_phrase_embeddings where phrase = '{0}';
""".format(phrase)


class SearchEmbedding:
    def __init__(self, search_id, phrase, serialized_embeddings) -> None:
        self.search_id = search_id
        self.phrase = phrase
        self.serialized_json = serialized_embeddings

    class MysqlCommands:

        def create_table():
            return """
    CREATE TABLE lyricsapp_search_embeddings (
                     search_id char(32) not null PRIMARY KEY,
                     phrase varchar(50) NOT NULL,
                     serialized_embeddings longtext,
                     CONSTRAINT phrase_unique UNIQUE (phrase)
    );
"""

        def update_embedding(search_id, embeddings):
            return """
    UPDATE lyricsapp_search_embeddings SET serialized_embeddings = '{1}' WHERE search_id = '{0}';
""".format(search_id, embeddings)
        
        def insert_embedding(search_id, phrase, embeddings):
            return """
    INSERT INTO lyricsapp_search_embeddings (search_id, phrase, serialized_embeddings) VALUES ('{0}','{1}', '{2}');
""".format(search_id, phrase, embeddings)
        
        def get_embedding(search_id):
            return """
    SELECT serialized_embeddings from lyricsapp_search_embeddings where search_id = '{0}';
""".format(search_id)
