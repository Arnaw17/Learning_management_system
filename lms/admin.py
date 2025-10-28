from django.contrib import admin
from .models import StudentProfile, InstructorProfile, Course, CourseModule, Lesson # <-- UPDATE IMPORTS
from django.contrib import messages
from django.contrib.auth.models import Group

# --- Inline Models for Course Structure ---

class LessonInline(admin.TabularInline):
    """Allows lessons to be added/edited directly on the CourseModule page."""
    model = Lesson
    extra = 1  # Display 1 empty form by default
    fields = ('title', 'lesson_type', 'duration_minutes', 'order')


class CourseModuleInline(admin.TabularInline):
    """Allows modules to be added/edited directly on the Course page."""
    model = CourseModule
    extra = 1 # Display 1 empty form by default
    # Note: If you want to use LessonInline here, you'd use admin.StackedInline 
    # and override get_formset, but for simplicity, we'll keep it flat.
    fields = ('title', 'description', 'order')

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

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin view for the main Course model."""
    list_display = ('title', 'instructor', 'category', 'price', 'level', 'is_published', 'created_at')
    list_filter = ('level', 'category', 'is_published', 'created_at')
    search_fields = ('title', 'short_description', 'instructor__user__username')
    prepopulated_fields = {'slug': ('title',)}
    
    # Organize fields into fieldsets for better layout
    fieldsets = (
        ('Course Identification', {
            'fields': ('title', 'slug', 'instructor', 'category', 'level'),
        }),
        ('Description & Media', {
            'fields': ('short_description', 'detailed_description', 'thumbnail'),
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_published'),
        }),
    )

    # Use inline to add/edit modules directly on the Course page
    inlines = [CourseModuleInline]

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    """Admin view for Course Modules, including lesson inlines."""
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)
    
    # Use inline to add/edit lessons directly on the Course Module page
    inlines = [LessonInline]

# Optionally, register Lesson separately if needed, but it's often better handled via ModuleInline
# @admin.register(Lesson)
# class LessonAdmin(admin.ModelAdmin):
#     list_display = ('title', 'module', 'lesson_type', 'duration_minutes', 'order')
#     list_filter = ('lesson_type', 'module__course')