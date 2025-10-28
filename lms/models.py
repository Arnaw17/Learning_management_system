from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    contact = models.CharField(max_length=20, blank=True)
    dob = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StudentProfile({self.user.username})"


class InstructorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    contact = models.CharField(max_length=20, blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    instructor_id = models.CharField(max_length=32, unique=True, blank=True)
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
    
    # FIX: Added 'outline' field (was missing)
    outline = models.TextField(blank=True, verbose_name="Course Outline") 
    
    # Relationships
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='courses')
    category = models.CharField(max_length=100) # You might want a separate Category model later

    # Pricing and Media
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # FIX: Renamed 'thumbnail' to 'image' (was 'image' in your form)
    image = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True) 
    
    # FIX: Added 'course_video' field (was missing)
    course_video = models.FileField(upload_to='course_videos/', null=True, blank=True)
    
    # FIX: Added 'notes_file' field (was missing)
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
        # Auto-generate slug if it's not set
        if not self.slug:
            base_slug = slugify(self.title)
            # Ensure slug is unique by appending a short UUID if necessary
            unique_slug = base_slug
            counter = 1
            while Course.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{uuid.uuid4().hex[:4]}'
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class CourseModule(models.Model):
    """A section or chapter within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        # Ensure order is unique within the context of a single course
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
    content_url = models.URLField(max_length=500, blank=True) # For video link or other resource
    content_text = models.TextField(blank=True) # For text-based lessons
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Duration in minutes (0 for reading)")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        # Ensure order is unique within the context of a single module
        unique_together = ('module', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title}: Lesson {self.order} - {self.title}"