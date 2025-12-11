from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Post, Job, Event, Comment, JobApplication
from django.core.exceptions import ValidationError
import datetime

# Registration Form
class StudentAlumniRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Add a valid email address.")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_student = forms.BooleanField(required=False, label="I am a Student")
    is_alumni = forms.BooleanField(required=False, label="I am an Alumni")
    enrollment_year = forms.IntegerField(required=True, min_value=1950, max_value=datetime.date.today().year + 1, help_text="Enter your enrollment year (YYYY)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'is_student', 'is_alumni')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_enrollment_year(self):
        year = self.cleaned_data.get('enrollment_year')
        current_year = datetime.date.today().year
        if year < 1950 or year > current_year + 1:
            raise ValidationError("Please enter a valid enrollment year.")
        return year

# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'enrollment_year', 'graduation_year', 'industry', 'major', 'current_company', 'linkedin_url']

# Post Creation Form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share an update, news, or achievement...'}),
        }

# Comment Form (New)
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 1, 'placeholder': 'Write a comment...', 'class': 'form-control'}),
        }

# Job Posting Form
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company_name', 'location', 'job_type', 'description', 'requirements']

# Event Creation Form
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Why are you a good fit?'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }