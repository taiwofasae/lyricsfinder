from embeddings import embeddings
from semantic_search import search_helpers
from common import songsearch, log

def top_10_similarity_scores(search_id):
    scores = []
    song_ids = []

    for (_, _song_ids, _scores) in similarity_scores_by_search_id(search_id, batch_size=1000):
        _song_ids, _scores = extract_top_n_scores(_song_ids, _scores, n=10)
        scores.extend(_scores)
        song_ids.extend(_song_ids)

    return extract_top_n_scores(song_ids, scores, n=10)

def extract_top_n_scores(song_ids, scores, n=10):
    if len(song_ids) != len(scores):
        raise ValueError('len(song_ids) != len(scores)')
    
    idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]

    return [song_ids[i] for i in idx], [scores[i] for i in idx]

def similarity_scores_by_search_id(search_id, batch_size = 10):

    num_songs = songsearch.get_num_songs()
    batches = (num_songs + batch_size - 1) // batch_size

    
    for batch_id in range(0, batches):

        batch_no = batch_id + 1

        song_ids, scores, new_song_ids, new_scores = similarity_scores_for_song_ids_range(search_id, page_no=batch_id, batch_size=batch_size)

        yield (batch_no, song_ids, scores, new_song_ids, new_scores)

def similarity_scores_for_song_ids_range(search_id, page_no=0, batch_size=10):

    song_ids = [song.song_id for song in songsearch.get_songs(page_no=page_no, batch_size=batch_size)]

    _song_ids, _scores = songsearch.get_scores_for_song_id_range(search_id, song_ids[0], song_ids[-1])

    # build map of song_ids -> score, keep existing scores
    song_id_map = {}
    for id, score in zip(_song_ids, _scores):
        song_id_map[id] = score


    null_song_ids = [song_id for song_id in song_ids if song_id not in _song_ids]

    # compute similarity score
    null_scores = similarity_scores(search_id, null_song_ids)

    for id, score in zip(null_song_ids, null_scores):
        song_id_map[id] = score

    scores = [song_id_map[id] for id in song_id_map]

    return song_ids, scores, null_song_ids, null_scores

def similarity_scores(search_id, song_ids):

    if not song_ids:
        return []

    search_string_embedding = embeddings.get_embeddings_for_search_phrase(search_id)
    
    songs_embedding = embeddings.get_embeddings_for_songs(song_ids)

    log.info("Songs_embedding: type:'{0}', length: {1}".format(type(songs_embedding), len(songs_embedding)))
    if len(songs_embedding) > 0:
        log.info("Songs embedding item at [0]: type:'{0}'".format(type(songs_embedding[0])))
        
    log.info("Search string embedding: type:'{0}', length: {1}".format(type(search_string_embedding), len(search_string_embedding)))
    if len(search_string_embedding) > 0:
        log.info("search string embedding item at [0]: type:'{0}'".format(type(search_string_embedding[0])))
    
    
    scores = search_helpers.cosine_similarity_with_matrix(songs_embedding, search_string_embedding)

    return scores[0].tolist()

def similarity_score(search_id, song_id):

    return similarity_scores(search_id, [song_id])[0]
