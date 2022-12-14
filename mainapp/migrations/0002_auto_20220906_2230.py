# Generated by Django 3.0.9 on 2022-09-06 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='album',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trak_on_album', to='mainapp.Album', verbose_name='Альбом/EP'),
        ),
        migrations.AlterField(
            model_name='track',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track_artist', to='mainapp.Artist', verbose_name='Имя артиста/группы'),
        ),
    ]
