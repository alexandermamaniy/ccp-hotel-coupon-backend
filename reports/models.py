from django.db import models
import uuid
from core.models import TimeStampedModel

def upload_to(instance, filename):
    return f'reports/{filename}'.format(filename=filename)

class Report(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Title', max_length=255, blank=False, null=False)
    media_url = models.ImageField(upload_to=upload_to, blank=True, null=True)
    hotelier_profile = models.ForeignKey('hotelier_profiles.HotelierProfile', on_delete=models.CASCADE, verbose_name='Hotelier profile')

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} - {self.hotelier_profile}'