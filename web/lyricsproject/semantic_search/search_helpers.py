import numpy as np

SCALE = 5


def cosine_similarity(a, b):
  score = 5 * np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))
  return round(score, 1)

def _convert_to_2D_matrix(v):
  if v.ndim < 2:
    v = np.array(v)
    if v.ndim < 2: # if 1D
      v = v.reshape(1,-1)
  return v

def cosine_similarity_with_matrix(source, entry):
  source = np.asarray(source)
  entry = np.asarray(entry)

  source = _convert_to_2D_matrix(source)
  entry = _convert_to_2D_matrix(entry)

  (s1,s2) = source.shape # often m by D
  (e1,e2) = entry.shape # n by D
  if e2 == s2:
    # transpose source matrix
    source = source.transpose() # D by m

  p1 = entry.dot(source)
  p2 = np.linalg.norm(entry, axis=1).reshape(-1,1) * np.linalg.norm(source, axis=0).reshape(1,-1)
  result = p1 / p2
  
  return np.round(result * SCALE, 2)

def find_similarity_rank(songs_embeddings, phrase_embeddings, index_in_song):
  source = np.asarray(songs_embeddings)
  entry = np.asarray(phrase_embeddings)
  sim_matrix = cosine_similarity_with_matrix(source=source, entry=entry)
  
  r, c = np.arange(sim_matrix.shape[0]), np.atleast_1d(index_in_song)

  return np.array(sim_matrix).argsort()[:,::-1].argsort()[r, c]

def top_n_songs_indices(songs_embeddings, phrase_embeddings, n=10):
  source = np.asarray(songs_embeddings)
  entry = np.asarray(phrase_embeddings)
  return np.array(cosine_similarity_with_matrix(source=source, entry=entry)).argsort()[:,-n:][:,::-1]