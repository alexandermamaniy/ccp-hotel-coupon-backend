import enum
from django.db import models
import uuid
from core.models import TimeStampedModel

def upload_to(instance, filename):
    return f'coupons/{filename}'

class Coupon(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Title', max_length=255, blank=False, null=False)
    description = models.TextField('Description', blank=True, null=True)
    discount = models.PositiveIntegerField('Discount', default=0)
    media_url = models.ImageField(upload_to=upload_to, blank=True, null=True)
    quantity = models.PositiveIntegerField('Quantity', default=0)
    how_many_have_redeemed = models.PositiveIntegerField('How many coupons have been redemeed', default=0)
    expiration_date = models.DateTimeField('Expiration date', blank=True, null=True)
    hotelier_profile = models.ForeignKey('hotelier_profiles.HotelierProfile', on_delete=models.CASCADE, verbose_name='Hotelier profile')

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} - {self.hotelier_profile}'