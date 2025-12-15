from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Post, Job, Event, JobApplication

# Register Custom User Model
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_alumni')}),
    )
    list_display = ['username', 'email', 'is_student', 'is_alumni']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'industry', 'graduation_year']
    search_fields = ['user__username', 'industry']

class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'posted_by', 'created_at']
    list_filter = ['job_type', 'created_at']

class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created_at']

# Register all models for the Admin Dashboard module
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Event)
admin.site.register(JobApplication)