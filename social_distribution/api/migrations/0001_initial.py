# Generated by Django 3.2 on 2021-04-09 23:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, null=True)),
                ('url', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
