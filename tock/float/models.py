from django.db import models

class FloatTasks(models.Model):
     task_id = models.CharField(max_length=200, blank=True)
     task_name = models.CharField(max_length=500, blank=True)
     people_id = models.CharField(max_length=200, blank=True)
     person_name = models.CharField(max_length=500, blank=True)
     project_id = models.CharField(max_length=200, blank=True)
     project_name = models.CharField(max_length=500, blank=True)
     client_name = models.CharField(max_length=500, blank=True)
     start_date = models.DateField(null=True)
     end_date = models.DateField(null=True)
     hours_pd = models.CharField(max_length=200, blank=True)
     task_cal_days = models.CharField(max_length=200, blank=True)
     created_by = models.CharField(max_length=500, blank=True)
     creator_id = models.CharField(max_length=200, blank=True)
     modified_by = models.CharField(max_length=500, blank=True)
     priority = models.CharField(max_length=200, blank=True)

     class Meta:
        verbose_name = "Float Task Data"
        verbose_name_plural = "Float Task Data"

        def __str__(self):
            return '%s - %s (%s)' % (self.person_name, self.project_name)
