from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django import forms

from .models import UserData

class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

admin.site.register(UserData, UserDataAdmin)
