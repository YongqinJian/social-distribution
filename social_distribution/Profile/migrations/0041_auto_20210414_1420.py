# Generated by Django 3.1.6 on 2021-04-14 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0040_auto_20210414_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author_json',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='commentlike',
            name='author_json',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='postlike',
            name='author_json',
            field=models.JSONField(null=True),
        ),
    ]
