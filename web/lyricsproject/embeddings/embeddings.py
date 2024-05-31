from embeddings import settings
from embeddings import openai_api
from embeddings import persistence
from common import songsearch, log
import importlib
import numpy as np

PERSIST = settings.EMBEDDINGS_PERSISTENCE


model_dict = {
        'default': openai_api.get_embeddings_for_phrases,
        'openai': openai_api.get_embeddings_for_phrases,
        'random': lambda phrases: [np.random.rand(768,) for _ in phrases],
    }


class API:

    def __init__(self, model_api = 'default'):
        if model_api in model_dict:
            model_api = model_dict[model_api]
        
        self.model_api = model_api


    def get_embeddings_for_phrases(self, phrases, *args, **kwargs):
        log.info("getting search phrases for {0} search_ids".format(len(phrases)))

        if len(phrases) < 5:
            log.info("search_phrases: '{0}'".format('\n'.join(phrases)))

        return self.model_api(phrases, *args, **kwargs)

