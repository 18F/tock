from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import UserData, EmployeeGrade

class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user',)

class EmployeeGradeAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserData, UserDataAdmin)
admin.site.register(EmployeeGrade, EmployeeGradeAdmin)
