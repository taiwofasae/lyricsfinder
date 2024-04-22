from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models
from django_q.tasks import async_task
from embeddings import songsearch
import logging

@receiver(post_save, sender=models.Search)
def execute_search(sender, instance, **kwargs):
    logging.info("'Post_save on Search' dispatch called")
    execute_search(instance.id)

def execute_pending_search_phrases():
    songsearch.execute_pending_search_phrases()

def execute_search(search_id):
    async_task('embeddings.songsearch.execute_search', search_id)
