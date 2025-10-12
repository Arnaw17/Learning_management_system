from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from .models import StudentProfile, InstructorProfile

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
        user = User.objects.create_user(username=email, email=email, password=data['password'],
                                        first_name=data.get('first_name', ''), last_name=data.get('last_name', ''))
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
        user = User.objects.create_user(username=email, email=email, password=data['password'],
                                        first_name=data.get('name', ''))
        user.is_staff = True
        user.save()
        InstructorProfile.objects.create(user=user, contact=data.get('contact', ''), expertise=data.get('expertise', ''))
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

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
