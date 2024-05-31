import numpy as np
from embeddings import embeddings
from searcher import search_helpers


class Indexing:
    def __init__(self, keys = None, embeddings = None) -> None:
        self._index_table = {}
        self._keys = keys
        self._embeddings = embeddings


    def build(self):
        pass

    def _search_knn(self, v, n):
        pass

    def knn(self, v, n=10):
        return self._search_knn(v, n)
    

nms_lib_index = Indexing()

def top_10_similarity_scores(search_id):
    
    return top_n_similarity_scores(search_id, n=10)


def top_n_similarity_scores(search_id, n=10):
    
    search_string_embedding = embeddings.get_embeddings_for_search_phrase(search_id)

    song_ids, scores = nms_lib_index.knn(search_string_embedding, n=n)

    return song_ids.tolist(), round(search_helpers.SCALE * scores, 2).tolist()
