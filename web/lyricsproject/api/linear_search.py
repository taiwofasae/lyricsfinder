from searcher import linear_search, embeddings_filereader
from searcher.embeddings_filereader import InMemoryFileReader, PandasFileReader
from common import cleaning
from common.file_locator import FileLocator
from embeddings import embeddings
from fastapi import FastAPI, Query
from typing import Annotated
from lyricsproject import settings as project_settings
from lyricsproject import env

from logging.config import dictConfig
dictConfig(project_settings.LOGGING)

from common import log

app = FastAPI()


embeddings_model = env.get_key('EMBEDDINGS_MODEL') or 'random'
embeddings_model_path = env.get_key('EMBEDDINGS_MODEL_PATH') or 'file://song_embeddings/random.csv'
embeddings_file = env.get_key('EMBEDDINGS_FILE') or 'file://song_embeddings/random.csv'

log.info('embeddings model: {}'.format(embeddings_model))
log.info('embeddings model file: {}'.format(embeddings_model_path))
# load embeddings model
embeddings_model_file = FileLocator(embeddings_model_path, temp_path='MODEL').full_temp_path()
embeddings_fn = embeddings.selector_fn(embeddings_model, model_file=embeddings_model_file)


log.info('embeddings file: {}'.format(embeddings_file))
assert embeddings_file

# load embeddings into memory
inmemory_embeddings = InMemoryFileReader(file_reader=PandasFileReader(
    FileLocator(embeddings_file, temp_path='embeddings.csv').temp_source).reader)


@app.get('/tutorial/')
async def tutorial(query: Annotated[str | None, Query(max_length=100)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if query:
        results.update({"query": query})
    return results

@app.post('/')
async def root(phrase: Annotated[str, Query(min_length=5, max_length=100)] = None):
    
    if not phrase:
        raise ValueError('phrase can not be empty')
    
    results = search(searchphrase=phrase)

    return {"results": results, "model": embeddings_model}



def search(searchphrase):

    searchphrase = cleaning.clean_phrase(searchphrase)
    
    return linear_search.linear_search(searchphrase, 
                                       embeddings_reader=inmemory_embeddings.reader, 
                                       embeddings_model=embeddings_fn, chunksize = 10)