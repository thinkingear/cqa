# Generated by Django 4.1.7 on 2023-04-08 14:24

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
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('feed', tinymce.models.HTMLField(blank=True, null=True)),
                ('poster', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_posted', to='account.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=128, unique=True)),
                ('followers', models.ManyToManyField(related_name='followed_questions', to='account.user')),
                ('poster', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_posted', to='account.user')),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.CreateModel(
            name='QuestionVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qa.question')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.user')),
            ],
        ),
        migrations.CreateModel(
            name='AnswerVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField()),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qa.answer')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.user')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='qa.question'),
        ),
        migrations.AddConstraint(
            model_name='questionvote',
            constraint=models.UniqueConstraint(fields=('voter', 'question'), name='question_voter'),
        ),
        migrations.AddConstraint(
            model_name='answervote',
            constraint=models.UniqueConstraint(fields=('voter', 'answer'), name='answer_voter'),
        ),
    ]
