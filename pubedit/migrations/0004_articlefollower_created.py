# Generated by Django 4.1.7 on 2023-04-21 04:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pubedit', '0003_articletag_article_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlefollower',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
