from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class UserData(models.Model):
	user = models.OneToOneField(User, related_name='user_data')
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)