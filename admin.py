from django.contrib import admin
from .models import StudentProfile, InstructorProfile, Course, CourseModule, Lesson, Enrollment
from django.contrib import messages
from django.contrib.auth.models import Group # Imported but unused (often happens)

# --- 1. Inline Models for Course Structure ---

class LessonInline(admin.TabularInline):
    """Allows lessons to be added/edited directly on the CourseModule page."""
    model = Lesson
    extra = 1 
    fields = ('title', 'lesson_type', 'duration_minutes', 'order')


class CourseModuleInline(admin.TabularInline):
    """Allows modules to be added/edited directly on the Course page."""
    model = CourseModule
    extra = 1 
    fields = ('title', 'description', 'order')


# --- 2. Inline Model for Student Engagement ---

class EnrollmentInline(admin.TabularInline):
    """Allows viewing and managing students enrolled in a Course."""
    model = Enrollment
    extra = 0 # Do not show extra empty forms by default
    fields = ('student', 'enrollment_date', 'is_completed')
    readonly_fields = ('enrollment_date',)
    # Use raw_id_fields for student lookup, very efficient for many students
    raw_id_fields = ('student',) 


# --- 3. Actions ---

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


# --- 4. Model Admin Classes ---

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    # Recommended: Add an Enrollment Inline to see which courses the student is taking
    inlines = [EnrollmentInline] 
    list_display = ('user', 'contact', 'dob', 'created_at')


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact', 'expertise', 'instructor_id', 'approved', 'created_at')
    actions = [approve_instructors]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin view for the main Course model."""
    list_display = ('title', 'instructor', 'category', 'price', 'level', 'is_published', 'student_count', 'created_at')
    list_filter = ('level', 'category', 'is_published', 'created_at')
    search_fields = ('title', 'short_description', 'instructor__user__username')
    prepopulated_fields = {'slug': ('title',)}
    
    # Organize fields into fieldsets for better layout
    fieldsets = (
        ('Course Identification', {
            'fields': ('title', 'slug', 'instructor', 'category', 'level'),
        }),
        ('Description & Media', {
            # FIX: Changed 'thumbnail' to 'image' based on your models.py
            'fields': ('short_description', 'detailed_description', 'image', 'course_video', 'notes_file'),
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_published'),
        }),
    )

    # Use inlines to add/edit modules AND view enrollments directly on the Course page
    inlines = [CourseModuleInline, EnrollmentInline]
    
    # New Method: Display the count of enrolled students in the list view
    def get_queryset(self, request):
        # Annotate queryset with the count of related Enrollment objects
        return super().get_queryset(request).annotate(
            _student_count=Count('enrollments', distinct=True)
        )

    def student_count(self, obj):
        # Access the annotated count
        return obj._student_count
    
    student_count.admin_order_field = '_student_count'
    student_count.short_description = 'Enrolled Students'


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    """Admin view for Course Modules, including lesson inlines."""
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)
    
    inlines = [LessonInline]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    # This remains correct, allowing direct management of enrollment records
    list_display = ('student', 'course', 'enrollment_date', 'is_completed')
    list_filter = ('enrollment_date', 'is_completed', 'course')
    search_fields = ('student__user__username', 'course__title')
    raw_id_fields = ('student', 'course')