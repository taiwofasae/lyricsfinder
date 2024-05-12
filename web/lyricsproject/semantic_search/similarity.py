import numpy as np
from embeddings import embeddings
import logging
from semantic_search import search_helpers


def similarity_scores(search_id, song_ids):

    search_string_embedding = embeddings.get_embeddings_for_search_phrase(search_id)
    

    songs_embedding = [embeddings.get_embeddings_for_song(id) for id in song_ids]

    scores = [search_helpers.cosine_similarity(x, search_string_embedding) for x in songs_embedding]

    return scores

def similarity_score(search_id, song_id):

    search_string_embedding = embeddings.get_embeddings_for_search_phrase(search_id)
    logging.info("search string embedding[:5]: {0}".format(search_string_embedding[:5]))

    song_embedding = embeddings.get_embeddings_for_song(song_id)
    logging.info("song embedding[:5]: {0}".format(song_embedding[:5]))

    return search_helpers.cosine_similarity(search_string_embedding, song_embedding)
