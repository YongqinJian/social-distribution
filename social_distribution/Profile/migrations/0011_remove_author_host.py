# Generated by Django 3.1.6 on 2021-03-25 01:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0010_author_host'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='host',
        ),
    ]
