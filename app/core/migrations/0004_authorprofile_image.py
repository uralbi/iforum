# Generated by Django 3.2.18 on 2023-03-11 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_post_published_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='authorprofile',
            name='image',
            field=models.ImageField(blank=True, upload_to='profile_images/%Y/%m/%d'),
        ),
    ]
