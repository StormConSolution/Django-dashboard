from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse


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

class ChartType(models.Model):
    label = models.CharField(max_length=80, blank=False, unique=True)
    load_async = models.BooleanField(default=False)

    def __str__(self):
        return self.label

class AspectType(models.Model):
    label = models.CharField(max_length=80, blank=False, unique=True)

    def __str__(self):
        return self.label

class Project(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=80, blank=False)
    users = models.ManyToManyField(User)
    charts = models.ManyToManyField(ChartType)

    def __str__(self):
        return self.name

    class Meta:
        get_latest_by = 'date_created'
    
    def show_entities(self):
        return self.charts.filter(label='entity_table').count() > 0
    
    def show_aspects(self):
        return self.charts.filter(label='aspect_s').count() > 0

    def get_absolute_url(self):
        return reverse('projects', kwargs={'project_id':self.id})

class Classification(models.Model):
    label = models.CharField(max_length=80, db_index=True)
    
    def __str__(self):
        return self.label

class Entity(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)
    classifications = models.ManyToManyField(Classification)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = 'Entities'

class Emotion(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)

    def __str__(self):
        return self.label

class Source(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)

    def __str__(self):
        return self.label

class Data(models.Model):
    date_created = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    sentiment = models.FloatField(default=0, db_index=True)
    language = models.CharField(max_length=2, default='en', choices=LANGUAGES)
    entities = models.ManyToManyField(Entity)

    class Meta:
        verbose_name_plural = 'Data'

    def __str__(self):
        return self.text

class Aspect(models.Model):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    label = models.CharField(max_length=80, blank=True, db_index=True)
    sentiment = models.FloatField(default=0, db_index=True)
    chunk = models.TextField(blank=False)
    topic = models.TextField(blank=False, db_index=True)
    sentiment_text = ArrayField(models.CharField(max_length=40))

    def __str__(self):
        return self.label

class EmotionalEntity(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE)
    data = models.ForeignKey(Data, on_delete=models.CASCADE)


class TwitterSearch(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    query = models.CharField(max_length=80)
    project_name = models.CharField(max_length=80)

    entities = models.BooleanField(default=False, help_text='Do you want to detect entities?')
    aspect = models.ForeignKey(AspectType, 
            default=None,
            blank=True,
            help_text='Which aspect model to use? (optional)', on_delete=models.CASCADE)
    
    completed = models.BooleanField(default=False, help_text='Set automatically')
    
    def __str__(self):
        return self.query

    class Meta:
        verbose_name_plural = 'Twitter Searches'
