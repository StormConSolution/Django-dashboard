from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


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
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=80, blank=False)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    class Meta:
        get_latest_by = 'date_created'

class Classification(models.Model):
    label = models.CharField(max_length=80)
    
    def __str__(self):
        return self.label

class Entity(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)
    classifications = models.ManyToManyField(Classification)

    def __str__(self):
        return self.label

class Emotion(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)

    def __str__(self):
        return self.label

class Source(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)

    def __str__(self):
        return self.label

class Data(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    sentiment = models.FloatField(default=0)
    language = models.CharField(max_length=2, default='en', choices=LANGUAGES)
    keywords = ArrayField(models.CharField(max_length=40))
    entities = models.ManyToManyField(Entity)

    def __str__(self):
        return self.text

class Aspect(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    label = models.CharField(max_length=80, blank=True)
    sentiment = models.FloatField(default=0)
    chunk = models.TextField(blank=False)
    topic = models.TextField(blank=False)
    sentiment_text = ArrayField(models.CharField(max_length=40))

    def __str__(self):
        return self.label

class EmotionalEntity(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)

class Chart(models.Model):
    project = models.ManyToManyField(Project)
    chart_type = models.CharField(max_length=80, blank=False)
    chart_size = models.IntegerField(blank=False)

    def __str__(self):
        return self
