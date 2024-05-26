from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from lyricsapp.models import Song, SongSearch, Search

# Register your models here.
#admin.site.register(Song)

class SongSearchesInline(admin.TabularInline):
    model = SongSearch
    extra = 0



@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'short_lyrics', 'char_length','created_on','id')

    list_filter = ('artist',)

    search_fields = ('title', 'lyrics')

    inlines = [SongSearchesInline]

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('phrase','status', 'api_version', 'created_on','done_timestamp','id')

    list_filter = ('api_version','status')

    search_fields = ('phrase',)

    ordering = ('-created_on',)

    inlines = [SongSearchesInline]

@admin.register(SongSearch)
class SongSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'search_link', 'song_link', 'sim_score', 'significant','created_on')

    ordering = ('-created_on',)

    # def song_link(self, item):
    #     url = resolve_url(admin_urlname(Song._meta, 'changelist')) + '?song_id={}'.format(item.song_id)
    #     return format_html(
    #         '<a href="{url}">{name}</a>'.format(url=url, name=str(item.song))
    #     )
    # song_link.short_description = 'song'

    def song_link(self, item):
        filter_url = resolve_url(admin_urlname(SongSearch._meta, 'changelist')) + '?song_id={}'.format(item.song_id)
        song_url = resolve_url(admin_urlname(Song._meta, 'change'), item.song_id)
        return format_html(
            '<a href="{song_url}">{name}</a> | <a href="{filter_url}">filter</a>'.format(song_url=song_url, name=str(item.song),
                                                                                filter_url=filter_url)
        )
    song_link.short_description = 'song'

    def search_link(self, item):
        url = resolve_url(admin_urlname(Search._meta, 'change'), item.search_id)
        return format_html(
            '<a href="{url}">{name}</a>'.format(url=url, name=str(item.search))
        )
    search_link.short_description = 'search'