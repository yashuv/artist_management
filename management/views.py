from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.db import connection
from django.core.paginator import Paginator
from datetime import datetime

import csv
import os
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from .models import Artist
from .forms import CSVUploadForm


class ArtistCSVUploadView(View):
    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)
            try:
                for row in reader:
                    Artist.objects.create(**row)
                return HttpResponse(
                    "CSV file has been uploaded and processed.", status=200
                )
            except Exception as e:
                return HttpResponse(str(e), status=400)
        else:
            return HttpResponse(str(form.errors), status=400)

    def get(self, request):
        form = CSVUploadForm()
        return render(request, "artist/artists.html", {"form": form})


def export_artists_csv(request):
    """
    Exports the artists data to a CSV file in the 'exported' folder of the project.
    """

    # make the 'exported' folder if it does not exist
    exported_folder = os.path.join(settings.BASE_DIR, "exported")
    os.makedirs(exported_folder, exist_ok=True)

    # path to the CSV file
    csv_file_path = os.path.join(exported_folder, "artists.csv")

    with open(csv_file_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "name",
                "dob",
                "gender",
                "address",
                "first_release_year",
                "no_of_albums_released",
            ]
        )

        artists = Artist.objects.all().values_list(
            "name",
            "dob",
            "gender",
            "address",
            "first_release_year",
            "no_of_albums_released",
        )
        for artist in artists:
            writer.writerow(artist)

    return HttpResponse(f"CSV file has been exported to: {csv_file_path}")


class RegisterArtistAPIView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        name = request.POST.get("name")
        dob = request.POST.get("dob")
        if datetime.strptime(dob, "%Y-%m-%d").date() > datetime.now().date(): # validate dob
            return render(
                request,
                "artist/register.html",
                {"error": "Enter correct date of birth"},
            )
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        first_release_year = request.POST.get("first_release_year")
        no_of_albums_released = request.POST.get("no_of_albums_released")
        sql_query = f"""
            INSERT INTO management_Artist (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at)
            VALUES ('{name}', '{dob}', '{gender}', '{address}', '{first_release_year}', '{no_of_albums_released}', '{datetime.now()}', '{datetime.now()}')
        """
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
        return redirect("/artist/all/")

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        return render(
            request,
            "artist/register.html",
            context={"active_user": request.user.is_authenticated},
        )


class ViewArtistAPIView(APIView):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id, name, dob, gender, address, first_release_year, created_at, updated_at, no_of_albums_released FROM management_Artist WHERE id = {pk} LIMIT 1"
            )
            artist = cursor.fetchone()
        if artist:
            (
                artist_id,
                name,
                dob,
                gender,
                address,
                first_release_year,
                created_at,
                updated_at,
                no_of_albums_released,
            ) = artist
            context = {
                "id": artist_id,
                "name": name,
                "address": address,
                "dob": dob.strftime("%Y-%m-%d"),
                "gender": gender,
                "updated_at": updated_at.strftime("%Y-%m-%d"),
                "created_at": created_at.strftime("%Y-%m-%d"),
                "first_released_year": first_release_year,
                "no_of_albums_released": no_of_albums_released,
                "active_user": request.user.is_authenticated,
            }
            return render(request, "artist/artist.html", context=context)


class ViewArtistsAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name FROM management_Artist ORDER BY created_at asc"
            )
            artists = cursor.fetchall()

        paginator = Paginator(artists, 5)
        try:
            page_number = int(request.GET.get("page"))
        except Exception as e:
            page_number = 1
        page_obj = paginator.get_page(page_number)
        artist_info = [(artist[0], artist[1]) for artist in artists]
        artist_info = artist_info[(page_number - 1) * 5 : 5 * page_number]
        return render(
            request,
            "artist/artists.html",
            {
                "active_user": request.user.is_authenticated,
                "artists": artist_info,
                "page_obj": page_obj,
            },
        )


class UpdateArtistAPIView(APIView):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at FROM management_Artist WHERE id = {pk} LIMIT 1")
            artist = cursor.fetchone()
        if artist:
            (
                name,
                dob,
                gender,
                address,
                first_release_year,
                no_of_albums_released,
                created_at,
                updated_at,
            ) = artist

            context = {
                "name": name,
                "address": address,
                "dob": dob.strftime("%Y-%m-%d"),
                "gender": gender,
                "first_release_year": first_release_year,
                "no_of_albums_released": no_of_albums_released,
                "updated_at": updated_at.strftime("%Y-%m-%d"),
                "created_at": created_at.strftime("%Y-%m-%d"),
                "active_user": request.user.is_authenticated,
                "modify": True,
            }
            return render(request, "artist/register.html", context)

    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect('/user/login/')
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        if datetime.strptime(dob, '%Y-%m-%d').date() > datetime.now().date():
            return render(request, 'artist/register.html', {'error': 'Enter correct date of birth'})
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        first_release_year = request.POST.get('first_release_year')
        no_of_albums_released = request.POST.get('no_of_albums_released')

        sql_query = """
                        UPDATE management_Artist
                        SET name = %s, dob = %s, gender = %s, address = %s, first_release_year=%s, no_of_albums_released=%s, updated_at=%s
                        WHERE id = %s
                        """
        values = [name, dob, gender, address, first_release_year, no_of_albums_released, datetime.now(), pk]
        with connection.cursor() as cursor:
            cursor.execute(sql_query, values)

        return redirect('/artist/all/')


class DeleteArtistAPIView(APIView):
    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        
        delete_music_query = f"DELETE FROM management_Music WHERE artist_id = {pk}"
        delete_artist_query = f"DELETE FROM management_Artist WHERE id = {pk}"

        with connection.cursor() as cursor:
            cursor.execute(delete_music_query)
            cursor.execute(delete_artist_query)
        return redirect("/artist/all/")


class RegisterSongAPIView(APIView):
    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        title = request.POST.get("title")
        album_name = request.POST.get("album_name")
        genre = request.POST.get("genre")

        sql_query = """
            INSERT INTO management_Music (title, album_name, genre, artist_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = [title, album_name, genre, pk, datetime.now(), datetime.now()]
        with connection.cursor() as cursor:
            cursor.execute(sql_query, values)
        return redirect("/artist/all/")

    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM management_Artist WHERE id = {pk}")
            artist = cursor.fetchone()

        if artist:
            artist_name = artist[0]

        return render(
            request,
            "song/register.html",
            context={
                "active_user": request.user.is_authenticated,
                "artist_name": artist_name,
            },
        )


class ViewSongAPIView(APIView):
    def get(self, request, pk=None, song_id=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT a.name, m.title, m.album_name, m.genre, m.created_at, m.updated_at FROM management_Music m JOIN management_Artist a ON m.artist_id = a.id WHERE m.id = {song_id} AND a.id = {pk} LIMIT 1"
            )

            artist_music = cursor.fetchone()

        if artist_music:
            artist_name, title, album_name, genre, created_at, updated_at = artist_music
            context = {
                "artist_name": artist_name,
                "title": title,
                "album_name": album_name,
                "genre": genre,
                "updated_at": updated_at.strftime("%Y-%m-%d"),
                "created_at": created_at.strftime("%Y-%m-%d"),
                "active_user": request.user.is_authenticated,
            }
            return render(request, "song/song.html", context=context)


class ViewSongsAPIView(APIView):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        sql_query = f"SELECT id, title FROM management_Music WHERE artist_id = {pk} ORDER BY created_at DESC"
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            songs = cursor.fetchall()

        paginator = Paginator(songs, 5)
        try:
            page_number = int(request.GET.get("page"))
        except Exception as e:
            page_number = 1
        page_obj = paginator.get_page(page_number)
        songs_info = [(pk, song[0], song[1]) for song in songs]
        songs_info = songs_info[(page_number - 1) * 5 : 5 * page_number]
        return render(
            request,
            "song/songs.html",
            {
                "songs": songs_info,
                "page_obj": page_obj,
                "active_user": request.user.is_authenticated,
            },
        )


class UpdateSongAPIView(APIView):
    def get(self, request, pk=None, song_id=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM management_Music WHERE id = {song_id} LIMIT 1"
            )
            music = cursor.fetchone()

            cursor.execute(f"SELECT name FROM management_Artist WHERE id = {pk}")

            artist = cursor.fetchone()

        if music and artist:
            artist_name = artist[0]

            _, title, album_name, genre, *_ = music
            context = {
                "active_user": request.user.is_authenticated,
                "title": title,
                "album_name": album_name,
                "genre": genre,
                "artist_name": artist_name,
                "modify": True,
            }
            return render(request, "song/register.html", context)

    def post(self, request, pk=None, song_id=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        title = request.POST.get("title")
        album_name = request.POST.get("album_name")
        genre = request.POST.get("genre")
        sql_query = """
                        UPDATE management_Music
                        SET title = %s, album_name = %s, genre = %s, updated_at = %s
                        WHERE id = %s
                        """
        values = [title, album_name, genre, datetime.now(), song_id]
        with connection.cursor() as cursor:
            cursor.execute(sql_query, values)

        return redirect(f"/artist/{pk}/songs/{song_id}/")


class DeleteSongAPIView(APIView):
    def post(self, request, pk=None, song_id=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM management_Music WHERE id = {song_id}")

        return redirect(f"/artist/{pk}/songs/")
