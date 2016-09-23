from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import UserData

class EmployeeDataAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


admin.site.register(UserData)
