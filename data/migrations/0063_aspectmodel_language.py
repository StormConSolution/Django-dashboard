# Generated by Django 3.0.8 on 2021-06-05 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0062_auto_20210603_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='aspectmodel',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('ar', 'Arabic (العربية)'), ('zh', 'Chinese (中文)'), ('da', 'Danish (Dansk)'), ('nl', 'Dutch (Nederlands)'), ('fi', 'Finnish (Suomi)'), ('fr', 'French (Français)'), ('de', 'German (Deutsch)'), ('he', 'Hebrew (עִברִית)'), ('it', 'Italian (Italiano)'), ('id', 'Indonesian (Bahasa Indonesia)'), ('ja', 'Japanese (日本語)'), ('ko', 'Korean (한국어)'), ('no', 'Norwegian (Norsk)'), ('pl', 'Polish (Polski)'), ('pt', 'Portuguese (Português)'), ('ru', 'Russian (русский)'), ('es', 'Spanish (Español)'), ('sv', 'Swedish (Svenska)'), ('tr', 'Turkish (Türk)'), ('th', 'Thai (ไทย)'), ('vi', 'Vietnamese (Tiếng Việt)'), ('ur', 'Urdu (اردو)')], default='en', max_length=2),
        ),
    ]
