from django.urls import path
from .views import RegisterArtistAPIView, ViewArtistAPIView, ViewArtistsAPIView, UpdateArtistAPIView, DeleteArtistAPIView, RegisterSongAPIView, ViewSongAPIView, ViewSongsAPIView, UpdateSongAPIView, DeleteSongAPIView, ArtistCSVUploadView, export_artists_csv


urlpatterns = [
    path('register/', RegisterArtistAPIView.as_view(), name='artist_register'),
    path('all/', ViewArtistsAPIView.as_view(), name='artist_all'),
    path('<int:pk>/', ViewArtistAPIView.as_view(), name='artist_view'),
    path('edit/<int:pk>/', UpdateArtistAPIView.as_view(), name='artist_modify'),
    path('delete/<int:pk>/', DeleteArtistAPIView.as_view(), name='artist_delete'),
    path('<int:pk>/songs/add/', RegisterSongAPIView.as_view(), name='song_register'),
    path('<int:pk>/songs/<int:song_id>/', ViewSongAPIView.as_view(), name='song_view'),
    path('<int:pk>/songs/', ViewSongsAPIView.as_view(), name='song_all'),
    path('<int:pk>/songs/<int:song_id>/edit/', UpdateSongAPIView.as_view(), name='song_modify'),
    path('<int:pk>/songs/<int:song_id>/delete/', DeleteSongAPIView.as_view(), name='song_delete'),
    path('upload-csv/', ArtistCSVUploadView.as_view(), name='upload_csv'),
    path('export-csv/', export_artists_csv, name='export_artists_csv'),

]