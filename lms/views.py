from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import StudentProfile, InstructorProfile, Course # <-- ADD Course model
from .forms import StudentRegistrationForm, InstructorRegistrationForm, LoginForm, CourseCreationForm, Course, InstructorProfile # <-- ADD CourseCreationForm
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
    try:
        # Check if the user has an approved InstructorProfile
        profile = request.user.instructor_profile
        if not profile.approved:
            messages.error(request, 'Your instructor account is pending admin approval.')
            logout(request) # Log out unapproved instructors
            return redirect('home')
    except InstructorProfile.DoesNotExist:
        messages.error(request, 'You do not have an instructor profile.')
        return redirect('home')

    return render(request, 'lms/instructordash.html')


@login_required
def instructor_create_course(request):
    try:
        # 1. RETRIEVE THE PROFILE: Get the specific InstructorProfile associated with the logged-in User
        instructor_profile = request.user.instructor_profile # Assumes related_name is 'instructorprofile' or default
        
    except InstructorProfile.DoesNotExist:
        # Handle the case where a logged-in user doesn't have an instructor profile (shouldn't happen post-login check)
        messages.error(request, 'Instructor profile not found. Please contact support.')
        return redirect('instructor_dashboard')
    if request.method == 'POST':
        # Handle form submission logic
        form = CourseCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the course logic
            course = form.save(commit=False)
            # IMPORTANT: Ensure the Course model has an 'instructor' field linked to User
            course.instructor = instructor_profile 
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('instructor_dashboard') 
        else:
            messages.error(request, 'There was an error in the form. Please correct the fields.')
    else:
        # GET request: create a new, empty form instance
        form = CourseCreationForm() 

    # The 'form' variable must be included in the context dictionary for the template to render the fields
    context = {
        'form': form,
    }
    # FIX: Using the assumed correct template path and name
    return render(request, 'lms/instructor_create_course.html', context) 

@login_required
def instructor_my_courses(request):
    # Ensure the user has a valid and approved InstructorProfile
    try:
        # Retrieve the InstructorProfile instance for the logged-in user
        instructor_profile = get_object_or_404(InstructorProfile, user=request.user)
        
    except Exception:
        messages.error(request, 'You do not have a valid instructor profile.')
        return redirect('home')

    # Fetch all courses linked to this specific InstructorProfile
    my_courses = Course.objects.filter(instructor=instructor_profile).order_by('-created_at') # Assuming 'created_at' exists

    context = {
        'my_courses': my_courses,
        'profile': instructor_profile,
    }
    
    # Render the new template
    return render(request, 'lms/instructor_my_courses.html', context)

@login_required
def instructor_edit_course(request, pk):
    # 1. Security Check: Retrieve the InstructorProfile for the logged-in user
    try:
        instructor_profile = get_object_or_404(InstructorProfile, user=request.user)
    except Exception:
        messages.error(request, 'Profile error. Please log in again.')
        return redirect('instructor_dashboard')

    # 2. Retrieve Course: Ensure the course exists AND belongs to the logged-in instructor
    course = get_object_or_404(
        Course, 
        pk=pk, 
        instructor=instructor_profile
    )

    if request.method == 'POST':
        # 3. Handle POST: Pass the request data, files, and the existing instance
        form = CourseCreationForm(request.POST, request.FILES, instance=course)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully! 👍')
            return redirect('instructor_my_courses')
        else:
            # Show errors if validation fails
            messages.error(request, 'Error updating course. Please check the fields.')
    
    else:
        # 4. Handle GET: Pre-populate the form with the existing course instance data
        form = CourseCreationForm(instance=course)

    context = {
        'form': form,
        'course': course, # Pass the course instance to the template
    }
    
    # 5. Render the editing template. We can reuse the creation template.
    # Note: If reusing, ensure the H1/title in the template reflects "Edit Course"
    return render(request, 'lms/instructor_edit_course.html', context)

@login_required
@require_http_methods(["POST"]) # Use POST for security, even if the intention is deletion
def instructor_delete_course(request, pk):
    # 1. Security Check: Retrieve the InstructorProfile
    try:
        instructor_profile = get_object_or_404(InstructorProfile, user=request.user)
    except Exception:
        messages.error(request, 'Profile error. Cannot delete course.')
        return redirect('instructor_my_courses')

    # 2. Retrieve Course: Ensure the course exists AND belongs to the logged-in instructor
    course = get_object_or_404(
        Course, 
        pk=pk, 
        instructor=instructor_profile # Critical security check!
    )
    
    course_title = course.title
    
    # 3. Perform Deletion
    try:
        course.delete()
        messages.success(request, f'Course "{course_title}" was successfully deleted. 🗑️')
    except Exception as e:
        messages.error(request, f'An error occurred while deleting "{course_title}": {e}')
        
    return redirect('instructor_my_courses')


def explore_courses_view(request):
    """Fetches all published courses for the Explore page."""
    # Assuming is_published=True means the course is ready for students
    all_courses = Course.objects.filter(is_published=True).order_by('-created_at')
    
    context = {
        'courses': all_courses,
    }
    # Renders the new template
    return render(request, 'lms/explore_courses.html', context)
# In your views.py

# ... (Existing imports: Course, messages, login_required, etc.) ...

def course_detail_view(request, course_slug):
    # Fetch the course using the slug
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    
    has_access = False
    
    if request.user.is_authenticated:
        # Check if the user is an instructor (they always have access)
        if hasattr(request.user, 'instructor_profile'):
             has_access = True
        
        # Check if the user is enrolled (assuming StudentProfile has enrolled_courses field)
        try:
            student_profile = request.user.student_profile
            if student_profile.enrolled_courses.filter(slug=course_slug).exists():
                has_access = True
        except StudentProfile.DoesNotExist:
            # User is logged in but isn't a student/instructor (shouldn't happen often)
            pass

    context = {
        'course': course,
        'has_access': has_access,
        'is_logged_in': request.user.is_authenticated,
    }
    return render(request, 'lms/course_detail.html', context)


# Update the existing purchase_course stub for the new flow
def purchase_course(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to purchase a course.")
        return redirect('student_login') 

    # Logic to process purchase (e.g., handle payment form submission)
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        
        # Placeholder for successful payment processing
        
        try:
            student_profile = request.user.student_profile
            # Add course to student's enrolled list
            student_profile.enrolled_courses.add(course) 
            messages.success(request, f'Purchase successful! You are now enrolled in "{course.title}".')
            # Redirect to the course detail page to grant full access
            return redirect('course_detail', course_slug=course.slug) 
            
        except StudentProfile.DoesNotExist:
            messages.error(request, 'Could not complete enrollment. Student profile not found.')
            return redirect('home')
        
    messages.error(request, 'Invalid purchase request.')
    return redirect('explore_courses')
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


# Consolidated the two definitions of instructor_create_course above.
# The remaining stub views are fine, assuming they point to the correct templates.

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