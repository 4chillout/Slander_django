# Generated by Django 3.0.9 on 2022-09-06 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20220906_2230'),
        ('authapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='userpic',
            field=models.ManyToManyField(blank=True, to='mainapp.Image', verbose_name='Фото пользователя'),
        ),
    ]
