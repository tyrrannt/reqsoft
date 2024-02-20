import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import models
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from taggit.models import Tag

from blog_app.forms import ArticleCreateForm, ArticleUpdateForm, CommentCreateForm, CategoryCreateForm
from blog_app.models import Article, Category, Comment
from main_app.mixins import AuthorRequiredMixin


# Create your views here.

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = ' - Список категорий'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryCreateForm

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # category = Category.objects.all().values_list('title', flat=True)
        context['title'] = ' - Список статей'
        return context


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    queryset = model.objects.detail()

    def get_similar_articles(self, obj):
        """
        Метод get_similar_articles() извлекает список статей, которые имеют общие теги с текущей статьей, и сортирует
        их по количеству общих тегов. Затем он перемешивает этот список и возвращает первые 6 статей.
        """
        article_tags_ids = obj.tags.values_list('id', flat=True)
        similar_articles = Article.objects.filter(tags__in=article_tags_ids).exclude(id=obj.id)
        similar_articles = similar_articles.annotate(related_tags=Count('tags')).order_by('-related_tags')
        similar_articles_list = list(similar_articles.all())
        random.shuffle(similar_articles_list)
        return similar_articles_list[:6]

    def get_context_data(self, **kwargs):
        """
        Метод get_context_data создает контекст шаблона, который включает заголовок статьи, форму создания комментария
        и список похожих статей, полученных из get_similar_articles().
        """
        context = super().get_context_data(**kwargs)
        category = Category.objects.all()
        context['title'] = self.object.title
        context['category'] = category
        context['form'] = CommentCreateForm
        context['similar_articles'] = self.get_similar_articles(self.object)
        return context


class ArticleByCategoryListView(LoginRequiredMixin, ListView):
    model = Article
    category = None

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Article.objects.all().filter(category__slug=self.category.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.all()
        context['category'] = self.category
        context['title'] = f' - Статьи из категории: {self.category.title}'
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """
    Представление: создание материалов на сайте
    """
    model = Article
    form_class = ArticleCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = ' - Добавление статьи на сайт'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class ArticleUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Представление: обновления материала на сайте
    """
    model = Article
    form_class = ArticleUpdateForm
    template_name = 'blog_app/article_update.html'
    success_message = 'Материал был успешно обновлен'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f' - Обновление статьи: {self.object.title}'
        return context

    def form_valid(self, form):
        form.instance.updater = self.request.user
        form.save()
        return super().form_valid(form)


class ArticleDeleteView(AuthorRequiredMixin, DeleteView):
    """
    Представление: удаления материала
    """
    model = Article
    success_url = reverse_lazy('blog_app:article_list')
    context_object_name = 'article'
    template_name = 'blog_app/article_delete.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f' - Удаление статьи: {self.object.title}'
        return context


class ArticleByTagListView(ListView):
    model = Article
    context_object_name = 'articles'
    paginate_by = 10
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = Article.objects.all().filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f' - Статьи по тегу: {self.tag.name}'
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        """
        Метод is_ajax() возвращает True, если запрос был сделан через AJAX, и False в противном случае.
        """
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        """
        Метод form_invalid() вызывается, когда форма создания комментария не проходит валидацию. Если запрос был через
        AJAX, то возвращается JsonResponse с ошибкой, иначе вызывается родительский метод form_invalid().
        """
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        """
        Метод form_valid() вызывается, когда форма создания комментария прошла валидацию. В нем сохраняется новый
        комментарий, и возвращается успешный ответ с атрибутами в виде json с помощью JsonResponse, в случае, если
        это был не AJAX запрос, редеректим пользователя на статью.
        """

        comment = form.save(commit=False)
        comment.article_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.profile.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.profile.get_absolute_url()
            }, status=200)

        return redirect(comment.article.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)


class ArticleSearchResultView(ListView):
    """
    Реализация поиска статей на сайте
    """
    model = Article
    context_object_name = 'articles'
    paginate_by = 10
    allow_empty = True

    def get_queryset(self):
        query = self.request.GET.get('do')
        search_vector = SearchVector('full_description', weight='B') + SearchVector('title', weight='A')
        search_query = SearchQuery(query)
        return (self.model.objects.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f' - Результаты поиска: {self.request.GET.get("do")}'
        return context