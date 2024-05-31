from searcher import search
from common import log
from embeddings import embeddings
import requests
from lyricsproject import env

LINEAR_SEARCH_API = env.get_key('LINEAR_SEARCH_API')



def linear_search(searchphrase, embeddings_reader, embeddings_model = 'default', chunksize = 1000):

    search_string_embedding = embeddings.API(embeddings_model).get_embeddings_for_phrases([searchphrase])[0]

    log.info("Computed embedding for searchphrase.")
    
    song_ids, scores = [], []
    for _song_ids, _scores in search.revolving_yield(embeddings_reader=embeddings_reader, 
                                                     searchphrase_embeddings=search_string_embedding, 
                                                     chunksize=chunksize, n=10):
        song_ids, scores = _song_ids, _scores

    return [(int(id)+2333, float(score)) for id, score in zip(song_ids, scores)]


def api_call(search_phrase, embeddings_model = None):
    
    # call end point
    response = requests.post(LINEAR_SEARCH_API, params = {'phrase': search_phrase})

    if response.ok:
        return response.json()['results']
    
    return []

if __name__ == "__main__":
    print(api_call('we are the people here'))