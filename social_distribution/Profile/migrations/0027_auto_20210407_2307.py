# Generated by Django 3.1.6 on 2021-04-08 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0026_auto_20210407_2305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='remote_author_username',
            new_name='remote_author_displayName',
        ),
    ]