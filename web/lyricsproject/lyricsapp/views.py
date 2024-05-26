from django.shortcuts import render, redirect
from django import http
from django.views.decorators.csrf import csrf_exempt
from common import songsearch, log
from lyricsapp import models, forms, dispatchers
from lyricsproject import settings

# Create your views here.

def create_search_response(uuid, lyrics, status):
    return {
        'uuid': uuid,
        'lyrics': lyrics,
        'status': status
    }

@csrf_exempt
def search(request):
    if request.method == 'POST':

        form = forms.SearchForm(request.POST)

        if form.is_valid():

            uuid = form.cleaned_data["uuid"].replace("-","")
            search_phrase = form.cleaned_data["search_phrase"]

            # if uuid exists, fetch it
            # else create it and return response.

            if settings.SEARCH.get("ONDEMAND", False):
                search_result, status = _search_on_demand(uuid, search_phrase)
            else:
                search_result, status = _search(uuid, search_phrase)

            response_data = create_search_response(uuid, search_result, status)

            return http.JsonResponse(response_data)
        
        return http.HttpResponseBadRequest("Invalid form.")

    else:
        return http.HttpResponseBadRequest("Invalid method. Use POST")

def _search(uuid, search_phrase):
    search_obj = songsearch.get_search(uuid)
    if not search_obj:
        search_obj = _create_search(uuid, search_phrase)

    result = []
    if search_obj.status == 'DONE':
        result = [x.serialize_to_json() for x in songsearch.get_songs_for_search(search_id=uuid)]

    return result, search_obj.status == 'DONE'

def _search_on_demand(uuid, search_phrase):

    songs = songsearch.search_on_demand(search_phrase)

    _create_search(uuid, search_phrase)

    return songs

def _create_search(uuid, search_phrase):
    models.Search(id = uuid,
                        phrase = search_phrase,
                        status = 'PENDING').save()
    search_obj = songsearch.get_search(uuid)

    dispatchers.execute_search(uuid)

    return search_obj
