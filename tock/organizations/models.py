from django.db import models
from django.utils.text import slugify


class Organization(models.Model):
    """
    For use with identifying what organization manages/owns/controls
    something.
    """

    name = models.CharField(max_length=512, verbose_name='Organization Name')
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    To define business units within a given org. 
    For example, "Engineering Chapter" or "Human Services Portfolio"
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    org = models.ForeignKey(Organization, default=1, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, help_text="Uncheck if it is not a current business unit")
    
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Unit, self).save(*args, **kwargs)
