from datetime import timedelta, datetime, date, time

from django import template
from django.db.models import Count, Q
from django.utils import timezone
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

@register.simple_tag
def popular_articles():
    """
    Данный код является Django-шаблон тегом. Он выводит список 10 самых популярных статей за последние 7 дней,
    отсортированных по количеству просмотров за сегодняшний день и за все время.

    Объяснение кода:

    Строки 1-5: импорт необходимых модулей и модели Article.
    Строка 7: регистрация шаблонного тега в Django.
    Строки 9-10: получение текущей даты и вычисление даты начала дня 7 дней назад.
    Строка 12: вычисление даты начала текущего дня.
    Строка 14: получение всех статей и количества их просмотров за последние 7 дней. Аннотации total_view_count и
    today_view_count вычисляют общее количество просмотров за 7 дней и количество просмотров за сегодняшний день,
    соответственно.
    Строка 15: запрос к связанным объектам - для улучшения производительности используется метод prefetch_related().
    Строки 17-20: сортировка статей по количеству просмотров, сначала по просмотрам за все время (total_view_count),
    затем по просмотрам за сегодня (today_view_count). Отбираются первые 10 статей.
    Строка 22: возвращение списка популярных статей.
    :return:
    """

    # получаем текущую дату и время в формате datetime
    now = timezone.now()
    # вычисляем дату начала дня (00:00) 7 дней назад
    start_date = now - timedelta(days=7)
    # вычисляем дату начала текущего дня (00:00)
    today_start = timezone.make_aware(datetime.combine(date.today(), time.min))
    # получаем все статьи и количество их просмотров за последние 7 дней
    articles = Article.objects.annotate(
        total_view_count=Count('views', filter=Q(views__viewed_on__gte=start_date)),
        today_view_count=Count('views', filter=Q(views__viewed_on__gte=today_start))
    ).prefetch_related('views')
    # сортируем статьи по количеству просмотров в порядке убывания, сначала по просмотрам за сегодня, затем за все время
    popular_articles = articles.order_by('-total_view_count', '-today_view_count')[:10]
    return popular_articles
