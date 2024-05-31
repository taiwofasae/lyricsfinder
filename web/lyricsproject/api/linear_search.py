from searcher import linear_search, embeddings_filereader
from common import cleaning, file
from fastapi import FastAPI, Query
from typing import Annotated
from lyricsproject import settings as project_settings
from lyricsproject import env

from logging.config import dictConfig
dictConfig(project_settings.LOGGING)
from common import log

app = FastAPI()


embeddings_model = env.get_key('EMBEDDINGS_MODEL') or 'random'
embeddings_file = env.get_key('EMBEDDINGS_FILE')
log.info('embeddings file: {}'.format(embeddings_file))
log.info('embeddings model: {}'.format(embeddings_model))
if embeddings_file:
    file_reader = embeddings_filereader.selector_fn(embeddings_file)
else:
    file_reader = embeddings_filereader.selector_fn('file://song_embeddings/random.csv')
    if not project_settings.DEBUG:
        file_reader = embeddings_filereader.selector_fn('s3://embeds/song_embeddings/random.csv')


inmemory_embeddings = embeddings_filereader.InMemoryFileReader(file_reader)


@app.get('/tutorial/')
async def tutorial(query: Annotated[str | None, Query(max_length=100)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if query:
        results.update({"query": query})
    return results

@app.post('/')
async def root(phrase: Annotated[str, Query(min_length=10, max_length=100)] = None):
    
    if not phrase:
        raise ValueError('phrase can not be empty')
    
    results = search(searchphrase=phrase)

    print(results)

    return {"results": results, "model": embeddings_model}



def search(searchphrase):

    searchphrase = cleaning.clean_phrase(searchphrase)
    
    return linear_search.linear_search(searchphrase, 
                                       embeddings_reader=inmemory_embeddings.reader, 
                                       embeddings_model=embeddings_model, chunksize = 10)