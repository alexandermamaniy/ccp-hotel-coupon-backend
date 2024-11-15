from django.db import models
import uuid
from users.models import User
from core.models import TimeStampedModel

from coupons.models import Coupon


def upload_to(instance, filename):
    return f'user-profiles/{filename}'


class CouponUserProfile(TimeStampedModel):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile_id = models.ForeignKey('user_profiles.UserProfile', on_delete=models.CASCADE)
    coupon_id = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user_profile_id.full_name} - {self.coupon_id.title}'


class UserProfile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='User profile')
    full_name = models.CharField('Full name', max_length=255, blank=True, null=False)

    picture_url = models.ImageField(upload_to=upload_to, blank=True, null=True)

    coupons = models.ManyToManyField(Coupon, through="CouponUserProfile" ,related_name='profiles')

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} - {self.user}'