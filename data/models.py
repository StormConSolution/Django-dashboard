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


class AspectModel(models.Model):
    label = models.CharField(max_length=80, blank=False, unique=True)

    def __str__(self):
        return self.label


class Project(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=80, blank=False)
    users = models.ManyToManyField(User)
    charts = models.ManyToManyField(ChartType, blank=True)
    aspect_model = models.ForeignKey(AspectModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        get_latest_by = 'date_created'
        ordering = ('name',)

    def show_entities(self):
        return self.charts.filter(label='entity_table').count() > 0

    def show_aspects(self):
        return self.charts.filter(label='aspect_s').count() > 0

    def get_absolute_url(self):
        return reverse('projects', kwargs={'project_id': self.id})
    
    def most_recent_date(self):
        # Get the date of my most recent data item.
        if self.data_set.count():
            return self.data_set.latest().date_created
        return None

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


class Keyword(models.Model):
    label = models.CharField(
        max_length=300, unique=True, blank=False, null=False)

    def __str__(self):
        return self.label


class Country(models.Model):
    label = models.CharField(
        max_length=300, unique=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.label


class Data(models.Model):
    date_created = models.DateField(db_index=True)
    url = models.URLField(blank=True, null=True, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    sentiment = models.FloatField(default=0, db_index=True)
    weighted_score = models.FloatField(default=0, db_index=True)
    language = models.CharField(max_length=2, default='en', choices=LANGUAGES)
    entities = models.ManyToManyField(Entity)

    class Meta:
        verbose_name_plural = 'Data'
        get_latest_by = 'date_created'

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

class TwitterSearch(models.Model):
    NOT_RUNNING = 0
    RUNNING = 1
    ERROR = 2
    DONE = 3

    STATUSES = (
        (NOT_RUNNING, 'Not Running'),
        (RUNNING, 'Running'),
        (ERROR, 'Error'),
        (DONE, 'Done'),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    query = models.CharField(max_length=80,
         help_text='See https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/premium-operators for info on setting up queries')
    project_name = models.CharField(max_length=80)

    entities = models.BooleanField(
        default=False, help_text='Do you want to detect entities?')
    
    aspect = models.ForeignKey(AspectModel,
       default=None,
       null=True,  # test
       blank=True,
       help_text='Which aspect model to use? (optional)', on_delete=models.CASCADE)

    status = models.IntegerField(choices=STATUSES, default=NOT_RUNNING)

    def __str__(self):
        return self.query

    class Meta:
        verbose_name_plural = 'Twitter Searches'
