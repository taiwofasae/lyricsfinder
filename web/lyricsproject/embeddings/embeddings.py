from embeddings import settings
from embeddings import openai_api, word2vec
from embeddings import persistence
from common import songsearch, log
import importlib
import numpy as np

PERSIST = settings.EMBEDDINGS_PERSISTENCE


key_map = {
        'openai': openai_api.API().get_embeddings_for_phrases,
        'random': lambda phrases: [np.random.rand(768,) for _ in phrases]
    }

# not used
extension_map = {
    'w2v': word2vec.Word2Vec
}

def selector_fn(key, model_file = None):
    log.info(f"selector_fn key:{key}")
    log.info(f"model_file:{model_file}") if model_file else None
    if callable(key):
        log.info('selector_fn for embeddings model is callable!')
        return key
    
    fn = key_map['random']

    if key in key_map:
        fn = key_map[key]

    elif model_file and isinstance(model_file, str):
        if key == 'word2vec':
            log.info("model file ends with .w2v. Selecting word2vec...")
            fn = word2vec.Word2Vec(model_file).get_embeddings_for_phrases
        
        

    
    return lambda phrases, *args, **kwargs: get_embeddings_for_phrases(fn, phrases=phrases, *args, **kwargs)



def get_embeddings_for_phrases(model, phrases, *args, **kwargs):
    log.info("getting search phrases for {0} search_ids".format(len(phrases)))

    if len(phrases) < 5:
        log.info("search_phrases: '{0}'".format('\n'.join(phrases)))

    return model(phrases, *args, **kwargs)

