from django import forms

class SearchForm(forms.Form):
    uuid = forms.CharField(label="search uuid", min_length=10)
    search_phrase = forms.CharField(label="search phrase", min_length=5)