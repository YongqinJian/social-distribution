# Generated by Django 3.1.6 on 2021-02-19 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, max_length=25)),
                ('sender', models.CharField(blank=True, max_length=50)),
                ('receiver', models.CharField(blank=True, max_length=50)),
            ],
        ),
    ]