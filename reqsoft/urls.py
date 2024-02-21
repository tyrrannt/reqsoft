"""
URL configuration for reqsoft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from reqsoft import settings

handler403 = 'main_app.views.tr_handler403'
handler404 = 'main_app.views.tr_handler404'
handler500 = 'main_app.views.tr_handler500'

urlpatterns = [
    path('', include('main_app.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('customeuser_app.urls')),
    path('blog/', include('blog_app.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('.well-known/', include('main_app.urls')),
]

if settings.DEBUG:
    # import debug_toolbar, so that it can be used in development
    urlpatterns = [path('__debug__/', include('debug_toolbar.urls'))] + urlpatterns
    # serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
