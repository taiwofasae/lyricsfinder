from openai import OpenAI

from common import log

count = 0

client = OpenAI()

def get_embeddings_for_phrases(phrases, model="text-embedding-3-small"):
    global count
    count += 1
    log.info("Open AI call no: {0}".format(count))
    log.info("Api call to openai for {} items".format(len(phrases)))
    phrases = [text.replace("\n", " ") for text in phrases]
    return [d.embedding for d in client.embeddings.create(input = phrases, model=model).data]


API_VERSION = 'v2'