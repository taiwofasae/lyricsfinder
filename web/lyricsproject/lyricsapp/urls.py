from django.urls import path
from django.contrib import admin
from django.views.generic import RedirectView
from lyricsapp import views

urlpatterns = [
    path('search/', views.search)
]