from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

# =========================================================
# User Profile Models
# =========================================================

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    contact = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # NEW: Many-to-Many relationship with Course via the Enrollment model
    enrolled_courses = models.ManyToManyField(
        'Course',
        through='Enrollment',  # Use the intermediate model
        related_name='enrolled_students'
    )

    def __str__(self):
        return f"StudentProfile({self.user.username})"


class InstructorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    contact = models.CharField(max_length=20, blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    instructor_id = models.CharField(max_length=32, unique=True, blank=True)
    
    # NEW FIELD: Profile Image
    profile_image = models.ImageField(
        upload_to='instructor_profiles/', 
        null=True, 
        blank=True,
        verbose_name="Profile Picture"
    )
    
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"InstructorProfile({self.user.username})"

# =========================================================
# Course Models (Required for Course Creation)
# =========================================================

class Course(models.Model):
    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    # Core details
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    detailed_description = models.TextField(blank=True)
    outline = models.TextField(blank=True, verbose_name="Course Outline") 
    
    # Relationships
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='courses')
    category = models.CharField(max_length=100) 

    # Pricing and Media
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True) 
    course_video = models.FileField(upload_to='course_videos/', null=True, blank=True)
    notes_file = models.FileField(upload_to='course_notes/', null=True, blank=True)
    
    # Status and Metadata
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            # The original logic for ensuring a unique slug remains here...
            if Course.objects.filter(slug=unique_slug).exists():
                 unique_slug = f'{base_slug}-{uuid.uuid4().hex[:4]}'
            self.slug = unique_slug
        super().save(*args, **kwargs)


class CourseModule(models.Model):
    """A section or chapter within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('course', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title}: Module {self.order} - {self.title}"


class Lesson(models.Model):
    """An individual unit of content (video, text, quiz) within a module."""
    LESSON_TYPES = (
        ('video', 'Video'),
        ('text', 'Reading/Article'),
        ('quiz', 'Quiz'),
    )
    
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPES, default='video')
    content_url = models.URLField(max_length=500, blank=True) 
    content_text = models.TextField(blank=True) 
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Duration in minutes (0 for reading)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('module', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title}: Lesson {self.order} - {self.title}"

# =========================================================
# NEW: Student Enrollment/Engagement Model
# =========================================================

class Enrollment(models.Model):
    """
    Intermediate model to track student enrollment in a course.
    This serves as your 'student_engagement' database.
    """
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    # Optional: Add fields to track engagement, e.g., completion status
    is_completed = models.BooleanField(default=False) 
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Ensures a student can only enroll in the same course once
        unique_together = ('student', 'course') 
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.title}"
    

