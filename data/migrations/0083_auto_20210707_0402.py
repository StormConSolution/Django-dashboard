# Generated by Django 3.0.8 on 2021-07-07 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0082_project_popup_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aspectmodel',
            name='standard',
            field=models.BooleanField(default=False),
        ),
    ]