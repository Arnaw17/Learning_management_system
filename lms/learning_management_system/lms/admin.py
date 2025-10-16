from django.contrib import admin
from .models import StudentProfile, InstructorProfile
from django.contrib import messages


def approve_instructors(modeladmin, request, queryset):
	updated = 0
	for profile in queryset:
		if not profile.approved:
			profile.approved = True
			profile.save()
			user = profile.user
			user.is_staff = True
			user.save()
			updated += 1
	messages.success(request, f"{updated} instructor(s) approved and promoted to staff.")


approve_instructors.short_description = 'Approve selected instructors'


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'contact', 'dob', 'created_at')


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'contact', 'expertise', 'instructor_id', 'approved', 'created_at')
	actions = [approve_instructors]
