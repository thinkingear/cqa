# Generated by Django 4.1.7 on 2023-04-24 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0004_delete_contentfollownotification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursefollownotification',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='questionfollownotification',
            name='answer',
        ),
        migrations.AlterField(
            model_name='accountfollownotification',
            name='action',
            field=models.CharField(choices=[('post', 'Post'), ('upvote', 'Upvote'), ('follow', 'Follow')], max_length=10, null=True),
        ),
        migrations.DeleteModel(
            name='ArticleFollowNotification',
        ),
        migrations.DeleteModel(
            name='CourseFollowNotification',
        ),
        migrations.DeleteModel(
            name='QuestionFollowNotification',
        ),
    ]
