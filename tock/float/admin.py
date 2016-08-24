from django.contrib import admin
from .models import FloatTasks

class FloatTasksAdmin(admin.ModelAdmin):
    readonly_fields = ('tock_pk',)

admin.site.register(FloatTasks, FloatTasksAdmin)
