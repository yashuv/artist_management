# Generated by Django 4.1 on 2024-05-31 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('dob', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other')], default='m', max_length=1, verbose_name='Select Gender')),
                ('address', models.CharField(max_length=255)),
                ('first_release_year', models.CharField(max_length=4)),
                ('no_of_albums_released', models.CharField(max_length=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('album_name', models.CharField(max_length=50)),
                ('genre', models.CharField(choices=[('rnb', 'RNB'), ('country', 'Country'), ('classic', 'Classic'), ('rock', 'Rock'), ('jazz', 'Jazz')], default='rnb', max_length=10, verbose_name='Select Genre')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.artist')),
            ],
        ),
    ]
