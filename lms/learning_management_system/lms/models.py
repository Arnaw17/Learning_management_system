from django.db import models
from django.conf import settings


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
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"InstructorProfile({self.user.username})"
