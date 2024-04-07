
class Song:
    def __init__(self, song_id, title = "", lyrics = "") -> None:
        self.song_id = song_id
        self.title = title
        self.lyrics = lyrics

    def get_short_lyrics(self):
        return self.lyrics[0:100]

    def __str__(self) -> str:
        return f"song_id: {self.song_id}, title: {self.title}, lyrics: {self.get_short_lyrics()}"

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
    

class SongEmbedding:
    def __init__(self, song_id, song_title, serialized_embeddings) -> None:
        self.song_id = song_id
        self.song_title = song_title
        self.serialized_json = serialized_embeddings

        

class PhraseEmbedding:
    def __init__(self, phrase, serialized_embeddings) -> None:
        self.phrase = phrase
        self.serialized_json = serialized_embeddings