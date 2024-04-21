import numpy as np
from . import embeddings
import logging

def cosine_similarity(a, b):
    score = 5 * np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return round(score, 1)

def similarity_scores(search_id, song_ids):

    search_string_embedding = embeddings.get_embeddings_for_search_phrase(search_id)
    

    songs_embedding = [embeddings.get_embeddings_for_song(id) for id in song_ids]

    scores = [cosine_similarity(x, search_string_embedding) for x in songs_embedding]

    return scores

def similarity_score(search_id, song_id):

    search_string_embedding = embeddings.get_embeddings_for_search_phrase(search_id)
    logging.info("search string embedding[:5]: {0}".format(search_string_embedding[:5]))

    song_embedding = embeddings.get_embeddings_for_song(song_id)
    logging.info("song embedding[:5]: {0}".format(song_embedding[:5]))

    return cosine_similarity(search_string_embedding, song_embedding)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

#print(similarity_scores('5b126c1c494f4be19f96b541d1cffb6f', [1, 2, 3]))