import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.urls import reverse

class Sentiment(models.Model):
    label = models.CharField(max_length=80) 
    definition = models.TextField()
    rule_id = models.TextField()
    language = models.CharField(max_length=2, default='en', choices=settings.LANGUAGES)
    sentiment = models.CharField(max_length=80)
    users = models.ManyToManyField(User)
    api_key = models.TextField(blank=False, default="")

class ChartType(models.Model):
    label = models.CharField(max_length=80, blank=False, unique=True)
    load_async = models.BooleanField(default=False)

    def __str__(self):
        return self.label

class AspectModel(models.Model):
    label = models.CharField(max_length=80, blank=False)
    language = models.CharField(max_length=2, default='en', choices=settings.LANGUAGES)
    users = models.ManyToManyField(User, blank=True)
    standard = models.BooleanField(default=True)
    
    def __str__(self):
        return self.label
    
    class Meta:
        ordering = ('label',)

class PredefinedAspectRule(models.Model):
    label = models.CharField(max_length=80, blank=False)

class AspectRule(models.Model):
    rule_name = models.CharField(max_length=80, blank=False)
    definition = models.TextField(blank=True)
    aspect_model = models.ForeignKey(AspectModel, on_delete=models.CASCADE)
    classifications = models.TextField(blank=True)
    predefined = models.BooleanField(default=False)
    
    class Meta:
        unique_together=('rule_name', 'aspect_model')
        ordering = ('rule_name',)

class Project(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=80, blank=False)
    users = models.ManyToManyField(User)
    charts = models.ManyToManyField(ChartType, blank=True)
    aspect_model = models.ForeignKey(AspectModel, on_delete=models.CASCADE, null=True, blank=True)
    sentiment = models.ManyToManyField(Sentiment, blank=True)
    geo_enabled = models.BooleanField(default=False)
    api_key = models.TextField(blank=False, default="")

    def __str__(self):
        return self.name

    class Meta:
        get_latest_by = 'date_created'
        ordering = ('name',)

    def get_absolute_url(self):
        return reverse('project', kwargs={'project_id': self.id})
    
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
    label = models.CharField(max_length=80, db_index=True)
    english_label = models.CharField(max_length=80, db_index=True, default='', 
            help_text='Non-blank only when language is not english')
    language = models.CharField(max_length=2, default='en', choices=settings.LANGUAGES)
    classifications = models.ManyToManyField(Classification)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = 'Entities'
        unique_together=('label', 'english_label', 'language')


class Source(models.Model):
    label = models.CharField(max_length=80, unique=True, db_index=True)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ('label',)

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
        ordering = ('label',)

    def __str__(self):
        return self.label

class Summary(models.Model):
    date_created = models.DateField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=80, default="")
    description = models.TextField()

    def __str__(self):
        return self.title

class AlertRule(models.Model):
    """
    The rules for sending out an alert.
    """
    PERIOD = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    aspect = models.CharField(max_length=80, default='')
    frequency = models.IntegerField(help_text='How many times should the data appear before sending an alert', default=0)
    period = models.CharField(max_length=80, choices=PERIOD, default='daily')
    keywords = models.TextField(blank=True)
    emails = models.TextField(blank=True)
    sms = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)

    def should_notify(self):
        """
        Has this rule been triggered enough to send out a notification.
        """
        if self.active == False:
            return False
        today = datetime.datetime.now().date()
        if self.period == 'daily' and self.alert_set.filter(
                date_created__gte=today).count() >= self.frequency:
            return True
        elif self.period == 'weekly' and self.alert_set.filter(
                date_created__gte=today-datetime.timedelta(7)).count() >= self.frequency:
            return True
        elif self.period == 'monthly' and self.alert_set.filter(
                date_created__gte=today-datetime.timedelta(30)).count() >= self.frequency:
            return True
        
        return False

class Alert(models.Model):
    """
    The alert that is generated when an AlertRule is triggered.
    """
    date_created = models.DateField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    data = models.ForeignKey('Data', blank=True, null=True, on_delete=models.CASCADE)
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=80, default="")
    description = models.TextField()

    def __str__(self):
        return self.title

class Data(models.Model):
    date_created = models.DateField(db_index=True)
    url = models.URLField(blank=True, null=True, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    sentiment = models.FloatField(default=0, db_index=True)
    relevance = models.FloatField(default=0, db_index=True)
    language = models.CharField(max_length=2, default='en', choices=settings.LANGUAGES)
    entities = models.ManyToManyField(Entity)
    metadata = JSONField(blank=True, default=dict)

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
