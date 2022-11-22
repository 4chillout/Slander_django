from django import forms
from .models import Album, Rating, Artist, Image, Comment, Track, Genre
from urllib.parse import urlparse
import requests
from PIL import Image as Img
from urllib import request
from django.core.files.base import ContentFile


class ImageUploadForm(forms.ModelForm):
    """
    Валидация ссылки и уникальности заполнение полей ввода
    !не выводятся ошибки формы кроме error_message со вьюхи
    """
    prefix = 'Image'

    class Meta:
        model = Image
        fields = ['image_url', 'original']

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data['image_url'] and cleaned_data['original']:
            raise forms.ValidationError('Заполните только одно поле ввода!')
        if cleaned_data['image_url']:  # валидация и загрузка картинки по URL
            try:
                resp = requests.get(cleaned_data['image_url'], stream=True).raw
            except requests.exceptions.RequestException as e:
                raise forms.ValidationError('Нерабочая ссылка!')
            try:
                img = Img.open(resp)
            except IOError:
                raise forms.ValidationError('Невозможно открыть файл картинки!')
        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True):
        cleaned_data = self.cleaned_data
        original = super(ImageUploadForm, self).save(commit=False)
        if cleaned_data['image_url']:
            image_url = self.cleaned_data['image_url']
            image_name = urlparse(cleaned_data['image_url']).path.split('/')[-1].lower()
            response = request.urlopen(image_url)
            original.original.save(image_name, ContentFile(response.read()), save=False)
        if commit:
            original.save()
        return original


class RatingForm(forms.ModelForm):
    """Форма добавления рейтинга"""
    class Meta:
      model = Rating
      fields = ('ip', 'value', 'artist')


class GenreForm(forms.ModelForm):
    """Форма добавления жанра"""
    class Meta:
      model = Genre
      fields = ['name']


class ArtistForm(forms.ModelForm):
    """Форма создания статьи с артистом"""
    prefix = 'Artist'
    GENRE_CHOICES = Genre().get_genre_choices()
    genres = forms.MultipleChoiceField(label='Жанры', required=False,
                                       widget=forms.CheckboxSelectMultiple(),
                                       choices=GENRE_CHOICES,)

    class Meta:
        model = Artist
        fields = ['name', 'biography', 'genres']


class AlbumForm(forms.ModelForm):
    """Форма создания статьи с альбомом"""
    prefix = 'Album'
    GENRE_CHOICES = Genre().get_genre_choices()
    genres = forms.MultipleChoiceField(label='Жанры', required=False,
                                       widget=forms.CheckboxSelectMultiple(),
                                       choices=GENRE_CHOICES,)
    published_date = forms.DateField(label='Дата релиза', widget=forms.DateInput(format='%d-%m-%Y',
                                     attrs={'type': 'date'}))

    class Meta:
        model = Album
        fields = ['title', 'description', 'artist', 'published_date', 'genres', 'url']


class TrackForm(forms.ModelForm):
    """Форма создания статьи с песней"""
    prefix = 'Track'
    GENRE_CHOICES = Genre().get_genre_choices()
    genres = forms.MultipleChoiceField(label='Жанры', required=False,
                                       widget=forms.CheckboxSelectMultiple(),
                                       choices=GENRE_CHOICES,)

    class Meta:
        model = Track
        fields = ['title', 'album', 'other_artist', 'description', 'genres', 'url']


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""
    prefix = 'Comment'

    class Meta:
        model = Comment
        fields = ["comment_text"]
