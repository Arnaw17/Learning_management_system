from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
# Keep your essential model imports consolidated here:
from .models import StudentProfile, InstructorProfile, Course, CourseModule, Enrollment

User = get_user_model()


class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    contact = forms.CharField(max_length=20, required=False)
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        existing = User.objects.filter(username=email).first()
        if existing:
            raise ValidationError('A user with that email already exists. Try logging in instead.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match')
        return cleaned

    def save(self):
        data = self.cleaned_data
        email = data['email'].lower()
        try:
            user = User.objects.create_user(username=email, email=email, password=data['password'],
                                             first_name=data.get('first_name', ''), last_name=data.get('last_name', ''))
        except IntegrityError:
            raise ValidationError('A user with that email already exists')
        StudentProfile.objects.create(user=user, contact=data.get('contact', ''), dob=data.get('dob', None))
        return user


class InstructorRegistrationForm(forms.Form):
    name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm password')
    contact = forms.CharField(max_length=20, required=False)
    expertise = forms.CharField(max_length=200, required=False)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(username=email).exists():
            raise ValidationError('A user with that email already exists')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match')
        return cleaned

    def save(self):
        data = self.cleaned_data
        email = data['email'].lower()
        existing = User.objects.filter(username=email).first()
        if existing:
            auth_user = authenticate(username=email, password=data['password'])
            if auth_user is None:
                raise ValidationError('A user with that email already exists. Provide the correct password to attach instructor profile.')
            if InstructorProfile.objects.filter(user=existing).exists():
                raise ValidationError('An instructor profile for this user already exists')
            import uuid
            instructor_id = uuid.uuid4().hex[:12].upper()
            InstructorProfile.objects.create(user=existing, contact=data.get('contact', ''), expertise=data.get('expertise', ''), instructor_id=instructor_id, approved=False)
            return existing

        user = User.objects.create_user(username=email, email=email, password=data['password'],
                                         first_name=data.get('name', ''))
        user.is_staff = False
        user.save()
        import uuid
        instructor_id = uuid.uuid4().hex[:12].upper()
        InstructorProfile.objects.create(user=user, contact=data.get('contact', ''), expertise=data.get('expertise', ''), instructor_id=instructor_id, approved=False)
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    remember_me = forms.BooleanField(required=False, initial=False)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError('Invalid email or password')
            cleaned['user'] = user
        return cleaned

# =========================================================
# Course Management Forms
# =========================================================

class CourseCreationForm(forms.ModelForm):
    """
    Consolidated form for instructors to create/edit courses.
    """
    category = forms.ChoiceField(
        choices=[
            ('', 'Select Category'),
            ('WEB', 'Web Development'),
            ('DATA', 'Data Science & Analytics'),
            ('DES', 'Design'),
            ('BUS', 'Business'),
            ('OTH', 'Other'),
        ],
        required=True
    )
    
    detailed_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'A detailed outline, prerequisites, and learning goals.'})
    )
    
    short_description = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'A concise summary of the course content.'})
    )
    
    outline = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'Structured topics and learning milestones.'})
    )


    class Meta:
        model = Course
        fields = [
            'title', 
            'short_description', 
            'detailed_description', 
            'outline', 
            'category', 
            'price', 
            'image', 
            'course_video', 
            'notes_file', 
            'level', 
            'is_published'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., The Ultimate Django Development Guide'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }
        
        exclude = ('slug', 'instructor')

class EnrollmentForm(forms.ModelForm):
    """
    Form to handle the creation of a Student-Course Enrollment record.
    Used internally in views, so all fields are hidden or excluded.
    """
    class Meta:
        model = Enrollment
        # Exclude all fields, as they are set programmatically in the view
        # (student = request.user.student_profile and course = retrieved_course).
        fields = []
class InstructorProfileEditForm(forms.ModelForm):
    """Form for instructors to edit ALL profile details, including image upload."""
    
    # User fields (first_name, last_name) will be updated on the related User model
    first_name = forms.CharField(max_length=150, required=True, label='First Name')
    last_name = forms.CharField(max_length=150, required=False, label='Last Name')

    class Meta:
        model = InstructorProfile
        # Include all editable fields from InstructorProfile + the User fields declared above
        fields = ['first_name', 'last_name', 'contact', 'expertise', 'profile_image']
        
    def __init__(self, *args, **kwargs):
        # Retrieve user instance passed in context, if it exists
        user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        # Initialize form fields with current User data
        if user_instance:
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        
        # Determine if re-approval is needed based on changes to critical fields.
        re_approval_needed = False
        
        # Get original profile data from the database for comparison
        original_profile = InstructorProfile.objects.get(pk=profile.pk)
        
        # Check for changes in fields that require re-approval:
        if (user.first_name != self.cleaned_data['first_name'] or 
            user.last_name != self.cleaned_data['last_name'] or 
            original_profile.contact != self.cleaned_data['contact'] or
            original_profile.expertise != self.cleaned_data['expertise'] or
            self.cleaned_data['profile_image'] != original_profile.profile_image):
            
            re_approval_needed = True
            
        # Update User model fields (name)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Apply re-approval logic
            if re_approval_needed and profile.approved:
                profile.approved = False
                # Add a message to display in the view
                profile._message_on_save = "Your profile has been updated. Since core details were changed, your account will require admin re-approval to publish or modify courses."
            
            profile.save()
            
        return profile