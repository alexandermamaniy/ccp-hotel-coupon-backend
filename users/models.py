from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from pytz import all_timezones
from core.models import TimeStampedModel
class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff=False, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email,  password=None, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):

    email = models.CharField(max_length = 255, unique = True)
    is_staff = models.BooleanField(default = False)
    timezone = models.CharField(max_length=100, choices=[(tz, tz) for tz in all_timezones], default='UTC')

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    USERNAME_FIELD = 'email'

    def natural_key(self):
        return (self.email)

    def __str__(self):
        return f'email: {self.email}'