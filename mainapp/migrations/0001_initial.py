# Generated by Django 3.0.9 on 2022-07-13 18:36

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Название альбома')),
                ('description', models.TextField(blank=True, default='', verbose_name='Описание альбома')),
                ('published_date', models.DateField(default=datetime.date.today, verbose_name='Дата релиза')),
                ('url', models.URLField(blank=True, default='', verbose_name='Ссылка на альбом со Spotify или Яндекс.Музыка')),
                ('html', models.TextField(blank=True, default='', verbose_name='html код для отображения альбома')),
                ('rate', models.IntegerField(default=0, verbose_name='Значение рейтинга')),
                ('draft', models.BooleanField(default=False, verbose_name='Черновик')),
                ('slug', models.SlugField(blank=True, default='', max_length=250)),
            ],
            options={
                'verbose_name': 'Альбом',
                'verbose_name_plural': 'Альбомы',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя артиста/группы')),
                ('biography', models.TextField(blank=True, default='', verbose_name='Биография артиста/группы')),
                ('rate', models.IntegerField(default=0, verbose_name='Значение рейтинга')),
                ('draft', models.BooleanField(default=False, verbose_name='Черновик')),
                ('slug', models.SlugField(blank=True, default='', max_length=250)),
            ],
            options={
                'verbose_name': 'Артист',
                'verbose_name_plural': 'Артисты',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original', models.ImageField(blank=True, null=True, upload_to='artists', verbose_name='Или загрузите изображение с ПК')),
                ('image_url', models.URLField(blank=True, null=True, verbose_name='Загрузите изображение, вставив ссылку на него')),
                ('height', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(1)], verbose_name='Высота')),
                ('width', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(1)], verbose_name='Ширина')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=70, verbose_name='Название песни')),
                ('description', models.TextField(blank=True, default='', verbose_name='О песне')),
                ('url', models.URLField(blank=True, default='', verbose_name='Ссылка на песню со Spotify или Яндекс.Музыка')),
                ('html', models.TextField(blank=True, default='', verbose_name='html код для отображения песни')),
                ('rate', models.IntegerField(default=0, verbose_name='Значение рейтинга')),
                ('draft', models.BooleanField(default=False, verbose_name='Черновик')),
                ('slug', models.SlugField(blank=True, default='', max_length=250)),
                ('album', models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='trak_on_album', to='mainapp.Album', verbose_name='Альбом/EP')),
                ('artist', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='track_artist', to='mainapp.Artist', verbose_name='Имя артиста/группы')),
                ('genres', models.ManyToManyField(to='mainapp.Genre', verbose_name='жанры')),
                ('other_artist', models.ForeignKey(blank=True, default='', help_text='Укажите, если это feat', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='track_other_artist', to='mainapp.Artist', verbose_name='Имя приглашённого артиста/группы')),
                ('user', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='track_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь создавший статью')),
            ],
            options={
                'verbose_name': 'Песня',
                'verbose_name_plural': 'Песни',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=15, verbose_name='IP адрес')),
                ('value', models.IntegerField(default=0, verbose_name='Значение')),
                ('album', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Album', verbose_name='альбом')),
                ('artist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Artist', verbose_name='артист')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.Rating', verbose_name='Родитель')),
                ('track', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Track', verbose_name='песня')),
            ],
            options={
                'verbose_name': 'Рейтинг',
                'verbose_name_plural': 'Рейтинги',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(max_length=50, verbose_name='Имя комментатора')),
                ('comment_text', models.TextField(max_length=1000, verbose_name='Текст комментария')),
                ('album', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Album')),
                ('artist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Artist')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.Comment', verbose_name='Родитель')),
                ('track', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Track')),
                ('user', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
            },
        ),
        migrations.AddField(
            model_name='artist',
            name='genres',
            field=models.ManyToManyField(to='mainapp.Genre', verbose_name='жанры'),
        ),
        migrations.AddField(
            model_name='artist',
            name='photo',
            field=models.ManyToManyField(blank=True, to='mainapp.Image', verbose_name='Фото артиста'),
        ),
        migrations.AddField(
            model_name='artist',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='artist_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь создавший статью'),
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artist_album', to='mainapp.Artist', verbose_name='Артист/группа'),
        ),
        migrations.AddField(
            model_name='album',
            name='genres',
            field=models.ManyToManyField(to='mainapp.Genre', verbose_name='Жанры'),
        ),
        migrations.AddField(
            model_name='album',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='album_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь создавший статью'),
        ),
    ]