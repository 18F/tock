from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserData

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserDataInline(admin.StackedInline):
    model = UserData
    can_delete = False
    verbose_name_plural = 'User Data'

# Define a new User admin
class UserAdmin(UserAdmin):
	inlines = (UserDataInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)