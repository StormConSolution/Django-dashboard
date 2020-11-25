# Generated by Django 3.0.8 on 2020-11-13 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0021_data_adjectives'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjectives', models.CharField(blank=True, max_length=300, null=True)),
                ('frequency', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='data',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Country'),
        ),
        migrations.AlterField(
            model_name='data',
            name='adjectives',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Comment'),
        ),
    ]
