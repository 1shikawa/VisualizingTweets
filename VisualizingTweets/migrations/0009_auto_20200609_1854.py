# Generated by Django 2.2.13 on 2020-06-09 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VisualizingTweets', '0008_stock_stock_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='screen_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='スクリーン名'),
        ),
    ]