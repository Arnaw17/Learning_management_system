from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import StudentProfile, InstructorProfile
from .forms import StudentRegistrationForm, InstructorRegistrationForm, LoginForm

User = get_user_model()


def home(request):
	return render(request, 'lms/index.html')


@ensure_csrf_cookie
def student_login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data['user']
			remember = form.cleaned_data.get('remember_me')
			login(request, user)
			if remember:
				# Two weeks
				request.session.set_expiry(1209600)
			else:
				# Browser session
				request.session.set_expiry(0)
			return redirect('home')
		else:
			messages.error(request, form.errors.as_text())
	else:
		form = LoginForm()
	return render(request, 'lms/log.html', {'form': form})


def student_register(request):
	if request.method == 'POST':
		form = StudentRegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages.success(request, 'Registration successful. Please log in.')
			return redirect('student_login')
	else:
		form = StudentRegistrationForm()
	return render(request, 'lms/reg.html', {'form': form})


@ensure_csrf_cookie
def instructor_login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data['user']
			remember = form.cleaned_data.get('remember_me')
			# Check for an InstructorProfile and whether it's approved by admin
			profile = InstructorProfile.objects.filter(user=user).first()
			if profile and profile.approved:
				# Ensure the user has staff flag set so Django permissions work consistently
				if not user.is_staff:
					user.is_staff = True
					user.save()
				login(request, user)
				if remember:
					request.session.set_expiry(1209600)
				else:
					request.session.set_expiry(0)
				return redirect('instructor_dashboard')
			# Profile exists but not approved yet
			if profile and not profile.approved:
				messages.error(request, 'Your instructor account is pending admin approval.')
			else:
				messages.error(request, 'You are not an instructor or your instructor profile is missing')
		else:
			messages.error(request, form.errors.as_text())
	else:
		form = LoginForm()
	return render(request, 'lms/instructorlogin.html', {'form': form})


@ensure_csrf_cookie
def instructor_register(request):
	if request.method == 'POST':
		form = InstructorRegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages.success(request, 'Instructor registration successful. Please log in.')
			return redirect('instructor_login')
	else:
		form = InstructorRegistrationForm()
	return render(request, 'lms/instructorreg.html', {'form': form})


@login_required
def instructor_dashboard(request):
	# You may want to check is_staff again
	if not request.user.is_staff:
		messages.error(request, 'Access denied')
		return redirect('home')
	return render(request, 'lms/instructordash.html')


def course_python(request):
	return render(request, 'lms/python.html')


def course_javascript(request):
	return render(request, 'lms/javascript.html')


def course_java(request):
	return render(request, 'lms/Java.html')


def course_cpp(request):
	return render(request, 'lms/C++.html')


def logout_view(request):
	logout(request)
	return redirect('home')


def instructor_create_course(request):
	return render(request, 'lms/instructordash.html')


def instructor_manage_courses(request):
	return render(request, 'lms/instructordash.html')


def instructor_add_quiz(request):
	return render(request, 'lms/instructordash.html')


def instructor_create_coupon(request):
	return render(request, 'lms/instructordash.html')


def instructor_engagement(request):
	return render(request, 'lms/instructordash.html')


def instructor_request_payout(request):
	return render(request, 'lms/instructordash.html')


def purchase_course(request):
	# Minimal purchase stub - in a real app you'd integrate payment here
	messages.info(request, 'Purchase flow is not implemented in this demo')
	return redirect('home')

