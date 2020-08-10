# Generated by Django 3.0.8 on 2020-08-07 21:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_aspect'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aspect',
            name='count',
        ),
        migrations.RemoveField(
            model_name='data',
            name='aspects',
        ),
        migrations.RemoveField(
            model_name='data',
            name='entities',
        ),
        migrations.AddField(
            model_name='aspect',
            name='chunk',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='aspect',
            name='sentiment',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='aspect',
            name='sentiment_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='aspect',
            name='topic',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=80)),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Data')),
            ],
        ),
    ]