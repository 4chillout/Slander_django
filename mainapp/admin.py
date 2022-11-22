from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Artist, Album, Track, Comment, Genre


admin.site.register(Genre)
admin.site.register(Comment)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    fields = ('name', 'biography', 'genres', 'photo', 'get_image', 'draft')
    list_display = ('get_image', 'name', 'draft')
    list_display_links = ('get_image', "name")
    readonly_fields = ("get_image",)
    search_fields = ("name",)
    list_editable = ("draft",)

    def get_image(self, obj):
        if obj.photo:
            return mark_safe(f'<img src={obj.photo} width="100" height="90"')
        else:
            return "Фотографии артиста нет"

    get_image.short_description = "Фото артиста"


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('artist', 'title', 'draft')
    list_display_links = ('title',)
    list_filter = ('artist__name', 'title')
    search_fields = ('artist__name', 'title')
    list_editable = ("draft",)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('artist', 'title', 'draft')
    list_display_links = ('title',)
    list_filter = ('artist', 'album__title', 'title')
    search_fields = ('artist__name', 'title', 'album__title')
    list_editable = ("draft",)
    save_on_top = True