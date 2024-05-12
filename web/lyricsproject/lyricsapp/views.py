from django.shortcuts import render, redirect
from django import http
from django.views.decorators.csrf import csrf_exempt
from common import songsearch, log
from lyricsapp import models, forms

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
            search_obj = songsearch.get_search(uuid)
            log.info("search_obj:{0}".format(search_obj))
            if not search_obj:
                models.Search(id = uuid,
                                phrase = search_phrase,
                                status = 'PENDING').save()
                search_obj = songsearch.get_search(uuid)

                #dispatchers.execute_search(search_id)

                return http.JsonResponse(create_search_response(uuid, [], False))
            

            # if search is pending, return status
            if search_obj.status != 'DONE':
                return http.JsonResponse(create_search_response(uuid, [], False))

            # else if completed, return results
            search_result = [x.serialize_to_json() for x in songsearch.get_songs_for_search(search_id=uuid)]
            response_data = create_search_response(uuid, search_result, True)

            return http.JsonResponse(response_data)
        
        return http.HttpResponseBadRequest("Invalid form.")

    else:
        return http.HttpResponseBadRequest("Invalid method. Use POST")

def status(request):
    pass
