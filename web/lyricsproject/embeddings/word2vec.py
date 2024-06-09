from embeddings import word2vec_model


class Word2Vec:

  def __init__(self, model_file) -> None:
    model = word2vec_model.Word2VecFileModel().load(model_file)
    self.model = word2vec_model.Sentence2VecModel(model)

  def get_embeddings_for_phrases(self, blocks):
    blocks = [text.replace("\n", " ") for text in blocks]
    return self.model(blocks)

  def single_word2vec_embeddings(self, text):
    return self.get_embeddings_for_phrases([text.replace("\n", " ")])[0]