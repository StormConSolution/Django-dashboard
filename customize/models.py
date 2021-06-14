from django.contrib.auth.models import User
from django.db import models

class Setting(models.Model):
    key = models.CharField(max_length=80, unique=True, db_index=True)
    value = models.CharField(max_length=80, blank=True)
    upload = models.FileField(max_length=80, upload_to='customize/', blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.key
