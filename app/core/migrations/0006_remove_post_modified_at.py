# Generated by Django 3.2.18 on 2023-03-04 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_tag_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='modified_at',
        ),
    ]
