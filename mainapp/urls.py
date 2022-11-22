from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.template import RequestContext
from . import views
app_name = 'mainapp'

urlpatterns = [
    path('', views.Index.as_view(), name='main_page'),
    path('artists/', views.ArtistsList.as_view(), name='artists'),
    path('albums/', views.AlbumsList.as_view(), name='albums'),
    path('tracks/', views.TrackList.as_view(), name='tracks'),
    path("search/", views.MainSearch.as_view(), name='main-search'),
    path("search/artists/", views.ArtistSearch.as_view(), name='artist-search'),
    path("search/albums/", views.AlbumSearch.as_view(), name='album-search'),
    path("search/tracks/", views.TrackSearch.as_view(), name='track-search'),
    path("filter/artists/", views.ArtistFilter.as_view(), name='artist-filter'),
    path("filter/albums/", views.AlbumFilter.as_view(), name='album-filter'),
    path("filter/tracks/", views.TrackFilter.as_view(), name='track-filter'),
    path("sorting/artists/", views.SortingArtists.as_view(), name='sort-artists'),
    path("sorting/albums/", views.SortingAlbums.as_view(), name='sort-albums'),
    path("sorting/tracks/", views.SortingTracks.as_view(), name='sort-tracks'),
    path('artists/post', views.ArtistCreate.as_view(), name='artist_post'),
    path('albums/post', views.AlbumCreate.as_view(), name='album_post'),
    path('tracks/post', views.TrackCreate.as_view(), name='track_post'),
    path('genre/post', views.AddGenre.as_view(), name='add-genre'),
    path('artists/<slug:slug>/', views.ArtistDetail.as_view(), name='artist_detail'),
    path('albums/<slug:slug>/', views.AlbumDetail.as_view(), name='album_detail'),
    path('tracks/<slug:slug>/', views.TrackDetail.as_view(), name='track_detail'),
    path("artists/<int:pk>/comment/", views.AddCommenttoArtist.as_view(), name="add_comment_to_artist"),
    path("artists/<int:id>/update-rating", views.AddRating.as_view(), name='update-rating-to-artist'),
    path("artists/<int:pk>/artist-delete/", views.ArtistDelete.as_view(), name='artist_delete'),
    path("artists/<int:pk>/artist-update/", views.ArtistUpdate.as_view(), name='artist_update'),
    path("albums/<int:pk>/comment/", views.AddCommenttoAlbum.as_view(), name="add_comment_to_album"),
    path("albums/<int:id>/update-rating", views.AddRating.as_view(), name='update-rating-to-album'),
    path("albums/<int:pk>/album-delete/", views.AlbumDelete.as_view(), name='album_delete'),
    path("albums/<int:pk>/album-update/", views.AlbumUpdate.as_view(), name='album_update'),
    path("tracks/<int:pk>/comment/", views.AddCommenttoTrack.as_view(), name="add_comment_to_track"),
    path("tracks/<int:id>/update-rating", views.AddRating.as_view(), name='update-rating-to-track'),
    path("tracks/<int:pk>/track-delete/", views.TrackDelete.as_view(), name='track_delete'),
    path("tracks/<int:pk>/track-update/", views.TrackUpdate.as_view(), name='track_update'),
]


def handler404(request, *args, **argv):
    response = render('404_login_required.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
