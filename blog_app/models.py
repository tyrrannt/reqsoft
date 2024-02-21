from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager
from taggit.models import Tag

from reqsoft.utils import unique_slugify

# Create your models here.
"""
get_user_model() - это удобный способ получить модель пользователя, определенную в проекте Django. Вместо того, чтобы 
явно импортировать модель пользователя (from django.contrib.auth.models import User), get_user_model() возвращает модель 
пользователя, которая настроена в настройках проекта (AUTH_USER_MODEL).

Основные преимущества использования get_user_model():

Гибкость: get_user_model() возвращает текущую модель пользователя проекта, что позволяет изменить модель пользователя, 
используемую в проекте, без необходимости изменения кода.
Портативность: использование get_user_model() позволяет вашему коду быть переносимым между различными проектами Django, 
где может быть использована различная модель пользователя.
Расширяемость: если вы расширяете модель пользователя проекта, например, добавляете новые поля, использование 
get_user_model() обеспечивает совместимость с этими изменениями, не нарушая стандартных возможностей аутентификации 
Django.
Кроме того, использование get_user_model() вместо явного импорта модели пользователя упрощает написание тестов, так 
как тесты не будут зависеть от конкретной модели пользователя.
"""
User = get_user_model()


class Article(models.Model):
    """
    Модель постов для сайта
    """

    class ArticleManager(models.Manager):
        """
        Кастомный менеджер для модели статей
        """

        def all(self):
            """
            Список статей (SQL запрос с фильтрацией для страницы списка статей)
            """
            return (self.get_queryset().select_related('author', 'category')
                    .prefetch_related('ratings', 'views').filter(status='published'))

        def detail(self):
            """
            Детальная статья (SQL запрос с фильтрацией для страницы со статьёй)
            добавляем метод detail(), который можем использовать в представлениях, например в DetailView,
            который оптимизирует SQL запросы.
            А в представлении DetailView добавляем строку: queryset = model.objects.detail()
            """
            return self.get_queryset()\
                .select_related('author', 'category')\
                .prefetch_related('comments', 'comments__author', 'comments__author__profile', 'tags')\
                .filter(status='published')

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    title = models.CharField(verbose_name='Заголовок', max_length=255)
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    short_description = models.TextField(verbose_name='Краткое описание', max_length=500)
    full_description = RichTextField(verbose_name='Полное описание', extra_plugins=['codesnippet'],)
    thumbnail = models.ImageField(
        verbose_name='Превью поста',
        blank=True,
        upload_to='images/thumbnails/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )
    status = models.CharField(choices=STATUS_OPTIONS, default='draft', verbose_name='Статус поста', max_length=10)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    author = models.ForeignKey(to=User, verbose_name='Автор', on_delete=models.SET_DEFAULT, related_name='author_posts',
                               default=1)
    updater = models.ForeignKey(to=User, verbose_name='Обновил', on_delete=models.SET_NULL, null=True,
                                related_name='updater_posts', blank=True)
    fixed = models.BooleanField(verbose_name='Зафиксировано', default=False)
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='articles', verbose_name='Категория')
    tags = TaggableManager()

    objects = ArticleManager()

    class Meta:
        """
        ordering - сортировка, ставим -created_at, чтобы выводились статьи в обратном порядке (сначала новые, потом старые).
        verbose_name - название модели в админке в ед.ч
        verbose_name_plural - в мн.числе
        db_table - название таблицы в БД. (можно не добавлять, будет создано автоматически)
        indexes - индексирование полей, чтобы ускорить результаты сортировки.
        """
        db_table = 'app_articles'
        ordering = ['-fixed', '-time_create']
        indexes = [models.Index(fields=['-fixed', '-time_create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_app:article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def get_objects(self):
        return self

    def get_view_count(self):
        """
        Возвращает количество просмотров для данной статьи
        """
        return self.views.count()


class Category(MPTTModel):
    """
    Модель категорий с вложенностью
    """
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, verbose_name='URL категории', blank=True)
    description = models.TextField(verbose_name='Описание категории', max_length=300)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class MPTTMeta:
        """
        Сортировка по вложенности
        """
        order_insertion_by = ('title',)

    class Meta:
        """
        Сортировка, название модели в админ панели, таблица в данными
        """
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'

    def __str__(self):
        """
        Возвращение заголовка статьи
        """
        return self.title

    def get_absolute_url(self):
        return reverse('blog_app:articles_by_category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)


class Comment(MPTTModel):
    """
    Модель древовидных комментариев
    С помощью библиотеки MPTT создаем древовидную систему комментариев.
    Ссылаемся на Article, так как комментарий закрепляется за статьей.
    Ссылаемся на User (автора комментария).
    Добавляем индексы для сортировки, получения оптимизированных результатов.
    order_insertion_by - сортировка по вложенности
    """

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'),
        ('draft', 'Черновик')
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья', related_name='comments')
    author = models.ForeignKey(User, verbose_name='Автор комментария', on_delete=models.CASCADE, related_name='comments_author')
    content = models.TextField(verbose_name='Текст комментария', max_length=3000)
    time_create = models.DateTimeField(verbose_name='Время добавления', auto_now_add=True)
    time_update = models.DateTimeField(verbose_name='Время обновления', auto_now=True)
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    class MTTMeta:
        order_insertion_by = ('-time_create',)

    class Meta:
        db_table = 'app_comments'
        indexes = [models.Index(fields=['-time_create', 'time_update', 'status', 'parent'])]
        ordering = ['-time_create']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author}:{self.content}'


class ViewCount(models.Model):
    """
    Модель просмотров для статей
    article - это внешний ключ, связывающий просмотр с соответствующей статьей.
    ip_address - это поле для хранения IP-адреса пользователя, который просмотрел статью.
    viewed_on - это поле для хранения даты и времени просмотра статьи.
    Мы также определяем два дополнительных параметра для нашей модели: Meta и str(). Параметр Meta содержит информацию
    о сортировке и индексировании модели, а также о ее имени и множественном числе для отображения в административном
    интерфейсе. Параметр str() определяет строковое представление объекта модели, которое будет отображаться в
    административном интерфейсе.
    """
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес')
    viewed_on = models.DateTimeField(auto_now_add=True, verbose_name='Дата просмотра')

    class Meta:
        ordering = ('-viewed_on',)
        indexes = [models.Index(fields=['-viewed_on'])]
        verbose_name = 'Просмотр'
        verbose_name_plural = 'Просмотры'

    def __str__(self):
        return self.article.title