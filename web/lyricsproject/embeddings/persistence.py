import json
import os
import ast
from common import log, s3, file
from lyricsproject import settings


embeddings_folder = 'embeds/'
song_folder = os.path.join(embeddings_folder, 'song/')
phrase_folder = os.path.join(embeddings_folder, 'phrase/')
search_folder = os.path.join(embeddings_folder, 'search/')

status_file = os.path.join(embeddings_folder, 'song/status.txt')


class Storage:

    def __init__(self, storage_method = None):
        if not storage_method:
            storage_method = file if settings.DEBUG else s3

        self.method = storage_method

    def upload_file(self, file_name, json_dump):
        self.method.upload_file(file_name=file_name, json_dump=json_dump)

    def download_file(self, file_name, json_deserialize=True):
        return self.method.download_file(file_name=file_name, json_deserialize=json_deserialize)

    def save_song_embedding(self, song_id, embeddings):
        
        self.upload_file("{0}{1}.csv".format(song_folder, song_id), json.dumps(embeddings))
        self._update_status(song_id)

    def load_song_embedding(self, song_id):
        
        return self.download_file("{0}{1}.csv".format(song_folder, song_id)) or []

    def save_phrase_embedding(self, phrase_id, embeddings):
        
        self.upload_file("{0}{1}.csv".format(phrase_folder, phrase_id), json.dumps(embeddings))


    def load_phrase_embedding(self, phrase_id):
        
        return self.download_file("{0}{1}.csv".format(phrase_folder, phrase_id)) or []

    def save_search_phrase_embedding(self, search_id, embeddings):
        
        self.upload_file("{0}{1}.csv".format(search_folder, search_id), json.dumps(embeddings))

    def load_search_phrase_embedding(self, search_id):
        
        return self.download_file("{0}{1}.csv".format(search_folder, search_id)) or []

    ## status management

    def _load_status(self):
        log.info("loading status set")
        return ast.literal_eval(self.download_file(status_file, json_deserialize=False).decode('utf-8') or '') or set()

    def _save_status(self, status_set):
        log.info("saving status set")
        self.upload_file(status_file, str(status_set))


    def _update_status(self, song_id):
        status_set = self._load_status()
        if song_id not in status_set:
            status_set.add(song_id)
            self._save_status(status_set)

    def song_embedding_exists(self, song_id):
        try:
            status_set = self._load_status()
        except:
            self._save_status(set())
            status_set = self._load_status()

        if isinstance(song_id, list):
            return [id in status_set for id in song_id]
        
        return song_id in status_set

    def all_song_statuses(self):
        return self._load_status()