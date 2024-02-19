from django import template
from django.db.models import Count
from taggit.models import Tag

from blog_app.models import Comment, Article

register = template.Library()

@register.simple_tag
def popular_tags():
    """
    Данный код создает пользовательский тег для шаблонов Django с именем popular_tags, который получает список
    популярных тегов, отсортированных по количеству статей, содержащих эти теги. Для этого используется модуль
    django.db.models для выполнения запросов к базе данных Django и модель Tag из стороннего пакета django-taggit для
    работы с тегами.

    После выполнения запроса, полученный список тегов сохраняется в переменной tag_list. Каждый элемент списка
    представлен в виде словаря, содержащего три ключа - name (имя тега), num_times (количество статей с этим тегом) и
    slug (уникальный идентификатор тега).

    Этот список затем возвращается из функции popular_tags в виде контекста, который можно использовать в шаблоне для
    вывода списка популярных тегов.
    """
    tags = Tag.objects.annotate(num_times=Count('article')).order_by('-num_times')
    tag_list = list(tags.values('name', 'num_times', 'slug'))
    return tag_list


@register.inclusion_tag('blog_app/latest_comments.html')
def show_latest_comments(count=5):
    """
    Этот код реализует inclusion tag под названием show_latest_comments, который позволяет вывести последние
    опубликованные комментарии в шаблоне latest_comments.html.

    Этот тег принимает аргумент count, определяющий количество комментариев для отображения. По умолчанию, это значение
    равно 5.

    Тег использует Comment.objects.select_related('author'), чтобы получить последние комментарии, связанные с их
    авторами. Фильтр filter(status='published') используется для получения только опубликованных комментариев.

    Комментарии сортируются по дате создания в обратном порядке с помощью order_by('-time_create').

    Наконец, тег возвращает словарь comments, который содержит последние комментарии для использования в шаблоне
    latest_comments.html.
    """
    comments = Comment.objects.select_related('author').filter(status='published').order_by('-time_create')[:count]
    return {'comments': comments}

@register.simple_tag()
def get_count_comments(article):
    return article.comments.count()
