from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import UserData

class EmployeeDataAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(UserData)
