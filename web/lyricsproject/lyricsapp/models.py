from django.db import models
from django.db.models import UniqueConstraint # Constrains fields to unique values
from django.db.models.functions import Lower # Returns lower cased value of field

# Create your models here.
class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Song(TimeStampedModel):
    """Model representing a song"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    artist = models.CharField(max_length=50)
    lyrics = models.TextField(max_length=2000)
    char_length = models.IntegerField(null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.lyrics:
            self.char_length = len(self.lyrics)

        super().save(*args, **kwargs)

    def short_lyrics(self):
        return self.lyrics[0:100]

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['title','artist'],
                name='song_title_artist_case_insensitive_unique',
                violation_error_message="Song and artist already exists (case insensitive match)"
            ),
        ]
    
import uuid

class Search(TimeStampedModel):
    """Model representing a search phrase"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    phrase = models.CharField(max_length=50)
    api_version = models.CharField(max_length=20, null=True)
    done_timestamp = models.DateTimeField('Done Time', null=True)


    SEARCH_STATUS = (
        ('PENDING','PENDING'),
        ('RUNNING','RUNNING'),
        ('DONE','DONE'),
    )
    status = models.CharField(
        max_length=10,
        choices=SEARCH_STATUS,
        blank=False,
        default=SEARCH_STATUS[0][0],
        help_text='Search status'
    )
    

    def __str__(self):
        return self.phrase
    
    def post_save(self, *args, **kwargs):
        super().post_save(*args, **kwargs)
    
    
    class Meta:

        constraints = [
            # UniqueConstraint(
            #     Lower('phrase'),
            #     name='search_phrase_case_insensitive_unique',
            #     violation_error_message="Search phrase already exists (case insensitive match)"
            # ),
        ]

class SongSearch(TimeStampedModel):
    """Model representing a search result on a song"""
    song = models.ForeignKey('Song', on_delete=models.RESTRICT)
    search = models.ForeignKey('Search', on_delete=models.RESTRICT)
    significant = models.BooleanField()
    sim_score = models.FloatField()

    def __str__(self) -> str:
        return f"search:'{self.search}' on the song: '{self.song}'"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['song_id','search_id'],
                name='composite_pk_song_id_search_id',
                violation_error_message='Song search already exists'
            ),
        ]