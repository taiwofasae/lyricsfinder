from searcher import search_helpers, searcher
from common import log
from embeddings import embeddings



def linear_search(searchphrase, embeddings_reader, embeddings_model = 'default', chunksize = 1000):

    search_string_embedding = embeddings.API(embeddings_model).get_embeddings_for_phrases([searchphrase])[0]

    log.info("Computed embedding for searchphrase.")
    
    song_ids, scores = [], []
    for _song_ids, _scores in searcher.revolving_yield(embeddings_reader=embeddings_reader, 
                                                     searchphrase_embeddings=search_string_embedding, 
                                                     chunksize=chunksize, n=10):
        song_ids, scores = _song_ids, _scores

    return [(int(id), float(score)) for id, score in zip(song_ids, scores)]


def api_call(search_phrase, embeddings_model = None):
    pass
    # call end point

    # return result