from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    deleted_date = models.DateTimeField('Deleted date', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True