from django.contrib import admin
from .models import StudentProfile, InstructorProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'contact', 'dob', 'created_at')


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'contact', 'expertise', 'created_at')
