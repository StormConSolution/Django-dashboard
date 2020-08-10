# Generated by Django 2.0.5 on 2020-08-10 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_project_chart'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chart_type', models.CharField(max_length=80)),
                ('chart_size', models.IntegerField()),
                ('Project', models.ManyToManyField(to='data.Project')),
            ],
        ),
    ]
