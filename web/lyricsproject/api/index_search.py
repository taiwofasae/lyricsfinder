from semantic_search import search_helpers, linear_db
from embeddings import embeddings

settings = ['embeddings database', 'embeddings api']

def search(searchphrase):
    
    return index_search(searchphrase)


def index_search(searchphrase):
    
    song_ids, songs_embeddings = load_embedding_matrix()

    search_string_embedding = embeddings.get_embeddings_for_phrases([searchphrase])[0]


    scores = search_helpers.cosine_similarity_with_matrix(songs_embeddings, search_string_embedding)


    song_ids, scores = linear_db._extract_top_n_scores(song_ids, scores, n=10)

    return [(id, score) for id, score in zip(song_ids, scores)]



def load_index():
    pass

