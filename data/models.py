from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField


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


def default_field():
    return {"sentiment_t": 2, "sentiment_f": 1, "aspects_t": 2, "aspects_f": 1, "keywords": 1, "entities": 1}


class Project(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=80, blank=False)
    users = models.ManyToManyField(User)
    # used to list chart types and their sizes
    chart = JSONField(
        default=default_field)

    def __str__(self):
        return self.name

    class Meta:
        get_latest_by = 'date_created'


class Data(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    source = models.CharField(max_length=80, blank=True)
    text = models.TextField(blank=False)
    sentiment = models.FloatField(default=0)
    language = models.CharField(max_length=2, default='en', choices=LANGUAGES)
    keywords = ArrayField(models.CharField(max_length=40))

    def __str__(self):
        return self.text


class Entity(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    label = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.label


class Aspect(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    label = models.CharField(max_length=80, blank=True)
    sentiment = models.FloatField(default=0)
    chunk = models.TextField(blank=False)
    topic = models.TextField(blank=False)
    sentiment_text = ArrayField(models.CharField(max_length=40))

    def __str__(self):
        return self.label
