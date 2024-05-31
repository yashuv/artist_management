from django.db import models
import enum

# Create your models here.


class GenderEnum(enum.Enum):
    Male = "m"
    Female = "f"
    Other = "o"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class GenreEnum(enum.Enum):
    RNB = "rnb"
    Country = "country"
    Classic = "classic"
    Rock = "rock"
    Jazz = "jazz"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Artist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=GenderEnum.choices(),
        default=GenderEnum.Male.value,
        verbose_name="Select Gender",
    )
    address = models.CharField(max_length=255)
    first_release_year = models.CharField(max_length=4)
    no_of_albums_released = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Music(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    album_name = models.CharField(max_length=50)
    genre = models.CharField(
        max_length=10,
        choices=GenreEnum.choices(),
        default=GenreEnum.RNB.value,
        verbose_name="Select Genre",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
