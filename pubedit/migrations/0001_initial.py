# Generated by Django 4.1.7 on 2023-04-18 06:35

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=128)),
                ('feed', tinymce.models.HTMLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ArticleFollower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pubedit.article')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.user')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='followers',
            field=models.ManyToManyField(related_name='followed_articles', through='pubedit.ArticleFollower', to='account.user'),
        ),
        migrations.AddField(
            model_name='article',
            name='poster',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_posted', to='account.user'),
        ),
        migrations.AddConstraint(
            model_name='articlefollower',
            constraint=models.UniqueConstraint(fields=('follower', 'article'), name='article_follower'),
        ),
    ]
