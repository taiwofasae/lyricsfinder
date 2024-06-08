from django.apps import AppConfig

class LyricsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lyricsapp'

    # def ready(self):
    #     # from scheduler import scheduler
    #     # scheduler.start()
    #     from lyricsapp import dispatchers
    #     dispatchers.fetch_embeddings(batch_size=20)
