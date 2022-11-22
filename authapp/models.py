from django.contrib.auth.models import AbstractUser
from django.db import models
import mainapp.models


class User(AbstractUser):
    """
    Модель пользователя
    """
    username = models.CharField(verbose_name='Имя пользователя', max_length=30, unique=True, blank=False)
    email = models.EmailField(verbose_name='Электронная почта', unique=True)
    userpic = models.ManyToManyField("mainapp.Image", verbose_name="Фото пользователя", blank=True)

    def get_userpic(self):
        """Отображение аватарки пользователя если она существует"""
        image_model = mainapp.models.Image()
        img = image_model.__class__.objects.filter(user__id=self.id)
        if img:
            for image in img:
                user_photo = image.original
                return user_photo.url if user_photo != '' else '/static/images/no-photo.gif'
        else:
            return '/static/images/no-photo.gif'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
