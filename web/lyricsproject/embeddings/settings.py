from lyricsproject import env, settings


EMBEDDINGS_PERSISTENCE = env.get_key('PERSISTENCE') == 'True'

S3_NOT_FILE = not settings.DEBUG