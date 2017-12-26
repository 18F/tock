from django.db import models


class Organization(models.Model):
    """For use with identifying what organization manages/owns/controls
    something."""

    name = models.CharField(max_length=512, verbose_name='Organization Name')
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
