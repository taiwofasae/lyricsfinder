from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.http import HttpResponse
from lyricsapp import dispatchers
from embeddings import songsearch, embeddings
import logging
from lyricsproject import settings

# Create your views here.

def execute(request, search_id):
    #dispatchers.execute_search(search_id)
    songsearch.execute_pending_search_phrases()
    #songsearch.execute_search(search_id)
    #embeddings.get_embeddings_for_search_phrase(search_id)

    return HttpResponse(status=200)

def index(request):
    """View function for home page of site"""

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

    #context_object_name = 'book_list'   # your own name for the list as a template variable
    
    template_name = 'book_list.html'  # Specify your own template name/location

class BookDetailView(generic.DetailView):
    model = Book

    template_name = 'book_detail.html'

def book_detail_view1(request, primary_key):
    try:
        book = Book.objects.get(pk=primary_key)
    except Book.DoesNotExist:
        raise Http404('Book does not exist')

    return render(request, 'catalog/book_detail.html', context={'book': book})

def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})



class AuthorListView(generic.ListView):
    model = Author

    template_name = 'author_list.html'

class AuthorDetailView(generic.DetailView):
    model = Author

    template_name = 'author_detail.html'



def orderFormView(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('show_url')
    
    template_name = 'ofv.html'
    context = {'form': form}
    return render(request, template_name, context)

def showView(request):
    obj = Orders.objects.all()
    template_name = 'sv.html'
    context = {'obj': obj}
    return render(request, template_name, context)

def updateView(request, f_oid):
    obj = Orders.objects.get(oid=f_oid)
    form = OrderForm(instance=obj)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('show_url')
    
    template_name = 'order.html'
    context = {'form': form}
    return render(request, template_name, context)

def deleteView(request, f_oid):
    obj = Orders.objects.get(oid=f_oid)
    if request.method == 'POST':
        obj.delete()
        return redirect('show_url')
    template_name = 'confirmation.html'
    context = {'obj': obj}
    return render(request, template_name, context)