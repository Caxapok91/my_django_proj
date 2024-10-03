from django.shortcuts import render
from django.http import *
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AuthorsForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


# Create your views here.
class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')


def edit1(request, id):
    author = Author.objects.get(id=id)
    if request.method == "POST":
        author.first_name = request.POST.get("first_name")
        author.last_name = request.POST.get("last_name")
        author.date_of_birth = request.POST.get("date_of_birth")
        author.date_of_death = request.POST.get("date_of_death")
        author.save()
        return HttpResponseRedirect("/authors_add/")
    else:
        return render(request, "catalog/edit1.html", {"author": author})


def delete(request, id):
    try:
        author = Author.objects.get(id=id)
        author.delete()
        return HttpResponseRedirect("/authors_add")
    except Author.DoesNotExist:
        return HttpResponseNotFound("<h2>Автор не найден</h2>")


def create(request):
    if request.method == "POST":
        author = Author()
        author.first_name = request.POST.get("first_name")
        author.last_name = request.POST.get("last_name")
        author.date_of_birth = request.POST.get("date_of_birth")
        author.date_of_death = request.POST.get("date_of_death")
        author.save()
        return HttpResponseRedirect("/authors_add/")


def authors_add(request):
    author = Author.objects.all()
    authorsform = AuthorsForm()
    return render(request, 'catalog/authors_add.html',
                  {'form': authorsform, 'author': author})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    # Универсальный класс представления списка книг,
    # находящихся в заказе у текущего пользователя
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user).filter(
            status__exact='2').order_by('due_back')


class BookListView(generic.ListView):
    model = Book
    paginate_by = 3


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 4


def index(request):
    # Генерация кол-ва некоторых клавных объектов

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Доступные книги(статус= "На складе")
    # Здесь метод 'all()' применен по умолчанию.
    # status__exact=2   два нижних подчеркивания!

    num_instances_available = BookInstance.objects.filter(status__exact=2).count()

    # Авторы книг,
    num_authors = Author.objects.count()
    # добавляем
    # Кол-во посещений этого view, подсчитываем в переменную session
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Отрисовка НТМL-шаблона index.html с данными
    # внутри переменной context
    return render(request, 'index.html',
                  context={'num_books': num_books,
                           'num_instances': num_instances,
                           'num_instances_available': num_instances_available,
                           'num_authors': num_authors,
                           'num_visits': num_visits,  # добавляем в шаблон
                           },
                  )
