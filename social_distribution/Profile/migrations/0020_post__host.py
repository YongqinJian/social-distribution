# Generated by Django 3.1.6 on 2021-03-31 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0019_author_remote_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='_host',
            field=models.CharField(blank=True, db_column='host', max_length=50),
        ),
    ]