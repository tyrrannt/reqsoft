from django.apps import AppConfig


class CustomeuserAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customeuser_app'
    verbose_name = 'Профили пользователей'
    verbose_name_plural = 'Профиль пользователя'
