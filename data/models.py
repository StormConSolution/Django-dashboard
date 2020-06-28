from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

LANGUAGES = (
    ('ar', 'Arabic (العربية)'),
    ('zh', 'Chinese (中文)'),
    ('da', 'Danish (Dansk)'),
    ('nl', 'Dutch (Nederlands)'),
    ('en', 'English'),
    ('fi', 'Finnish (Suomi)'),
    ('fr', 'French (Français)'),
    ('de', 'German (Deutsch)'),
    ('he', 'Hebrew (עִברִית)'),
    ('it', 'Italian (Italiano)'),
    ('id', 'Indonesian (Bahasa Indonesia)'),
    ('ja', 'Japanese (日本語)'),
    ('ko', 'Korean (한국어)'),
    ('no', 'Norwegian (Norsk)'),
    ('pl', 'Polish (Polski)'),
    ('pt', 'Portuguese (Português)'),
    ('ru', 'Russian (русский)'),
    ('es', 'Spanish (Español)'),
    ('sv', 'Swedish (Svenska)'),
    ('tr', 'Turkish (Türk)'),
    ('th', 'Thai (ไทย)'),
    ('vi', 'Vietnamese (Tiếng Việt)'),
    ('ur', 'Urdu (اردو)'),
)

class Project(models.Model):
    name = models.CharField(max_length=80, blank=False)
    users = models.ManyToManyField(User)
    
    def __str__(self):
        return self.name

class Data(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project)
    
    source = models.CharField(max_length=80, blank=True)
    text = models.TextField(blank=False)
    sentiment = models.FloatField(default=0)
    entities = JSONField(blank=True)
    aspects = JSONField(blank=True)
    keywords = ArrayField(models.CharField(max_length=40))
    language = models.CharField(max_length=2, default='en', choices=LANGUAGES)

    def __str__(self):
        return self.text
