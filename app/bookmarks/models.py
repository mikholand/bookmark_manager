from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    url = models.URLField(verbose_name='Ссылка на страницу')
    bookmark_type = models.CharField(max_length=20, default='website', verbose_name='Тип ссылки')
    preview_image = models.URLField(verbose_name='Превью')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    collections = models.ManyToManyField('Collection', related_name='bookmarks', verbose_name='Коллекция')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookmark', kwargs={'bookmark_id': self.pk})

    class Meta:
        app_label = 'bookmarks'
        db_table = 'bookmarks'
        verbose_name = 'Закладка'
        verbose_name_plural = 'Закладки'


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('collection', kwargs={'collection_id': self.pk})

    class Meta:
        app_label = 'bookmarks'
        db_table = 'collections'
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
