# Generated by Django 4.1.7 on 2023-04-26 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0006_delete_accountfollownotification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questioninvitation',
            options={'ordering': ['-created', '-updated']},
        ),
    ]
