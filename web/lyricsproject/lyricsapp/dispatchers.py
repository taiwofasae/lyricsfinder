from django.db.models.signals import post_save
from django.dispatch import receiver

from lyricsapp import models
from django_q.tasks import async_task
from common import log, songsearch
import uuid

@receiver(post_save, sender=models.Search)
def execute_search(sender, instance, **kwargs):
    log.info("'Post_save on Search' dispatch called")

    execute_search(instance.id)

def execute_pending_search_phrases():
    songsearch.execute_pending_search_phrases()

def execute_search(search_id):
    if isinstance(search_id,uuid.UUID):
        search_id = search_id.hex

    if '-' in search_id:
        search_id = search_id.replace('-','')

    async_task('common.songsearch.execute_search', search_id)
