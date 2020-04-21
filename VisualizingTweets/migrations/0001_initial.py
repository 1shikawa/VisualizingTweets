# Generated by Django 2.2.12 on 2020-04-07 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tweet_id', models.CharField(blank=True, max_length=50, verbose_name='ツイートID')),
                ('user_id', models.CharField(blank=True, max_length=50, verbose_name='ユーザーID')),
                ('user_name', models.CharField(blank=True, max_length=100, verbose_name='ユーザー名')),
                ('tweet_text', models.TextField(blank=True, max_length=500, verbose_name='ツイート内容')),
                ('tweet_url', models.URLField(blank=True, max_length=300, verbose_name='ツイートURL')),
                ('tweet_created_at', models.DateField(blank=True, verbose_name='ツイート日')),
                ('favorite_count', models.PositiveIntegerField(blank=True, default=0, verbose_name='いいね数')),
                ('retweet_count', models.PositiveIntegerField(blank=True, default=0, verbose_name='リツイート数')),
                ('expanded_url', models.URLField(blank=True, default='http://example.com', max_length=300, verbose_name='関連URL')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]