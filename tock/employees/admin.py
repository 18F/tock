from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import Employee

class EmployeeCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields"""

    class Meta:
        model = Employee
        fields = (
            'email',
            'first_name',
            'last_name',
            'start_date',
            'end_date',
            'is_admin'
            )

        def save(self, commit=True):
            employee = super(EmployeeCreationForm, self).save(commit=False)
            if commit:
                employee.save()

            return employee

class EmployeeChangeForm(forms.ModelForm):
    """A form for updating employees.
    """

    class Meta:
        model = Employee
        fields = (
            'email',
            'first_name',
            'last_name',
            'start_date',
            'end_date',
            'is_admin'
            )

class EmployeeAdmin(UserAdmin):
    # The forms to add and change user instances
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'start_date', 'end_date')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Employment info', {'fields': ('start_date', 'end_date')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. EmployeeAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()



admin.site.register(Employee, EmployeeAdmin)
admin.site.unregister(Group)
