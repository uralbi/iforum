# Generated by Django 3.2.18 on 2023-03-04 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.SmallIntegerField(default=0),
        ),
    ]