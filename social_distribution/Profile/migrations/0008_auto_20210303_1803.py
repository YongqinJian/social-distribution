# Generated by Django 3.1.7 on 2021-03-04 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0007_profile_github'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='github',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]