# Generated by Django 2.2.13 on 2020-06-08 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VisualizingTweets', '0007_auto_20200507_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='stock_user',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='ストック者'),
        ),
    ]
