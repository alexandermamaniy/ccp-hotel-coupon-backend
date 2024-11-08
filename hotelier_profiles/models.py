from django.db import models
import uuid
from users.models import User
from core.models import TimeStampedModel

def upload_to(instance, filename):
    return f'hotelier-profiles/{filename}'

class HotelierProfile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Hotelier profile')
    name = models.CharField('Hotel Name', max_length=255, blank=True, null=False)
    telephone = models.CharField('Hotel Telephone', max_length=255, blank=True, null=False)
    country = models.CharField('Hotel Country', max_length=255, blank=True, null=False)
    address = models.CharField('Hotel Address', max_length=255, blank=True, null=False)

    picture_url = models.ImageField(upload_to=upload_to, blank=True, null=True)

    class Meta:
        verbose_name = 'Hotelier Profile'
        verbose_name_plural = 'Hotelier Profiles'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.user}'