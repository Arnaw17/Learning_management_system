from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q # Added for dashboard analytics later

# IMPORTANT MODEL IMPORTS
from .models import StudentProfile, InstructorProfile, Course, Enrollment 

# IMPORTANT FORM IMPORTS (Assuming Enrollment is correctly imported from forms.py)
from .forms import StudentRegistrationForm, InstructorRegistrationForm, LoginForm, CourseCreationForm, InstructorProfileEditForm

User = get_user_model()

# =========================================================
# CORE AUTH VIEWS
# =========================================================

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
                request.session.set_expiry(1209600)
            else:
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
            profile = InstructorProfile.objects.filter(user=user).first()
            if profile and profile.approved:
                if not user.is_staff:
                    user.is_staff = True
                    user.save()
                login(request, user)
                if remember:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)
                return redirect('instructor_dashboard')
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

def logout_view(request):
    logout(request)
    return redirect('home')


# =========================================================
# INSTRUCTOR DASHBOARD & COURSE MANAGEMENT VIEWS
# =========================================================

@login_required
def instructor_dashboard(request):
    try:
        profile = request.user.instructor_profile
        if not profile.approved:
            messages.error(request, 'Your instructor account is pending admin approval.')
            logout(request)
            return redirect('home')
    except InstructorProfile.DoesNotExist:
        messages.error(request, 'You do not have an instructor profile.')
        return redirect('home')

    # Fetch data for the dashboard KPI cards
    instructor_courses = Course.objects.filter(instructor=profile)
    total_courses = instructor_courses.count()
    
    # Calculate total unique students enrolled in the instructor's courses
    total_enrolled_students = Enrollment.objects.filter(
        course__in=instructor_courses
    ).values('student').annotate(count=Count('student')).count()
    
    # Fetch recent enrollments for the dashboard feed
    recent_enrollments = Enrollment.objects.filter(
        course__in=instructor_courses
    ).select_related('student__user', 'course').order_by('-enrollment_date')[:5]

    context = {
        'total_courses': total_courses,
        'total_enrolled_students': total_enrolled_students,
        'recent_enrollments': recent_enrollments,
    }

    return render(request, 'lms/instructordash.html', context)


@login_required
def instructor_create_course(request):
    try:
        instructor_profile = request.user.instructor_profile
    except InstructorProfile.DoesNotExist:
        messages.error(request, 'Instructor profile not found.')
        return redirect('instructor_dashboard')
        
    if request.method == 'POST':
        form = CourseCreationForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = instructor_profile 
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('instructor_dashboard') 
        else:
            messages.error(request, 'There was an error in the form. Please correct the fields.')
    else:
        form = CourseCreationForm() 

    context = {'form': form}
    return render(request, 'lms/instructor_create_course.html', context) 

@login_required
def instructor_my_courses(request):
    try:
        instructor_profile = get_object_or_404(InstructorProfile, user=request.user)
    except Exception:
        messages.error(request, 'You do not have a valid instructor profile.')
        return redirect('home')

    my_courses = Course.objects.filter(instructor=instructor_profile).order_by('-created_at')

    context = {
        'my_courses': my_courses,
        'profile': instructor_profile,
    }
    
    return render(request, 'lms/instructor_my_courses.html', context)

@login_required
def instructor_edit_course(request, pk):
    try:
        instructor_profile = get_object_or_404(InstructorProfile, user=request.user)
    except Exception:
        messages.error(request, 'Profile error. Please log in again.')
        return redirect('instructor_dashboard')

    course = get_object_or_404(
        Course, 
        pk=pk, 
        instructor=instructor_profile
    )

    if request.method == 'POST':
        form = CourseCreationForm(request.POST, request.FILES, instance=course)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.title}" updated successfully! 👍')
            return redirect('instructor_my_courses')
        else:
            messages.error(request, 'Error updating course. Please check the fields.')
    
    else:
        form = CourseCreationForm(instance=course)

    context = {'form': form, 'course': course}
    return render(request, 'lms/instructor_edit_course.html', context)

@login_required
@require_http_methods(["POST"])
def instructor_delete_course(request, pk):
    try:
        instructor_profile = get_object_or_404(InstructorProfile, user=request.user)
    except Exception:
        messages.error(request, 'Profile error. Cannot delete course.')
        return redirect('instructor_my_courses')

    course = get_object_or_404(
        Course, 
        pk=pk, 
        instructor=instructor_profile
    )
    
    course_title = course.title
    
    try:
        course.delete()
        messages.success(request, f'Course "{course_title}" was successfully deleted. 🗑️')
    except Exception as e:
        messages.error(request, f'An error occurred while deleting "{course_title}": {e}')
        
    return redirect('instructor_my_courses')

# =========================================================
# STUDENT ENGAGEMENT VIEW (The main fix)
# =========================================================

@login_required
def instructor_engagement_view(request):
    """Fetches and displays all enrollment records for the instructor's courses."""
    try:
        # CRITICAL: Ensure the user is an instructor
        instructor_profile = request.user.instructor_profile
    except InstructorProfile.DoesNotExist:
        messages.error(request, "Access Denied. You do not have an instructor profile.")
        return redirect('instructor_dashboard') 
    
    # Get all courses taught by this instructor
    instructor_courses = instructor_profile.courses.all()
    
    # Filter Enrollment records linked to these courses
    all_enrollments = Enrollment.objects.filter(
        course__in=instructor_courses
    ).select_related('student__user', 'course').order_by('-enrollment_date')
    
    context = {'all_enrollments': all_enrollments}
    
    # RENDER THE CORRECT TEMPLATE NAME
    return render(request, 'lms/instructor_engagement.html', context) 


# =========================================================
# COURSE BROWSING & ACCESS VIEWS
# =========================================================

def explore_courses_view(request):
    all_courses = Course.objects.filter(is_published=True).order_by('-created_at')
    context = {'courses': all_courses}
    return render(request, 'lms/explore_courses.html', context)

def course_detail_view(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    has_access = False
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'instructor_profile') and course.instructor == request.user.instructor_profile:
             has_access = True
        
        try:
            student_profile = request.user.student_profile
            # Check the M2M relationship via the custom Enrollment model
            if Enrollment.objects.filter(student=student_profile, course=course).exists():
                 has_access = True
        except StudentProfile.DoesNotExist:
            pass

    context = {
        'course': course,
        'has_access': has_access,
        'is_logged_in': request.user.is_authenticated,
    }
    return render(request, 'lms/course_detail.html', context)

def purchase_course(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to purchase a course.")
        return redirect('student_login') 

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, pk=course_id)
        
        try:
            student_profile = request.user.student_profile
            
            # Use the Enrollment model directly for the M2M relationship
            Enrollment.objects.get_or_create(student=student_profile, course=course)
            
            messages.success(request, f'Purchase successful! You are now enrolled in "{course.title}".')
            return redirect('course_detail', course_slug=course.slug) 
            
        except StudentProfile.DoesNotExist:
            messages.error(request, 'Could not complete enrollment. Student profile not found.')
            return redirect('home')
        
    messages.error(request, 'Invalid purchase request.')
    return redirect('explore_courses')

# [your_app_name]/views.py
# ... (Ensure InstructorProfileEditForm is imported) ...

@login_required
def instructor_edit_profile(request):
    """Allows instructor to edit their profile and flags for re-approval if necessary."""
    try:
        profile = request.user.instructor_profile
    except InstructorProfile.DoesNotExist:
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        # NOTE: Must include request.FILES to handle the image upload
        form = InstructorProfileEditForm(
            request.POST, 
            request.FILES, 
            instance=profile, 
            user_instance=request.user
        )
        if form.is_valid():
            profile_saved = form.save()
            
            # Display custom message from the form (if re-approval was triggered)
            if hasattr(profile_saved, '_message_on_save'):
                messages.warning(request, profile_saved._message_on_save)
            else:
                messages.success(request, 'Profile successfully updated!')

            # If the profile is no longer approved, redirect them away from the dashboard
            if not profile_saved.approved:
                 return redirect('home') # or a waiting page
                 
            return redirect('instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InstructorProfileEditForm(
            instance=profile, 
            user_instance=request.user
        )

    context = {'form': form}
    # You will need to create this template: instructor_edit_profile.html
    return render(request, 'lms/instructor_edit_profile.html', context)

# =========================================================
# PLACEHOLDER/STUB VIEWS (Removed conflicting instructor_engagement stub)
# =========================================================

def instructor_manage_courses(request):
    # This might need to be consolidated with instructor_my_courses
    return render(request, 'lms/instructordash.html')

def instructor_add_quiz(request):
    return render(request, 'lms/instructordash.html')

def instructor_create_coupon(request):
    return render(request, 'lms/instructordash.html')

def instructor_request_payout(request):
    return render(request, 'lms/instructordash.html')


# The remaining course category stubs:
def course_python(request):
    return render(request, 'lms/python.html')
def course_javascript(request):
    return render(request, 'lms/javascript.html')
def course_java(request):
    return render(request, 'lms/Java.html')
def course_cpp(request):
    return render(request, 'lms/C++.html')