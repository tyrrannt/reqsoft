from django.urls import path
from . import views

app_name = 'blog_app'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<str:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<str:slug>/', views.ArticleByCategoryListView.as_view(), name="articles_by_category"),
]
