from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Book, Category
from .forms import BookForm


def all_books(request):
    """
    A view to return all book products, including sorting and search queries
    """
    books = Book.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                books = books.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            books = books.order_by(sortkey)

    if 'category' in request.GET:
        categories = request.GET['category'].split(',')
        books = books.filter(category__name__in=categories)
        categories = Category.objects.filter(name__in=categories)

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request,
                               "You didn't enter any search criteria!")
                return redirect(reverse('books'))

            queries = Q(name__icontains=query) | Q(author__icontains=query)
            books = books.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'books': books,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'books/books.html', context)


def book_info(request, book_id):
    """
    A view to return individuel product information
    """
    book = get_object_or_404(Book, pk=book_id)

    context = {
        'book': book,
    }

    return render(request, 'books/book_info.html', context)


def add_book(request):
    """ Add a book or product to the store """
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product or book!')
            return redirect(reverse('add_book'))
        else:
            messages.error(request, 'Failed to add a product. Please ensure the form is valid.')
    else:
        form = BookForm()

    template = 'books/add_book.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


def edit_book(request, book_id):
    """ Edit a book or product to the store """
    book = get_object_or_404(Book, pk=book_id)
    form = BookForm(instance=book)
    messages.info(request, f'You are editing {book.name}')

    template = 'books/edit_book.html'
    context = {
        'form': form,
        'book': book,
    }

    return render(request, template, context)
