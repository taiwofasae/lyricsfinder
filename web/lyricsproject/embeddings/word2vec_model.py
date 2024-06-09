import gensim.models.word2vec as w2v

class Word2VecModel:
  def __init__(self, model = None):
    self.model = model


  def fit(self, corpus):
    self.model.build_vocab(corpus)
    m_count = self.model.corpus_count
    epochs_count = self.model.epochs
    print(f'records count: [{m_count}]')
    print(f'Epochs count: [{epochs_count}]')
    print('Start training...')
    self.model.train(corpus, total_examples=m_count, epochs=epochs_count)
    print('Trained!')

  def __getitem__(self, word):
    return self.model.wv[word] if word in self.model.wv else None

  def __call__(self, *args, **kwargs):
    return self.get_embedding(*args, **kwargs)

  def get_embedding(self, word):
    if isinstance(word, list):
      return [self.get_embedding(w) for w in word]
    return self[word]


class Sentence2VecModel(Word2VecModel):

  def __init__(self, *args, **kwargs):
    super(Sentence2VecModel, self).__init__(*args, **kwargs)

  def __call__(self, *args, **kwargs):
    return self.get_embedding_sentence(*args, **kwargs)

  def sentence_to_words(self, sentence):
    return [p for p in sentence.lower().split() if p.isalpha()]

  def tokenize(self, sentence):
    # arrange proper tokenization
    return self.sentence_to_words(sentence)

  def tokenize_batch(self, sentences):
    return [self.tokenize(sentence) for sentence in sentences]


  def get_embedding_sentence(self, sentence):
    if isinstance(sentence, list):
      return [self.get_embedding_sentence(sent) for sent in sentence]

    vector_sum = 0
    count = 0
    for word in self.tokenize(sentence):
      if word in self.model.wv:
        vector_sum += self.get_embedding(word)
        count += 1
    if count > 0:
      return vector_sum / count
    else:
      return None

  def get_embedding_sentences(self, sentences):
    return [self.get_embedding_sentence(sence) for sence in sentences]


  def cosine_similarity_sentence(self, pair, pair2 = None):

    pair1 = pair
    if not pair2:
      pair1 = [p[0] for p in pair]
      pair2 = [p[1] for p in pair]

    pair1 = self.get_embedding_sentences(pair1)
    pair2 = self.get_embedding_sentences(pair2)


    return [cosine_similarity(p[0], p[1]) for p in zip(pair1, pair2)]

  def cosine_similarity_batch(self, pairs):
    return [self.cosine_similarity_sentence(pair) for pair in pairs]

class Word2VecFileModel(Word2VecModel):

  def __init__(self, *args, **kwargs):
    super(Word2VecFileModel, self).__init__(*args, **kwargs)


  def save(self, filename):
    self.model.save(filename)

  def load(self, filename):
    self.model = w2v.Word2Vec.load(filename)

    return self.model

import numpy as np
def cosine_similarity(a, b):
  return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))
