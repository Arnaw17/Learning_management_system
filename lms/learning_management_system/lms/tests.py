from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import StudentProfile, InstructorProfile


class RegistrationTests(TestCase):
	def test_student_registration_creates_profile(self):
		url = reverse('student_register')
		data = {
			'first_name': 'Test',
			'last_name': 'Student',
			'email': 'student@example.com',
			'password': 'strongpass123',
			'password2': 'strongpass123',
			'contact': '9876543210'
		}
		resp = self.client.post(url, data, follow=True)
		self.assertEqual(resp.status_code, 200)
		User = get_user_model()
		user = User.objects.filter(username='student@example.com').first()
		self.assertIsNotNone(user)
		self.assertTrue(StudentProfile.objects.filter(user=user).exists())

	def test_instructor_registration_creates_profile_and_staff(self):
		url = reverse('instructor_register')
		data = {
			'name': 'Prof Test',
			'email': 'instructor@example.com',
			'password': 'instrpass123',
			'password2': 'instrpass123',
			'contact': '9876543211',
			'expertise': 'python'
		}
		resp = self.client.post(url, data, follow=True)
		self.assertEqual(resp.status_code, 200)
		User = get_user_model()
		user = User.objects.filter(username='instructor@example.com').first()
		self.assertIsNotNone(user)
		# Instructors are not staff until approved by admin
		self.assertFalse(user.is_staff)
		self.assertTrue(InstructorProfile.objects.filter(user=user).exists())
		profile = InstructorProfile.objects.get(user=user)
		self.assertFalse(profile.approved)
