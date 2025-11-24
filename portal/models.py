from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 1. Login/Registration & User Profile Management
class User(AbstractUser):
    """
    Custom User model to distinguish between Students, Alumni, and Admins.
    Includes a many-to-many relationship for the follow system.
    """
    is_student = models.BooleanField(default=False)
    is_alumni = models.BooleanField(default=False)
    # New: Follow system
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

class Profile(models.Model):
    """
    Stores detailed information about a user, such as bio, location,
    education details, and professional info.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    enrollment_year = models.IntegerField(null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True, help_text="E.g., Tech, Finance, Healthcare")
    major = models.CharField(max_length=100, blank=True)
    current_company = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# 2. Newsfeed/Posts
class Post(models.Model):
    """
    Represents a user-generated update or news item in the feed.
    Supports likes from other users.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # New: Likes system
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

# Comment Model
class Comment(models.Model):
    """
    Represents a comment on a post. Supports threading via a self-referential
    'parent' field to allow replies to other comments.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

# 3. Events and Reunions
class Event(models.Model):
    """
    Represents an event or reunion organized by alumni or admins.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attendees = models.ManyToManyField(User, related_name='events_attending', blank=True)

    def __str__(self):
        return self.title

# 4. Job Portal
class Job(models.Model):
    """
    Represents a job opportunity posted by an alumni.
    Includes details like job type, company, and requirements.
    """
    JOB_TYPES = (
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('IN', 'Internship'),
        ('FR', 'Freelance'),
    )

    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    job_type = models.CharField(max_length=2, choices=JOB_TYPES, default='FT')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

class JobApplication(models.Model):
    """
    Tracks which users have applied to which jobs.
    Prevents duplicate applications for the same job.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    

    class Meta:
        # ENSURES database rejects duplicates even if code fails
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"