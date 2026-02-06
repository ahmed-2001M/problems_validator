from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Assignment, Task, TestCase, Submission

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role', 'is_approved')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Assignment)
admin.site.register(Task)
admin.site.register(TestCase)
admin.site.register(Submission)
