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
                search_result = _search_on_demand(uuid, search_phrase)
            else:
                search_result = _search(uuid, search_phrase)

            if search_result:
                response_data = create_search_response(uuid, search_result, True)

                return http.JsonResponse(response_data)
        
            return http.JsonResponse(create_search_response(uuid, [], False))
        
        return http.HttpResponseBadRequest("Invalid form.")

    else:
        return http.HttpResponseBadRequest("Invalid method. Use POST")

def _search(uuid, search_phrase):
    search_obj = songsearch.get_search(uuid)
    log.info("search_obj:{0}".format(search_obj))
    if not search_obj:
        models.Search(id = uuid,
                        phrase = search_phrase,
                        status = 'PENDING').save()
        search_obj = songsearch.get_search(uuid)

        dispatchers.execute_search(uuid)
    

    # if completed, return results
    if search_obj.status == 'DONE':
        return [x.serialize_to_json() for x in songsearch.get_songs_for_search(search_id=uuid)]

    return []

def _search_on_demand(uuid, search_phrase):

    songs = songsearch.search_on_demand(search_phrase)

    dispatchers._create_search(uuid, search_phrase)

    return songs