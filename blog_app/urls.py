from django.urls import path
from . import views
from .views import CommentCreateView, ArticleByTagListView, ArticleSearchResultView

app_name = 'blog_app'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='articles_create'),
    path('articles/<str:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<str:slug>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<str:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('articles/<int:pk>/comments/create/', CommentCreateView.as_view(), name='comment_create_view'),
    path('articles/tags/<str:tag>/', ArticleByTagListView.as_view(), name='articles_by_tags'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<str:slug>/', views.ArticleByCategoryListView.as_view(), name="articles_by_category"),
    path('category/files/<str:slug>/', views.FilesByCategoryListView.as_view(), name="files_by_category"),
    path('search/', ArticleSearchResultView.as_view(), name='search'),
    path('files/', views.FilesListView.as_view(), name='files_list'),
    path('files/<int:pk>/', views.FilesDetailView.as_view(), name='file_detail'),
    path('files/create/', views.FilesCreateView.as_view(), name='file_create'),
    path('files/<int:pk>/update/', views.FilesUpdateView.as_view(), name='file_update'),
    path('files/<int:pk>/delete/', views.FilesDeleteView.as_view(), name='file_delete'),
]
