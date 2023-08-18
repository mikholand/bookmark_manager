import requests
from bs4 import BeautifulSoup
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .forms import (
    AddBookmarkForm,
    AddCollectionForm,
    LoginUserForm,
    RegisterUserForm,
)
from .models import Bookmark, Collection
from .serializers import (
    BookmarkRequestSerializer,
    BookmarkSerializer,
    CollectionRequestSerializer,
    CollectionSerializer,
)
from .utils import DataMixin


def check_og_type(og_type):
    if 'article' in og_type:
        return 'article'
    elif 'book' in og_type:
        return 'book'
    elif 'music' in og_type:
        return 'music'
    elif 'video' in og_type:
        return 'video'
    else:
        return 'website'


def find_meta_content(soup, og_name):
    prop_meta = soup.find('meta', property=f'og:{og_name}')
    if prop_meta:
        return prop_meta.get('content', '')

    name_meta = soup.find('meta', attrs={'name': f'og:{og_name}'})
    if name_meta:
        return name_meta.get('content', '')

    if og_name == 'title':
        return soup.title.string if soup.title else ''

    if og_name == 'description':
        description = soup.find('meta', attrs={'name': og_name})
        if description:
            return description.get('content', '')

    return ''


def get_open_graph_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        og_data = {
            'title': find_meta_content(soup, 'title'),
            'description': find_meta_content(soup, 'description'),
            'image': find_meta_content(soup, 'image'),
            'type': find_meta_content(soup, 'type'),
        }

        return og_data
    else:
        return None


def is_not_authenticated(user):
    return not user.is_authenticated


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>404 Page not found =(</h1>')


@method_decorator(login_required, name='dispatch')
class BookmarkHome(DataMixin, ListView):
    model = Bookmark
    template_name = 'bookmarks/bookmarks.html'
    context_object_name = 'bookmarks'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная страница")
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)


class BookmarkHomeAPI(DataMixin, ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)


class BookmarkCreateView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddBookmarkForm
    template_name = 'bookmarks/bookmark_add.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True

    def form_valid(self, form):
        url = form.cleaned_data.get('url')
        og_data = get_open_graph_data(url)
        form.instance.user = self.request.user

        if og_data:
            form.instance.title = og_data.get('title', '')
            form.instance.description = og_data.get('description', '')
            form.instance.preview_image = og_data.get('image', '')
            form.instance.bookmark_type = check_og_type(og_data.get('type', ''))
            form.instance.url = url

        bookmark = form.save()
        collections = form.cleaned_data.get('collections')
        if collections:
            bookmark.collections.set(collections)

        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Добавление закладки")
        return dict(list(context.items()) + list(c_def.items()))


class BookmarkCreateAPIView(LoginRequiredMixin, DataMixin, CreateAPIView):
    serializer_class = BookmarkRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        url = serializer.validated_data.get('url')
        og_data = get_open_graph_data(url)
        user = self.request.user

        if og_data:
            serializer.validated_data['title'] = og_data.get('title', '')
            serializer.validated_data['description'] = og_data.get('description', '')
            serializer.validated_data['preview_image'] = og_data.get('image', '')
            serializer.validated_data['bookmark_type'] = check_og_type(og_data.get('type', ''))
            serializer.validated_data['url'] = url

        serializer.save(user=user)

    def get_user_context(self, **kwargs):
        context = super().get_user_context(**kwargs)
        # Добавить дополнительные элементы контекста, если необходимо
        return context

    @swagger_auto_schema(
        request_body=BookmarkRequestSerializer,
        responses={201: BookmarkSerializer()}
    )
    def post(self, request, *args, **kwargs):
        # Реализация метода post
        return self.create(request, *args, **kwargs)


class BookmarkUpdateView(LoginRequiredMixin, DataMixin, UpdateView):
    model = Bookmark
    form_class = AddBookmarkForm
    template_name = 'bookmarks/bookmark_update.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Редактирование закладки")
        return dict(list(context.items()) + list(c_def.items()))


class BookmarkUpdateAPIView(LoginRequiredMixin, DataMixin, UpdateAPIView):
    serializer_class = BookmarkRequestSerializer
    queryset = Bookmark.objects.all()

    def perform_update(self, serializer):
        url = serializer.validated_data.get('url')
        og_data = get_open_graph_data(url)
        user = self.request.user

        if og_data:
            serializer.validated_data['title'] = og_data.get('title', '')
            serializer.validated_data['description'] = og_data.get('description', '')
            serializer.validated_data['preview_image'] = og_data.get('image', '')
            serializer.validated_data['bookmark_type'] = check_og_type(og_data.get('type', ''))
            serializer.validated_data['url'] = url

        serializer.save(user=user)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_user_context(self, **kwargs):
        context = kwargs
        return context


class BookmarkDeleteView(LoginRequiredMixin, DataMixin, DeleteView):
    model = Bookmark
    template_name = 'bookmarks/bookmark_delete.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Удаление закладки")
        return dict(list(context.items()) + list(c_def.items()))


class BookmarkDeleteAPIView(LoginRequiredMixin, DataMixin, DestroyAPIView):
    queryset = Bookmark.objects.all()

    @swagger_auto_schema(
        responses={204: "No Content"}
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_user_context(self, **kwargs):
        context = kwargs
        return context


@method_decorator(login_required, name='dispatch')
class CollectionListView(DataMixin, ListView):
    model = Collection
    template_name = 'bookmarks/collections.html'
    context_object_name = 'collections'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Мои коллекции")
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)


class CollectionListAPIView(LoginRequiredMixin, ListAPIView):
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)


class CollectionBookmarksView(DataMixin, ListView):
    model = Bookmark
    template_name = 'bookmarks/collection_bookmarks.html'
    context_object_name = 'bookmarks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection_id = self.kwargs.get('collection_id')
        collection = get_object_or_404(Collection, id=collection_id, user=self.request.user)
        c_def = self.get_user_context(title=f"Закладки в коллекции {collection.title}")
        context.update(c_def)
        context['collection'] = collection
        return context

    def get_queryset(self):
        collection_id = self.kwargs.get('collection_id')
        return Bookmark.objects.filter(user=self.request.user, collections__id=collection_id)


class CollectionBookmarksAPIView(LoginRequiredMixin, ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        collection_id = self.kwargs.get('collection_id')
        collection = get_object_or_404(Collection, id=collection_id, user=self.request.user)
        return collection.bookmarks.all()


class CollectionCreateView(LoginRequiredMixin, CreateView):
    model = Collection
    form_class = AddCollectionForm
    template_name = 'bookmarks/collection_add.html'
    success_url = reverse_lazy('collections')
    login_url = reverse_lazy('home')
    raise_exception = True

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CollectionCreateAPIView(LoginRequiredMixin, CreateAPIView):
    serializer_class = CollectionRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    @swagger_auto_schema(
        request_body=CollectionRequestSerializer,
        responses={201: CollectionSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CollectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Collection
    form_class = AddCollectionForm
    template_name = 'bookmarks/collection_update.html'
    success_url = reverse_lazy('collections')
    login_url = reverse_lazy('home')
    raise_exception = True


class CollectionUpdateAPIView(LoginRequiredMixin, UpdateAPIView):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    @swagger_auto_schema(
        request_body=CollectionSerializer,
        responses={200: CollectionSerializer()}
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=CollectionSerializer,
        responses={200: CollectionSerializer()}
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CollectionDeleteView(LoginRequiredMixin, DeleteView):
    model = Collection
    template_name = 'bookmarks/collection_delete.html'
    success_url = reverse_lazy('collections')
    login_url = reverse_lazy('home')
    raise_exception = True


class CollectionDeleteAPIView(LoginRequiredMixin, DestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={204: "No Content"}
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'bookmarks/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data['email']
        user.save()
        login(self.request, user)
        return redirect('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    @method_decorator(user_passes_test(is_not_authenticated, login_url='home'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'bookmarks/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

    @method_decorator(user_passes_test(is_not_authenticated, login_url='home'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def logout_user(request):
    logout(request)
    return redirect('login')
