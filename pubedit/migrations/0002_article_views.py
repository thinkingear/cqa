# Generated by Django 4.1.7 on 2023-04-19 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pubedit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]