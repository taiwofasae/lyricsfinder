from embeddings import embeddings, songs as song_embeddings
from searcher import search_helpers
from common import songsearch, log


def song_ids_yield(batch_size = 1000):
    num_songs = songsearch.get_num_songs()
    batches = (num_songs + batch_size - 1) // batch_size

    
    for batch_id in range(0, batches):

        batch_no = batch_id + 1
        song_ids = [song.song_id for song in songsearch.get_songs(page_no=batch_id, batch_size=batch_size)]

        yield (batch_no, song_ids)


def _extract_top_n_scores(song_ids, scores, n=10):
    return search_helpers.extract_top_n_scores(song_ids=song_ids, scores=scores, n=n)


## By search phrase

def top_10_similarity_scores_by_search_phrase(search_phrase, batch_size = 1000):
    scores = []
    song_ids = []

    for (_, _song_ids, _scores) in top_10_similarity_scores_by_search_phrase_yield(search_phrase, batch_size=batch_size):
        # extract top 10 from all scores so far
        song_ids, scores = _song_ids, _scores

    return song_ids, scores

def top_10_similarity_scores_by_search_phrase_yield(search_phrase, batch_size = 1000):
    scores = []
    song_ids = []

    for (batch_no, _song_ids, _scores) in similarity_scores_by_search_phrase(search_phrase, batch_size=batch_size):
        _song_ids, _scores = _extract_top_n_scores(_song_ids, _scores, n=10)
        scores.extend(_scores)
        song_ids.extend(_song_ids)

        # extract top 10 from all scores so far
        _song_ids, _scores = _extract_top_n_scores(song_ids, scores, n=10)

        yield (batch_no, _song_ids, _scores)

    return _extract_top_n_scores(song_ids, scores, n=10)


def similarity_scores_by_search_phrase(search_phrase, batch_size = 10):

    for (batch_no, song_ids) in song_ids_yield(batch_size=batch_size):

        batch_id = batch_no - 1

        song_ids, scores = _compute_similarity_scores_for_song_ids_range_by_search_phrase(search_phrase, page_no=batch_id, batch_size=batch_size)

        yield (batch_no, song_ids, scores)


def _compute_similarity_scores_for_song_ids_range_by_search_phrase(search_phrase, page_no=0, batch_size=10):

    song_ids = [song.song_id for song in songsearch.get_songs(page_no=page_no, batch_size=batch_size)]

    scores = compute_similarity_scores_by_search_phrase(search_phrase, song_ids)

    return song_ids, scores


def compute_similarity_scores_by_search_phrase(search_phrase, song_ids):

    if not song_ids:
        return []

    search_string_embedding = embeddings.fetch_embeddings_for_search_phrase(search_phrase)
    
    songs_embedding = song_embeddings.get_embeddings_for_songs(song_ids)
    
    
    scores = search_helpers.cosine_similarity_with_matrix(songs_embedding, search_string_embedding)

    return scores[0].tolist()

## By search id

def top_10_similarity_scores(search_id, batch_size=1000):
    scores = []
    song_ids = []

    for (batch_no, _song_ids, _scores) in top_10_similarity_scores_yield(search_id, batch_size=batch_size):

        # extract top 10 from all scores so far
        song_ids, scores = _song_ids, _scores

    return song_ids, scores

def top_10_similarity_scores_yield(search_id, batch_size=1000):
    scores = []
    song_ids = []

    for (batch_no, _song_ids, _scores, _, _) in similarity_scores_by_search_id(search_id, batch_size=batch_size):
        _song_ids, _scores = _extract_top_n_scores(_song_ids, _scores, n=10)
        scores.extend(_scores)
        song_ids.extend(_song_ids)

        # extract top 10 from all scores so far
        _song_ids, _scores = _extract_top_n_scores(song_ids, scores, n=10)

        yield (batch_no, _song_ids, _scores)

def similarity_scores_by_search_id(search_id, batch_size = 10):

    for (batch_no, song_ids) in song_ids_yield(batch_size=batch_size):

        batch_id = batch_no - 1
        song_ids, scores, new_song_ids, new_scores = _compute_similarity_scores_for_song_ids_range(search_id, page_no=batch_id, batch_size=batch_size)

        yield (batch_no, song_ids, scores, new_song_ids, new_scores)


def _compute_similarity_scores_for_song_ids_range(search_id, page_no=0, batch_size=10):

    song_ids = [song.song_id for song in songsearch.get_songs(page_no=page_no, batch_size=batch_size)]

    _song_ids, _scores = songsearch.get_scores_for_song_id_range(search_id, song_ids[0], song_ids[-1])

    # build map of song_ids -> score, keep existing scores
    song_id_map = {}
    for id, score in zip(_song_ids, _scores):
        song_id_map[id] = score


    null_song_ids = [song_id for song_id in song_ids if song_id not in _song_ids]

    # compute similarity score
    null_scores = compute_similarity_scores_by_search_id(search_id, null_song_ids)

    for id, score in zip(null_song_ids, null_scores):
        song_id_map[id] = score

    scores = [song_id_map[id] for id in song_id_map]

    return song_ids, scores, null_song_ids, null_scores


def compute_similarity_scores_by_search_id(search_id, song_ids):

    if not song_ids:
        return []
    
    search_phrase = songsearch.get_search(search_id)
    if not search_phrase:
        return None

    return compute_similarity_scores_by_search_phrase(search_phrase.search_phrase, song_ids)

