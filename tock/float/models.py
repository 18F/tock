from django.db import models


class FloatTasks(models.Model):
    people_id = models.CharField(max_length=200, null=True)
    hours_pd = models.CharField(max_length=200, null=True)
    repeat_end = models.CharField(max_length=200, null=True)
    modified_by = models.CharField(max_length=200, null=True)
    task_cal_days = models.CharField(max_length=200, null=True)
    tentative = models.CharField(max_length=200, null=True)
    client_name = models.CharField(max_length=200, null=True)
    created_by = models.CharField(max_length=200, null=True)
    priority = models.CharField(max_length=200, null=True)
    project_id = models.CharField(max_length=200, null=True)
    start_date = models.DateField(null=True)
    project_name = models.CharField(max_length=200, null=True)
    person_name = models.CharField(max_length=200, null=True)
    end_date = models.DateField(null=True)
    repeat_state = models.CharField(max_length=200, null=True)
    task_notes = models.CharField(max_length=200, null=True)
    task_days = models.CharField(max_length=200, null=True)
    task_id = models.CharField(max_length=200, null=True)
    total_hours = models.CharField(max_length=200, null=True)
    creator_id = models.CharField(max_length=200, null=True)
    task_name = models.CharField(max_length=200, null=True)
    start_yr = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = "Float Task Data"
        verbose_name_plural = "Float Task Data"

    def __str__(self):
        return '%s - %s' % (self.person_name, self.task_id)

class FloatPeople(models.Model):
    people_id = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=500, blank=True)
    job_title = models.CharField(max_length=500, blank=True)
    email = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    im = models.CharField(max_length=500, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Float People Data"
        verbose_name_plural = "Float People Data"

        def __str__(self):
            return '%s (%s)' % (self.name, self.job_title)
