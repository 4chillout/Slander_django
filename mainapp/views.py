from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic.base import View
from django.template.defaultfilters import slugify
from unidecode import unidecode
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.urls import reverse_lazy


from .models import Artist, Album, Track, Comment, Rating
from .models import Genre as GenreModel
from .forms import ArtistForm, AlbumForm, ImageUploadForm, CommentForm, TrackForm, GenreForm


class Index(TemplateView):
    """
    Отображение главной страницы
    """
    template_name = 'index.html'


class Genre:
    """Отображает все жанры"""

    @staticmethod
    def get_genres():
        return GenreModel.objects.all()


class ArtistsList(Genre, ListView):
    """Страница cо статьями артистов"""
    model = Artist
    queryset = Artist.objects.filter(draft=False)
    template_name = 'artists.html'
    paginate_by = 5


class AlbumsList(Genre, ListView):
    """Страница cо статьями альбомов"""
    model = Album
    queryset = Album.objects.filter(draft=False)
    template_name = 'albums.html'
    paginate_by = 3


class TrackList(Genre, ListView):
    """Страница cо статьями песен"""
    model = Track
    queryset = Track.objects.filter(draft=False)
    template_name = 'tracks.html'
    paginate_by = 5


class ArtistDetail(Genre, DetailView):
    """Статья артиста"""
    model = Artist
    queryset = Artist.objects.filter(draft=False)
    template_name = 'artist_detail.html'

    def get_context_data(self, *args, **kwargs):
        """Отображает комментарии в статье артиста"""
        context = super().get_context_data(*args, **kwargs)
        form = CommentForm()
        context["form"] = form
        return context


class AlbumDetail(Genre, DetailView):
    """Статья альбома"""
    model = Album
    queryset = Album.objects.filter(draft=False)
    template_name = 'album_detail.html'

    def get_context_data(self, *args, **kwargs):
        """Отображает комментарии в статье альбома"""
        context = super().get_context_data(*args, **kwargs)
        form = CommentForm()
        context["form"] = form
        return context


class TrackDetail(Genre, DetailView):
    """Статья песни"""
    model = Track
    queryset = Track.objects.filter(draft=False)
    template_name = 'track_detail.html'

    def get_context_data(self, *args, **kwargs):
        """Отображает комментарии в статье песни"""
        context = super().get_context_data(*args, **kwargs)
        form = CommentForm()
        context["form"] = form
        return context


class AddRating(View):
    """Добавление рейтинга статье с артистом/альбомом/песней"""

    @staticmethod
    def get_client_ip(request):
        """Вычисляет ip, для того чтобы статье нельзя было поставить больше одного лайка с одного ip"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip    

    def update_rate(self, obj_type, id):
        """Пересчитывает рейтинг статьи"""
        obj = obj_type.objects.get(id=id)
        obj.rate = obj.calculate_rating()
        obj.save()
        return obj

    def post(self, request, id):
        """Определяет тип статьи и добавляет ей рейтинг"""
        if request.POST.get("obj-type") == 'artist':
            Rating.objects.update_or_create(ip=self.get_client_ip(request),  value=int(request.POST.get("value")),
                                            artist_id=id)
            obj = self.update_rate(obj_type=Artist, id=id)
            return redirect(obj.get_absolute_url())
        elif request.POST.get("obj-type") == 'album':
            Rating.objects.update_or_create(ip=self.get_client_ip(request),  value=int(request.POST.get("value")),
                                            album_id=id)
            obj = self.update_rate(obj_type=Album, id=id)
            return redirect(obj.get_absolute_url())
        elif request.POST.get("obj-type") == 'track':
            Rating.objects.update_or_create(ip=self.get_client_ip(request),  value=int(request.POST.get("value")),
                                            track_id=id)
            obj = self.update_rate(obj_type=Track, id=id)
            return redirect(obj.get_absolute_url())
        else:
            return HttpResponse(status=400)


class ArtistCreate(TemplateView):
    """Создает статью с артистом"""
    model = Artist
    template_name = 'artist_post.html'
    success_url = reverse_lazy('mainapp:artists')

    def get(self, request, *args, **kwargs):
        """Отображает формы"""
        if self.request.user.is_authenticated:
            context = super().get_context_data(*args, **kwargs)
            context["form"] = ArtistForm
            context["img_form"] = ImageUploadForm
            return self.render_to_response(context)
        else:
            return render(None, '404_login_required.html')
     
    def post(self, request, *args, **kwargs):
        """Проверяет наличие имени артиста в базе. Если такого артиста нет, то создает статью.
        Также создаёт статью если не загружено изображение"""
        artist_form = ArtistForm(request.POST)
        img_form = ImageUploadForm(request.POST, request.FILES)
        if artist_form.is_valid():
            if img_form.is_valid():
                img_of_artist = img_form.save()
                img_of_artist.save()
                artist_post = artist_form.save(commit=False)
                artist_post.user = self.request.user
                artist_post.save()
                artist_post.photo.add(img_of_artist)
                return redirect(artist_post.get_absolute_url())
            else:
                context = {'form': ArtistForm, "img_form": ImageUploadForm,
                           'error_message': 'Не удалось загрузить изображение'}
        else:
            query_res = Artist.objects.filter(name=self.request.POST.get("Artist-name"))
            if query_res:
                return render(request, self.template_name, {'form': ArtistForm, "img_form": ImageUploadForm,
                                                            'error_message': 'Данная статья уже существует'})
            else:
                return render(request, self.template_name, {'form': ArtistForm, "img_form": ImageUploadForm,
                                                            'error_message': 'Ошибка создания статьи'})
        return render(request, self.template_name, context)


class AlbumTrackCreateMixin(TemplateView):
    """Предок для создания статьи с альбомом/песней"""
    obj_model = None
    obj_form = None
    template_name = None
    success_url = None

    def get(self, request, *args, **kwargs):
        """Отображает формы"""
        if self.request.user.is_authenticated:
            context = super().get_context_data(*args, **kwargs)
            context["form"] = self.obj_form
            return self.render_to_response(context)
        else:
            return render(None, '404_login_required.html')

    def post(self, request, *args, **kwargs):
        """1)Проверяет наличие названия альбома/песни в базе. Если названия нет, то создает статью.
           2)При создании статьи с песней id артиста добавляется автоматически, исходя из альбома"""
        form = self.obj_form(request.POST)
        if form.is_valid():
            if self.obj_form == TrackForm:
                form.album = form.cleaned_data['album']
            else:
                form.artist = form.cleaned_data['artist']               
            obj_post = form.save(commit=False)
            obj_post.user = self.request.user
            if self.obj_form == TrackForm:
                obj_post.artist = obj_post.album.artist
            obj_post.save()
            return redirect(obj_post.get_absolute_url())
        else:
            if self.obj_form == TrackForm:
                q = 'Track-title'
            else:
                q = 'Album-title'
            query_res = self.obj_model.objects.filter(title=self.request.POST.get(q))
            if query_res:
                return render(request, self.template_name, {'form': form,
                                                            'error_message': 'Данная статья уже существует'})
            else:
                return render(request, self.template_name, {'form': form, 'error_message': 'Ошибка создания статьи'})
        

class AlbumCreate(AlbumTrackCreateMixin):
    """Создает статью с альбомом"""
    obj_model = Album
    obj_form = AlbumForm
    template_name = 'album_post.html'
    success_url = reverse_lazy('mainapp:albums')


class TrackCreate(AlbumTrackCreateMixin):
    """Создает статью с песней"""
    obj_model = Track
    obj_form = TrackForm
    template_name = 'track_post.html'
    success_url = reverse_lazy('mainapp:tracks')


class SearchMixin(Genre, ListView):
    """Предок для поиска отдельно статей с артистами, альбомами и песнями"""
    obj_model = None
    template_name = 'search_results.html'
    paginate_by = 4

    def get_queryset(self):
        """Формирует queryset для отображения на странице с результатами поиска"""
        if self.obj_model == Artist:
            return self.obj_model.objects.filter(name__icontains=self.request.GET.get("q"))
        else:
            return self.obj_model.objects.filter(title__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        """Необходимо для пагинации объектов queryset"""
        context = super().get_context_data(*args, **kwargs)
        query_name = self.request.GET.get("q")
        context["query_name"] = query_name
        context["q"] = f'q={query_name}&'
        context["obj_name"] = self.obj_model.__name__.lower()
        return context


class ArtistSearch(SearchMixin):
    """Поиск статьи артиста на странице со статьями артистов"""
    obj_model = Artist


class AlbumSearch(SearchMixin):
    """Поиск статьи альбома на странице со статьями альбомов"""
    obj_model = Album
    paginate_by = 3


class TrackSearch(SearchMixin):
    """Поиск статьи песни на странице со статьями песен"""
    obj_model = Track


class MainSearch(Genre, ListView):
    """Поиск на главной, который ищет по артистам, альбомам и песням одновременно"""
    template_name = 'main_search_results.html'
    paginate_by = 4

    def get_queryset(self):
        """Формирует queryset для отображения на странице с результатами поиска"""
        queryset = []
        artists = Artist.objects.filter(name__icontains=self.request.GET.get("q"))
        albums = Album.objects.filter(title__icontains=self.request.GET.get("q"))
        tracks = Track.objects.filter(title__icontains=self.request.GET.get("q"))
        if artists:
            queryset.extend(artists)
        if albums:
            queryset.extend(albums)
        if tracks:
            queryset.extend(tracks)
        return queryset

    def get_context_data(self, *args, **kwargs):
        """Необходимо для пагинации объектов queryset"""
        context = super().get_context_data(*args, **kwargs)
        query_name = self.request.GET.get("q")
        context["query_name"] = query_name
        context["q"] = f'q={query_name}&'
        return context


class FilterGenreMixin(Genre, ListView):
    """Предок для фильтрации отдельно статей с артистами, альбомами и песнями"""
    obj_model = None
    template_name = 'search_results.html'
    paginate_by = 4

    def get_queryset(self):
        """Удаляем повторяющиеся статьи из результатов фильтрации"""
        queryset = self.obj_model.objects.filter(Q(genres__name__in=self.request.GET.getlist("genre")))
        no_repeat_queryset = list(set(queryset))
        return no_repeat_queryset

    def get_context_data(self, *args, **kwargs):
        """Необходимо для пагинации объектов queryset"""
        context = super().get_context_data(*args, **kwargs)
        query_name_list = self.request.GET.getlist("genre")
        query_name = ", ".join(query_name_list)
        context["query_name"] = query_name
        context["genre"] = ''.join([f"genre={x}&" for x in query_name_list])
        context["obj_name"] = self.obj_model.__name__.lower()
        return context


class ArtistFilter(FilterGenreMixin):
    """Фильтр статей артистов по жанрам на странице со статьями артистов"""
    obj_model = Artist


class AlbumFilter(FilterGenreMixin):
    """Фильтр статей альбомов по жанрам на странице со статьями альбомов"""
    obj_model = Album
    paginate_by = 3


class TrackFilter(FilterGenreMixin):
    """Фильтр статей песен по жанрам на странице со статьями песен"""
    obj_model = Track


class AddGenre(TemplateView):
    """Добавляет жанр"""
    template_name = 'genre_post.html'
    model = GenreModel

    def get(self, request, *args, **kwargs):
        """Отображает формы"""
        if self.request.user.is_authenticated:
            context = super().get_context_data(*args, **kwargs)
            context["form"] = GenreForm
            return self.render_to_response(context)
        else:
            return render(None, '404_login_required.html')

    def post(self, request):
        form = GenreForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return render(None, self.template_name, {'form': form, 'error_message': 'Данный объект уже существует'})
        return render(None, 'index.html')


class AddCommentMixin(View):
    """Предок для создания комментария к любому типу статьи"""
    template_name = None
    model = Comment
    obj_model = None
    success_url = None

    def post(self, request, pk):
        """1)Если пользователь аунтифицирован то добавляет его имя в базу. 
           2)Если пользователь анонимен то имя комментатора будет отображаться как anonym"""
        form = CommentForm(request.POST)
        obj = self.obj_model.objects.get(id=pk)
        obj_name = self.obj_model.__name__.lower()
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            setattr(form, obj_name, obj)
            if self.request.user.is_authenticated:
                form.author_name = self.request.user.username
                form.user = self.request.user
            else:
                form.author_name = 'anonym'
            form.save()
        return redirect(obj.get_absolute_url())


class AddCommenttoArtist(AddCommentMixin):
    """Создает комментарий к статьей с артистом"""
    template_name = 'artist_detail.html'
    obj_model = Artist
    success_url = reverse_lazy('mainapp:artists')


class AddCommenttoAlbum(AddCommentMixin):
    """Создает комментарий к статье с альбомом"""
    template_name = 'album_detail.html'
    obj_model = Album
    success_url = reverse_lazy('mainapp:albums')


class AddCommenttoTrack(AddCommentMixin):
    """Создает комментарий к статье с песней"""
    template_name = 'track_detail.html'
    obj_model = Track
    success_url = reverse_lazy('mainapp:tracks')


class SortMixin(Genre, ListView):
    """Предок для сортировки статей по рейтингу"""
    model = None
    template_name = None
    paginate_by = 5

    def get_queryset(self):
        """Определяем тип сортировки (по убыванию или возрастанию рейтинга) и формируем queryset"""
        if self.request.GET.get("sort-type") == 'up-to-down':
            return self.model.objects.filter(draft=False).order_by('-rate')
        else:
            return self.model.objects.filter(draft=False).order_by('rate')

    def get_context_data(self, *args, **kwargs):
        """Необходимо для пагинации объектов queryset"""
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get("sort-type")
        context["q"] = f'sort-type={query}&'
        return context


class SortingArtists(SortMixin):
    """Страница со статьями артистов, отсортированных по рейтингу"""
    model = Artist
    template_name = 'artists.html'


class SortingAlbums(SortMixin):
    """Страница со статьями альбомов, отсортированных по рейтингу"""
    model = Album
    template_name = 'albums.html'
    paginate_by = 3


class SortingTracks(SortMixin):
    """Страница со статьями песен, отсортированных по рейтингу"""
    model = Track
    template_name = 'tracks.html'


@method_decorator(login_required, name='dispatch')
class ArtistDelete(DeleteView):
    """Удаление статьи с артистом"""
    model = Artist
    success_url = reverse_lazy('mainapp:artists')


@method_decorator(login_required, name='dispatch')
class ArtistUpdate(UpdateView):
    """Редактирование статьи с артистом"""
    model = Artist
    form_class = ArtistForm
    template_name = 'artist_post.html'
    success_url = reverse_lazy('mainapp:artists')

    def get_context_data(self, *args, **kwargs):
        """Отображает форму загрузки изображения"""
        context = super().get_context_data(*args, **kwargs)
        context["img_form"] = ImageUploadForm
        return context

    @staticmethod
    def generate_new_slug(artist_name, album_title, track_title=None):
        """Генерирует slug в зависимости от типа статьи"""
        if track_title is None:
            new_slug = 'album_' + str(artist_name) + '-' + str(album_title)
        else:
            new_slug = 'track_' + str(artist_name) + '-' + str(album_title) + '-' + str(track_title)
        return new_slug 

    def data_transfer_and_save(self, artist_form, obj):
        """1)Переносит данные из формы в бд, сохраняет статью. Создана для отсутствии повторяемости кода
           2)При изменении имени артиста изменяет slug его альбомов и песен"""
        self.object = obj
        if artist_form.cleaned_data['genres'] != []:
            self.object.genres.set(artist_form.cleaned_data['genres'])
        artist_form.name = artist_form.cleaned_data['name']
        self.object.slug = slugify(unidecode(artist_form.cleaned_data['name']))
        self.object.biography = artist_form.cleaned_data['biography']
        if self.object.name != artist_form.name:
            albums = Album.objects.filter(artist__name=self.object.name)
            tracks = Track.objects.filter(artist__name=self.object.name)
            for album in albums:
                new_slug_for_album = self.generate_new_slug(artist_form.name, album.title)
                album.slug = slugify(unidecode(new_slug_for_album))
                album.save()
            for track in tracks:
                album_title = Album.objects.get(id=track.album_id)
                new_slug_for_track = self.generate_new_slug(artist_form.name, album_title.title,
                                                            track_title=track.title)
                track.slug = slugify(unidecode(new_slug_for_track))
                track.save()
        self.object.name = artist_form.name
        self.object.save()

    def post(self, request, *args, **kwargs):
        """1)Изменять статью может только пользователь создавший её
           2)Проверяет наличие имени артиста в базе. Если кол-во статей с таким же именем больше 1
           то изменить статью нельзя
           3)Заменяет фотографию артиста, если в форму загружено изображение.
           Если изображение не загружено то оставляет прежнее изображение.
           4)Заменяет жанры, если в форме отмечены жанры
           5)Обновляет slug у статьи. Также обновляет slug песни если изменилось название альбома"""
        artist_form = self.form_class(request.POST)
        img_form = ImageUploadForm(request.POST, request.FILES)
        self.object = self.get_object()
        if artist_form.is_valid():
            query_res = Artist.objects.filter(name=artist_form.cleaned_data['name'])
            if self.request.user.id != self.object.user.id:
                return render(None, self.template_name, {'forms': artist_form,
                                                         'error_message': 'Данную статью может редактировать '
                                                                          'только создавший её пользователь'})
            if len(query_res) > 1:
                return render(None, self.template_name,
                              {'form': artist_form, 'img_form': img_form,
                               'error_message': 'Нельзя назвать статью с уже существующим именем'})
            else:
                if img_form.is_valid() and (img_form.cleaned_data.get('original') is not None or
                                            img_form.cleaned_data['image_url'] is not None):
                    img_of_artist = img_form.save()
                    img_of_artist.save()
                    if img_of_artist.original is not None:
                        self.object.photo.clear()
                        self.object.photo.add(img_of_artist)
                    self.data_transfer_and_save(artist_form, self.object)
                    return redirect(self.object.get_absolute_url())
                elif img_form.is_valid() and (img_form.cleaned_data.get('original') is None or
                                              img_form.cleaned_data['image_url'] is None):
                    self.data_transfer_and_save(artist_form, self.object)
                    return redirect(self.object.get_absolute_url())
                else:
                    context = {'form': artist_form, 'img_form': img_form,
                               'error_message': 'Не удалось загрузить изображение'}
                    return render(request, self.template_name, context)                
        return super(ArtistUpdate, self).post(request, **kwargs)


@method_decorator(login_required, name='dispatch')
class AlbumTrackUpdateMixin(UpdateView):
    """Предок для редактирования статьи с альбомом/песней"""
    model = None
    form_class = None
    template_name = None

    @staticmethod
    def generate_new_slug(artist_name, album_title, track_title=None):
        """Генерирует slug в зависимости от типа статьи"""
        if track_title is None:
            new_slug = 'album_' + str(artist_name) + '-' + str(album_title)
        else:
            new_slug = 'track_' + str(artist_name) + '-' + str(album_title) + '-' + str(track_title)
        return new_slug

    @staticmethod
    def url_to_html_widget(self, url):
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

    def check_title(self, form_title):
        """Если при редактировании изменилось название статьи,
         то метод проверяет наличие статьи в базе с таким же названием"""
        if self.object.title != form_title:
            query_res = self.model.objects.filter(title=form_title)
            return query_res
        else:
            return None

    def post(self, request, *args, **kwargs):
        """1)Изменять статью может только пользователь создавший её
           2)Нельзя изменить название статьи на уже существующее
           3)Обновляет привязку к артисту/альбому
           4)Обновляет html-виджет
           5)Заменяет жанры, если в форме отмечены жанры
           6)Обновляет slug у статьи. Также обновляет slug песни если изменилось название альбома"""
        """!Если в форме не отметить жанры, то все жанры очистятся у обьекта"""
        form = self.form_class(request.POST)
        self.object = self.get_object()
        if form.is_valid():
            if self.form_class == AlbumForm:
                form.artist = form.cleaned_data['artist']
                form.title = form.cleaned_data['title']
                query_res = self.check_title(form.title)
                if self.request.user.id != self.object.user.id:
                    return render(None, self.template_name, {'forms': self.form_class,
                                                             'error_message': 'Данный объект может редактировать '
                                                                              'только создавший его пользователь'})
                if query_res:
                    return render(None, self.template_name, {'forms': self.form_class,
                                                             'error_message': 'Данный объект уже существует в базе'})
                else:
                    if form.cleaned_data['url'] != self.object.url:
                        self.object.url = form.cleaned_data['url']
                        self.object.html = self.url_to_html_widget(self.object.url)
                    new_slug = self.generate_new_slug(form.artist, form.title)
                    self.object.slug = slugify(unidecode(new_slug))
                    self.object.save()
                    if self.object.title != form.title:
                        tracks = Track.objects.filter(album__title=self.object.title)
                        for track in tracks:
                            artist_name = Artist.objects.get(id=track.artist_id)
                            new_slug_for_track = self.generate_new_slug(artist_name, form.title,
                                                                        track_title=track.title)
                            track.slug = slugify(unidecode(new_slug_for_track))
                            track.save()
            if self.form_class == TrackForm:
                form.album = form.cleaned_data['album']
                form.title = form.cleaned_data['title']
                query_res = self.check_title(form.title)
                if self.request.user.id != self.object.user.id:
                    return render(None, self.template_name, {'forms': self.form_class,
                                                             'error_message': 'Данный объект может редактировать '
                                                                              'только создавший его пользователь'})
                if query_res:
                    return render(None, self.template_name, {'forms': self.form_class,
                                                             'error_message': 'Данный объект уже существует в базе'})
                else:
                    if form.cleaned_data['url'] != self.object.url:
                        self.object.url = form.cleaned_data['url']
                        self.object.html = self.url_to_html_widget(self.object.url)
                    self.object.artist = form.album.artist
                    new_slug = self.generate_new_slug(self.object.artist.name, form.album.title, track_title=form.title)
                    self.object.slug = slugify(unidecode(new_slug))
                    self.object.save()               
        return super(AlbumTrackUpdateMixin, self).post(request, **kwargs)


@method_decorator(login_required, name='dispatch')
class AlbumDelete(DeleteView):
    """Удаление статьи с альбомом"""
    model = Album
    success_url = reverse_lazy('mainapp:albums')


class AlbumUpdate(AlbumTrackUpdateMixin):
    """Редактирование статьи с альбомом"""
    model = Album
    form_class = AlbumForm
    success_url = reverse_lazy('mainapp:albums')
    template_name = 'album_post.html'


@method_decorator(login_required, name='dispatch')
class TrackDelete(DeleteView):
    """Удаление статьи с песней"""
    model = Track
    success_url = reverse_lazy('mainapp:tracks')


class TrackUpdate(AlbumTrackUpdateMixin):
    """Редактирование статьи с песней"""
    model = Track
    form_class = TrackForm
    success_url = reverse_lazy('mainapp:tracks')
    template_name = 'track_post.html'

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