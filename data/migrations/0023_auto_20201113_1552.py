# Generated by Django 3.0.8 on 2020-11-13 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_auto_20201113_1528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='adjectives',
        ),
        migrations.AddField(
            model_name='data',
            name='adjectives',
            field=models.ManyToManyField(to='data.Comment'),
        ),
    ]
