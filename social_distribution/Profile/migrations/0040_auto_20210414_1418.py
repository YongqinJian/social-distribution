# Generated by Django 3.1.6 on 2021-04-14 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0039_author_debug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='is_remote',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='commentlike',
            name='author',
        ),
        migrations.RemoveField(
            model_name='postlike',
            name='author',
        ),
        migrations.AddField(
            model_name='comment',
            name='author_json',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='author_json',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='postlike',
            name='author_json',
            field=models.TextField(null=True),
        ),
    ]