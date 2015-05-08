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


class EmployeeManager(BaseUserManager):

    def create_user(self, email):
        """
        Creates and saves an Employee with the given email address.
        """
        if not email:
            raise ValueError('Employees must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.save(using=self.db)
        return user


class Employee(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(blank=True, max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    objects = EmployeeManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
