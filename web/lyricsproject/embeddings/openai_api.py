import openai
from common import log

class API:
    def __init__(self) -> None:
        self.client = openai.OpenAI()
        self.count = 0

    def get_embeddings_for_phrases(self, phrases, model="text-embedding-3-small"):
        self.count += 1
        log.info("Open AI call no: {0}".format(self.count))
        log.info("Api call to openai for {} items".format(len(phrases)))
        phrases = [text.replace("\n", " ") for text in phrases]
        return [d.embedding for d in self.client.embeddings.create(input = phrases, model=model).data]
