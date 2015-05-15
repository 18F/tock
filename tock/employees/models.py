from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
# Create your models here.
from django.contrib.auth.models import User


class UserData(models.Model):
    user = models.OneToOneField(User, related_name='user_data')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
