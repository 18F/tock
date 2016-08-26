from django.contrib import admin
from .models import FloatTasks

class FloatTasksAdmin(admin.ModelAdmin):
    readonly_fields = ('tock_pk',)
    search_fields = ('im', 'project_name')

admin.site.register(FloatTasks, FloatTasksAdmin)
