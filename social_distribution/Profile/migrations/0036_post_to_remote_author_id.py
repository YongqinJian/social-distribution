# Generated by Django 3.1.6 on 2021-04-13 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0035_auto_20210411_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='to_remote_author_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
