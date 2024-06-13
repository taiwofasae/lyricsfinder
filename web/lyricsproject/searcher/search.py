from searcher import search_helpers
from common import log



def revolving_yield(embeddings_reader, searchphrase_embeddings, chunksize = 1000, n=10):
    
    song_ids = []
    scores = []
    for _song_ids, _scores in _yield(embeddings_reader, searchphrase_embeddings, chunksize = chunksize):
        song_ids.extend(_song_ids)
        scores.extend(_scores)

        log.debug("len(song_ids): {}".format(len(song_ids)))
        log.debug("len(scores): {}".format(len(scores)))
        log.debug("len(_song_ids): {}".format(len(_song_ids)))
        log.debug("len(_scores): {}".format(len(_scores)))

        # only keep top n scores
        song_ids, scores = search_helpers.extract_top_n_scores(song_ids, scores, n=n)

        log.debug("top n scores: {}".format(scores))
        log.debug("top n song_ids: {}".format(song_ids))

        yield song_ids, scores


def _yield(embeddings_reader, searchphrase_embeddings, chunksize = 1000):
    
    for song_ids, songs_embeddings in embeddings_reader(chunksize=chunksize):
        
        log.debug("len(songs_embeddings): {}".format(len(songs_embeddings)))
        log.debug("len(songs_embeddings[0]): {}".format(len(songs_embeddings[0])))
        log.debug("len(searchphrase_embeddings): {}".format(len(searchphrase_embeddings)))

        scores = search_helpers.cosine_similarity_with_matrix(songs_embeddings, searchphrase_embeddings)[0]

        yield song_ids, scores