from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from blog_app.models import Article, Category


# Create your views here.

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.all()
        context['title'] = ' - Список статей'
        context['category'] = category
        return context


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.all()
        context['title'] = self.object.title
        context['category'] = category
        return context


class ArticleByCategoryListView(ListView):
    model = Article
    category = None

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Article.objects.all().filter(category__slug=self.category.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.all()
        context['category'] = category
        context['title'] = f'Статьи из категории: {self.category.title}'
        return context
