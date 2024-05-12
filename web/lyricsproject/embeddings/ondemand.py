from embeddings import openai_api

from common import log




def get_embeddings_for_phrases(phrases):
    return openai_api.get_embeddings_for_phrases(phrases)


API_VERSION = openai_api.API_VERSION
