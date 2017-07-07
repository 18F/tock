from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.db.models import Q, Max

from rest_framework.authtoken.models import Token

from projects.models import ProfitLossAccount

class UserData(models.Model):
    user = models.OneToOneField(User, related_name='user_data', verbose_name='Tock username')
    start_date = models.DateField(blank=True, null=True, verbose_name='Employee start date')
    end_date = models.DateField(blank=True, null=True, verbose_name='Employee end date')
    current_employee = models.BooleanField(default=True, verbose_name='Is Current Employee')

    class Meta:
        verbose_name='Employee'
        verbose_name_plural='Employees'

    def __str__(self):
        return '%s' % (self.user)

    def save(self, *args, **kwargs):
        """Aligns User model and UserData model attributes on save."""
        user = User.objects.get(username=self.user)
        if self.current_employee:
            user.is_active = True
        else:
            user.is_active = False
            user.is_superuser = False
            user.is_staff = False
            user.save()
            try:
                token = Token.objects.get(user=self.user)
                token.delete()
            except Token.DoesNotExist:
                pass
        user.save()

        super(UserData, self).save(*args, **kwargs)
