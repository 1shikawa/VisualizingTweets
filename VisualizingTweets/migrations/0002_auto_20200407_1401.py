# Generated by Django 2.2.12 on 2020-04-07 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VisualizingTweets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='tweet_created_at',
            field=models.DateTimeField(blank=True, verbose_name='ツイート日'),
        ),
    ]
