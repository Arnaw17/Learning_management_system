from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
from .models import StudentProfile, InstructorProfile, Course, CourseModule

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
        # For student registration we must ensure the email is unused.
        # If a user already exists with this email, block registration and show a clear message.
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
            # Could happen if two requests race or validation was bypassed client-side
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
        # If a user with this email already exists, authenticate with provided password
        existing = User.objects.filter(username=email).first()
        if existing:
            # Verify password matches this user
            auth_user = authenticate(username=email, password=data['password'])
            if auth_user is None:
                raise ValidationError('A user with that email already exists. Provide the correct password to attach instructor profile.')
            # Ensure the user doesn't already have an instructor profile
            if InstructorProfile.objects.filter(user=existing).exists():
                raise ValidationError('An instructor profile for this user already exists')
            import uuid
            instructor_id = uuid.uuid4().hex[:12].upper()
            InstructorProfile.objects.create(user=existing, contact=data.get('contact', ''), expertise=data.get('expertise', ''), instructor_id=instructor_id, approved=False)
            return existing

        # New user flow
        user = User.objects.create_user(username=email, email=email, password=data['password'],
                                        first_name=data.get('name', ''))
        # Keep is_staff False until admin approves
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
# Continue from your existing forms.py content

# Import models you would need for the course forms
# NOTE: These model imports assume you have Course and Module models defined in .models
# from .models import Course, CourseModule # Uncomment this in your actual forms.py

# =========================================================
# Course Management Forms
# =========================================================

# In your forms.py, starting from line 170 (after the LoginForm class):

# =========================================================
# Course Management Forms
# =========================================================

class CourseCreationForm(forms.ModelForm):
    """
    Consolidated form for instructors to create/edit courses.
    """
    # Override fields from the model here if customization is needed
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
    
    # Custom widget for detailed_description
    detailed_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'A detailed outline, prerequisites, and learning goals.'})
    )
    
    # Custom widget for short_description (matching your initial widget definitions)
    short_description = forms.CharField(
        max_length=500, # Max length from model
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'A concise summary of the course content.'})
    )
    
    # Custom widget for outline (matching your current template)
    outline = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'Structured topics and learning milestones.'})
    )


    class Meta:
        model = Course
        # CRITICAL: This list includes ALL fields from the final model 
        # (title, short_description, detailed_description, outline, image, course_video, notes_file)
        fields = [
            'title', 
            'short_description', 
            'detailed_description', 
            'outline',      # New field
            'category', 
            'price', 
            'image',        # Corrected name
            'course_video', # New field
            'notes_file',   # New field
            'level', 
            'is_published'
        ]
        
        # Custom widgets for better user experience
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., The Ultimate Django Development Guide'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }
        
        # Hide the slug and instructor fields from the user
        exclude = ('slug', 'instructor')