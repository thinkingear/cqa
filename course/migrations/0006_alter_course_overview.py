# Generated by Django 4.1.7 on 2023-04-24 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_alter_course_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='overview',
            field=models.TextField(blank=True, null=True),
        ),
    ]
