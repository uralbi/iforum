# Generated by Django 3.2.18 on 2023-03-07 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_tag_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(max_length=100),
        ),
    ]
