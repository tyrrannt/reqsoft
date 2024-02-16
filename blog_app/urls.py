from django.urls import path
from . import views

app_name = 'blog_app'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='articles_create'),
    path('articles/<str:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<str:slug>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<str:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('category/<str:slug>/', views.ArticleByCategoryListView.as_view(), name="articles_by_category"),
]
