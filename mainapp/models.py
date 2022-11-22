from django.db import models
from datetime import date
from django.urls import reverse
from django.template.defaultfilters import slugify
from unidecode import unidecode
from django.db.models import Sum
from django.db.utils import OperationalError, ProgrammingError
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import MaxValueValidator, MinValueValidator
from authapp.models import User


class Genre(models.Model):
    """Жанры"""
    name = models.CharField("Название", max_length=100, unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_genre_choices():
        """Отображает все жанры на главной странице и в формах при создании статей"""
        all_genres = []
        try:
            genres = Genre.objects.all()
            for genre in genres:
                one_genre = (str(genre.id), str(genre.name))
                all_genres.append(one_genre)
            return all_genres
        except OperationalError:
            return all_genres
        except ProgrammingError:
            return all_genres     
        except ImproperlyConfigured:
            return all_genres     

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Image(models.Model):
    """"Изображения"""
    original = models.ImageField(upload_to='artists', blank=True, null=True,
                                 verbose_name='Или загрузите изображение с ПК')
    image_url = models.URLField(null=True, blank=True, verbose_name='Загрузите изображение, вставив ссылку на него')
    height = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Высота',
                                              validators=[
                                                  MaxValueValidator(10000),
                                                  MinValueValidator(1)])
    width = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Ширина',
                                             validators=[
                                                 MaxValueValidator(10000),
                                                 MinValueValidator(1)])

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Artist(models.Model):
    """Статья посвящённая артисту"""
    name = models.CharField('Имя артиста/группы', max_length=100)
    biography = models.TextField('Биография артиста/группы', default='', blank=True)
    genres = models.ManyToManyField(Genre, verbose_name="жанры")
    photo = models.ManyToManyField(Image, verbose_name="Фото артиста", blank=True)
    rate = models.IntegerField('Значение рейтинга', default=0)
    draft = models.BooleanField("Черновик", default=False)
    slug = models.SlugField(max_length=250, default='', blank=True)
    user = models.ForeignKey(User, verbose_name="Пользователь создавший статью", on_delete=models.CASCADE,
                             related_name='artist_user', default='')

    def __str__(self):
        return self.name

    @staticmethod
    def get_model_type():
        """Используется в поиске на главной"""
        return "artists"

    def save(self):
        """Генерирует slug при создании артиста"""
        if not self.id:
            self.slug = slugify(unidecode(self.name))
        super(Artist, self).save()

    def get_absolute_url(self):
        """Ссылка на артиста"""
        slug = slugify(unidecode(self.name))
        args = [slug, ]
        return reverse('mainapp:artist_detail', args=args)
    
    def calculate_rating(self):
        """Высчитывает и отображает рейтинг к артисту"""
        rate_dict = self.rating_set.filter(parent__isnull=True).filter(artist_id=self.id).aggregate(Sum('value'))
        rate = rate_dict.get('value__sum')
        return rate    

    def get_comments(self):
        """Отображает комментарии к артисту"""
        comments = self.comment_set.filter(parent__isnull=True)
        return comments

    def get_quantity_comments(self):
        """Отображает число комментариев к артисту"""
        comments = self.get_comments()
        return len(comments)
    
    def get_photo(self):
        """Отображает фотографию артиста если она существует"""
        img = Image.objects.filter(artist__id=self.id)
        if img:
            for image in img:
                artist_photo = image.original
                return artist_photo
        else:
            return None

    class Meta:
        ordering = ['-id']
        verbose_name = 'Артист'
        verbose_name_plural = "Артисты"


class Album(models.Model):
    """Статья посвящанная альбому"""
    artist = models.ForeignKey(Artist, verbose_name="Артист/группа", on_delete=models.CASCADE,
                               related_name='artist_album')
    title = models.CharField('Название альбома', max_length=150)
    description = models.TextField('Описание альбома', default='', blank=True)
    genres = models.ManyToManyField(Genre, verbose_name="Жанры")
    published_date = models.DateField("Дата релиза", default=date.today)
    url = models.URLField('Ссылка на альбом со Spotify или Яндекс.Музыка', default='', blank=True)
    html = models.TextField('html код для отображения альбома', default='', blank=True)
    rate = models.IntegerField('Значение рейтинга', default=0)
    draft = models.BooleanField("Черновик", default=False)
    slug = models.SlugField(max_length=250, default='', blank=True)
    user = models.ForeignKey(User, verbose_name="Пользователь создавший статью", on_delete=models.CASCADE,
                             related_name='album_user', default='')

    def __str__(self):
        return f"{self.artist} - {self.title}"

    @staticmethod
    def get_model_type():
        """Используется в поиске на главной"""
        return "albums"

    def url_to_html_widget(self):
        """Преобразует ссылку на альбом со стриминга в виджет html"""
        if 'spotify' in self.url:
            self.url = self.url[:25] + 'embed/' + self.url[25:55] + '?utm_source=generator'
            return f'<iframe style="border-radius:12px" src="{self.url}" width="100%" height="380" frameBorder="0"' \
                   f' allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen;' \
                   f' picture-in-picture" loading="lazy"></iframe>'
        elif 'yandex' in self.url:
            self.url = self.url[:24] + 'iframe/#' + self.url[24:]
            return f'<iframe frameborder="0" style="border:none;width:100%;height:450px;" width="100%" height="450"' \
                   f' src="{self.url}"></iframe>'
        else:
            return ''
    
    def save(self):
        """Генерирует slug и html при создании/изменении альбома"""
        if not self.id:
            album_name = 'album_' + str(self.artist.name) + '-' + str(self.title)
            self.slug = slugify(unidecode(album_name))
            self.html = self.url_to_html_widget()
            super(Album, self).save()
        else:
            super(Album, self).save()    
    
    def get_absolute_url(self):
        """Ссылка на альбом"""
        album_name = 'album_' + str(self.artist.name) + '-' + str(self.title)
        slug = slugify(unidecode(album_name))
        args = [slug, ]
        return reverse('mainapp:album_detail', args=args)

    def get_comments(self):
        """Отображает комментарии к альбому"""
        comments = self.comment_set.filter(parent__isnull=True)
        return comments

    def get_quantity_comments(self):
        """Отображает число комментариев к альбому"""
        comments = self.get_comments()
        return len(comments)

    def calculate_rating(self):
        """Высчитывает и отображает рейтинг к альбому"""
        rate_dict = self.rating_set.filter(parent__isnull=True).filter(album_id=self.id).aggregate(Sum('value'))
        rate = rate_dict.get('value__sum')
        return rate
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Альбом'
        verbose_name_plural = "Альбомы"


class Track(models.Model):
    """Статья посвящанная песне"""
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="Имя артиста/группы",
                               related_name='track_artist')
    other_artist = models.ForeignKey(Artist, on_delete=models.CASCADE,
                                     verbose_name="Имя приглашённого артиста/группы",
                                     help_text='Укажите, если это feat', related_name='track_other_artist',
                                     default='', blank=True, null=True)
    title = models.CharField('Название песни', max_length=70)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, verbose_name="Альбом/EP", related_name='trak_on_album')
    genres = models.ManyToManyField(Genre, verbose_name="жанры")
    description = models.TextField('О песне', default='', blank=True)
    url = models.URLField('Ссылка на песню со Spotify или Яндекс.Музыка', default='', blank=True)
    html = models.TextField('html код для отображения песни', default='', blank=True)
    rate = models.IntegerField('Значение рейтинга', default=0)
    draft = models.BooleanField("Черновик", default=False)
    slug = models.SlugField(max_length=250, default='', blank=True)
    user = models.ForeignKey(User, verbose_name="Пользователь создавший статью", on_delete=models.CASCADE,
                             related_name='track_user', default='')

    def __str__(self):
        if self.other_artist:
            return f"{self.artist} feat {self.other_artist} - {self.title}"
        else:
            return f"{self.artist.name} - {self.title}"

    @staticmethod
    def get_model_type():
        """Используется в поиске на главной"""
        return "tracks"

    def url_to_html_widget(self):
        """Преобразует ссылку на песню со стриминга в виджет html"""
        if 'spotify' in self.url:
            self.url = self.url[:25] + 'embed/' + self.url[25:53] + '?utm_source=generator'
            return f'<iframe style="border-radius:12px" src="{self.url}"' \
                   f' width="100%" height="380" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write;' \
                   f' encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        elif 'yandex' in self.url:
            self.url = self.url[:24] + 'iframe/#track/' + self.url.split('/')[-1] + '/' + self.url.split('/')[-3]
            return f'<iframe frameborder="0" style="border:none;width:100%;height:180px;" width="100%" height="180" ' \
                   f'src="{self.url}"></iframe>'
        else:
            return ''
    
    def save(self):
        """Генерирует slug и html при создании/изменении трека"""
        if not self.id:
            track_name = 'track_' + str(self.artist.name) + '-' + str(self.album.title) + '-' + str(self.title)
            self.slug = slugify(unidecode(track_name))
            self.html = self.url_to_html_widget()
            super(Track, self).save()
        else:
            super(Track, self).save()
    
    def get_absolute_url(self):
        """Ссылка на песню"""
        track_name = 'track_' + str(self.artist.name) + '-' + str(self.album.title) + '-' + str(self.title)
        slug = slugify(unidecode(track_name))
        args = [slug, ]
        return reverse('mainapp:track_detail', args=args)

    def get_comments(self):
        """Отображает комментарии к песне"""
        comments = self.comment_set.filter(parent__isnull=True)
        return comments

    def get_quantity_comments(self):
        """Отображает число комментариев к песне"""
        comments = self.get_comments()
        return len(comments)

    def calculate_rating(self):
        """Высчитывает и отображает рейтинг к песне"""
        rate_dict = self.rating_set.filter(parent__isnull=True).filter(track_id=self.id).aggregate(Sum('value'))
        rate = rate_dict.get('value__sum')
        return rate

    def get_published_date(self):
        """Отображает дату публикации альбома"""
        if self.album:
            return f"{self.album.published_date}"
        else:
            return "Укажите альбом"

    class Meta:
        ordering = ['-id']        
        verbose_name = 'Песня'
        verbose_name_plural = "Песни"


class Comment(models.Model):
    """Комментарии. Могут оставлять как и анонимы, так и зарегестрированные пользователи"""
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, default='',
                             blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, blank=True, null=True)
    author_name = models.CharField('Имя комментатора', max_length=50)
    comment_text = models.TextField('Текст комментария', max_length=1000)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return f"{self.author_name} - {self.comment_text}"

    def get_user_pic(self):
        """Отображение аватарки комментатора"""
        if self.user:
            if self.user.socialaccount_set.all():
                return self.user.socialaccount_set.all()[0].extra_data['photo_big']
            else:
                return self.user.get_userpic()
        else:
            return '/static/images/no-photo.gif'
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = "Комментарии"
    

class Rating(models.Model):
    """Рейтинг. Предусмотрен для каждого типа статьи"""
    ip = models.CharField("IP адрес", max_length=15)
    value = models.IntegerField('Значение', default=0)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="артист", blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, verbose_name="альбом", blank=True, null=True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name="песня", blank=True, null=True)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"
