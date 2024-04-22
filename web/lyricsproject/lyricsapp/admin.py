from django.contrib import admin

from .models import Song, SongSearch, Search

# Register your models here.
#admin.site.register(Song)

class SongSearchesInline(admin.TabularInline):
    model = SongSearch
    extra = 0



@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_lyrics', 'char_length','created_on','id')

    inlines = [SongSearchesInline]

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('phrase','status', 'api_version', 'created_on','done_timestamp','id')

    list_filter = ('api_version',)

    inlines = [SongSearchesInline]

@admin.register(SongSearch)
class SongSearchAdmin(admin.ModelAdmin):
    list_display = ('search', 'song', 'sim_score', 'significant','created_on')