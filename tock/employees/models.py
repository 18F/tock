import os
import json
import requests

from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db.models import Q, Max


class EmployeeGrade(models.Model):
    GRADE_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
        (13, '13'),
        (14, '14'),
        (15, '15'),
        (16, 'SES')
    )
    employee = models.ForeignKey(
        User,
        help_text='Please select from existing employees.'
    )
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        help_text='Please select a GS grade level.',
        unique_for_date='g_start_date'
    )
    g_start_date = models.DateField(
        help_text='Please select a start date for this grade.',
        verbose_name='Grade start date'
    )

    def __str__(self):
        return '{0} - {1} (Starting: {2})'.format(self.employee, self.grade, self.g_start_date)

    def get_grade(end_date, user):
        """Gets grade information based on a date and user. Original use of
        function is to append correct grade information to each
        TimecardObject."""
        queryset = EmployeeGrade.objects.filter(
                Q(employee = user)
                & Q(g_start_date__lte = end_date)
                ).all()
        if queryset:
            return queryset.latest('g_start_date')
        else:
            return None

class UserData(models.Model):

    UNIT_CHOICES = (
        (0, 'Operations-Team Operations'),
        (1, 'Operations-Talent'),
        (2, 'Operations-Infrastructure'),
        (3, 'Operations-Front Office'),
        (4, 'Chapters-Acquisition Managers'),
        (5, 'Chapters-Engineering'),
        (6, 'Chapters-Experience Design'),
        (7, 'Chapters-Product'),
        (8, 'Chapters-Strategists'),
        (9, 'Business-Acquisition Services'),
        (10, 'Business-Custom Partner Solutions'),
        (11, 'Business-Learn'),
        (12, 'Business-Products & Platforms'),
        (13, 'Business-Transformation Services'),
        (14, 'PIF-Fellows'),
        (15, 'PIF-Operations'),
        (16, 'Unknown / N/A')
    )

    user = models.OneToOneField(User, related_name='user_data', verbose_name='Tock username')
    start_date = models.DateField(blank=True, null=True, verbose_name='Employee start date')
    end_date = models.DateField(blank=True, null=True, verbose_name='Employee end date')
    current_employee = models.BooleanField(default=True, verbose_name='Is Current Employee')
    is_18f_employee = models.BooleanField(default=True, verbose_name='Is 18F Employee')
    is_billable = models.BooleanField(default=True, verbose_name="Is 18F Billable Employee")
    unit = models.IntegerField(null=True, choices=UNIT_CHOICES, verbose_name="Select 18F unit", blank=True)
    float_people_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='Float "people_id" attribute')

    class Meta:
        verbose_name='Employee'
        verbose_name_plural='Employees'

    def __str__(self):
        return '{0}'.format(self.user)

    def get_people_id(request):
        req_user = UserData.objects.get(user=request.user)

        if req_user.float_people_id is None:
            url = 'https://api.floatschedule.com/api/v1/'
            headers = {'Authorization': 'Bearer ' + os.environ.get('FLOAT_API_KEY')}
            endpoint = 'people'
            r = requests.get(url + endpoint, headers=headers)
            people_data = json.loads(r.content.decode().lower().strip())

            for i in people_data['people']:
                if i['im'] == req_user.user.username:
                    req_user.float_people_id = i['people_id']
                    req_user.save()

        return req_user.float_people_id

    def get_task_data(float_people_id):
        url = 'https://api.floatschedule.com/api/v1/'
        headers = {'Authorization': 'Bearer ' + os.environ.get('FLOAT_API_KEY')}
        endpoint = 'tasks'
        params = {'weeks': 1}
        r = requests.get(url + endpoint, headers=headers, params=params)
        task_data = json.loads(r.content.decode().lower().strip())


        for person_tasks in task_data['people']:
            if person_tasks['people_id'] == float_people_id:
                return person_tasks
            else:
                return None

    def save(self, *args, **kwargs):
        if self.current_employee is False:
            try:
                token = Token.objects.get(user=self.user)
                token.delete()
            except Token.DoesNotExist:
                pass

        super(UserData, self).save(*args, **kwargs)
