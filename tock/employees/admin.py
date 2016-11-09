from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import UserData, EmployeeGrade

class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


class EmployeeGradeAdmin(admin.ModelAdmin):
    search_fields = ('employee__username',)

admin.site.register(UserData, UserDataAdmin)
admin.site.register(EmployeeGrade, EmployeeGradeAdmin)
