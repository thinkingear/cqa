# Generated by Django 4.1.7 on 2023-04-19 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('course', '0002_alter_section_options_alter_video_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='followers',
            field=models.ManyToManyField(related_name='followed_videos', through='course.VideoFollower', to='account.user'),
        ),
    ]