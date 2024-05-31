from common import file, log, s3
import pandas as pd
import os
import string, random

maps = {
    'default': 's3://embeds/random.csv',
    'random': 'file://song_embeddings/random.csv',
    'openai': 's3://song_embeddings/openai.csv',
    'prefix': 's3://song_embeddings/{}.csv'
}

def selector_fn(model_name = 'default'):
    
    if model_name in maps:
        model_name = selector_fn[model_name]

    protocol, filepath = extract_file_protocol(model_name)
    
    if protocol == 'file':
        return PandasFileReader(filepath=filepath).reader
    elif protocol == 's3':
        return S3FileReader(filepath=filepath).reader
    else: # if no protocol, assume file in folder
        return S3FileReader(filepath=maps['prefix'].format(filepath)).reader
    
def extract_file_protocol(filepath):
    protocol = None
    
    splits = filepath.split('://')
    if len(splits) > 1:
        protocol = splits[0].lower()
        filepath = splits[1]

    return protocol, filepath
        
    


class EmbeddingsFileReader:
    def __init__(self) -> None:
        pass

    def cleanup(self):
        pass

class InMemoryFileReader(EmbeddingsFileReader):

    def __init__(self, file_reader, *args, **kwargs) -> None:
        super(InMemoryFileReader, self).__init__(*args, **kwargs)

        self.data = None
        self.file_reader = file_reader

    def _load_file(self):
        if not self.data:
            log.info("Loading file into memory")
            song_ids, song_embeddings = next(self.file_reader(chunksize=100000))

            self.data = (song_ids, song_embeddings)
            

        return self

    def reader(self, chunksize=100000):

        return [self._load_file().data]

class PandasFileReader(EmbeddingsFileReader):

    def __init__(self, filepath, *args, **kwargs) -> None:
        super(PandasFileReader, self).__init__(*args, **kwargs)

        self.filepath = file.get_full_path(filepath)

        if not file.file_exists(self.filepath):
            raise FileNotFoundError(self.filepath) 

    def reader(self, chunksize=1000):
        log.info("reading pandas dataframe from {}".format(self.filepath))
        with pd.read_csv(self.filepath, chunksize=chunksize) as reader:
            for chunk in reader:

                yield chunk['song_id'].values, chunk['embeddings'].apply(eval).tolist()

class S3FileReader(EmbeddingsFileReader):
    temp_folder = 's3/'
    temp_filepath = 's3/tmp_embeddings.csv'
    #''.join(random.choice(string.ascii_uppercase) for _ in range(25)) + '.csv'
    def __init__(self, filepath, *args, **kwargs) -> None:
        super(S3FileReader, self).__init__(*args, **kwargs)

        # make directory
        
        self.temp_filepath = file.get_full_path(S3FileReader.temp_filepath)
        S3FileReader.make_temp_directory(self.temp_filepath)

        # download file from s3
        s3.download_file_to(src_file_name=filepath, dest_file_name=self.temp_filepath)

        self.file_reader = PandasFileReader(self.temp_filepath, *args, **kwargs).reader

    def reader(self, chunksize=1000):
        return self.file_reader(chunksize=chunksize)
    
    def make_temp_directory(filepath):
        full_path = os.path.join(S3FileReader.temp_folder, filepath)

        dir_path = os.path.dirname(full_path)
        file.make_directory(dir_path)
        log.info("temporary directory made: '{}'".format(dir_path))

def _file_read_csv(skiprows=0, take=1000):

    filepath = file.get_full_path('embeddings_file.csv')

    df = pd.read_csv(filepath, skiprows=skiprows, nrows=take)

    song_ids = df['song_id']
    song_embeddings = df['embeddings']

    return song_ids, song_embeddings
