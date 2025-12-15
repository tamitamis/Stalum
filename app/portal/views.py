from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages 
from .models import User, Profile, Post, Job, Event, JobApplication, Comment
from .forms import StudentAlumniRegistrationForm, ProfileUpdateForm, PostForm, JobForm, EventForm, CommentForm

# --- Authentication ---

def register(request):
    """
    Handle user registration. Creates a new User and an associated Profile.
    Logs the user in immediately upon successful registration.
    """
    if request.method == 'POST':
        form = StudentAlumniRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            enrollment_year = form.cleaned_data.get('enrollment_year')
            Profile.objects.create(user=user, enrollment_year=enrollment_year)
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentAlumniRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Main Features ---

@login_required
def dashboard(request):
    """
    Display the main newsfeed, handle post creation, and suggest connections.
    Filters suggestions to exclude users already followed.
    """
    posts = Post.objects.all()
    # Handle Post Creation
    if request.method == 'POST' and 'post_submit' in request.POST:
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('dashboard')
    else:
        form = PostForm()
    
    comment_form = CommentForm()

    # SUGGESTED CONNECTIONS LOGIC
    # Exclude: Myself, Superusers, and People I already follow
    suggested_users = User.objects.exclude(id=request.user.id) \
                                  .exclude(is_superuser=True) \
                                  .exclude(id__in=request.user.following.all())[:5]
    
    return render(request, 'portal/dashboard.html', {
        'posts': posts, 
        'form': form, 
        'comment_form': comment_form,
        'suggested_users': suggested_users
    })

@login_required
def like_post(request, post_id):
    """
    Toggle the 'like' status for a specific post by the current user.
    Redirects back to the dashboard.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('dashboard')

@login_required
def follow_user(request, user_id):
    """
    Add a target user to the current user's following list.
    """
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        request.user.following.add(user_to_follow)
        messages.success(request, f"You are now following {user_to_follow.first_name}")
    return redirect('dashboard')

@login_required
def add_comment(request, post_id):
    """
    Add a comment to a post. Handles both top-level comments and replies
    if a 'parent_id' is provided in the POST data.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    # Parent comment was deleted or does not exist; ignore reply
                    parent_comment = None
            
            comment.save()
            return redirect('dashboard')
    return redirect('dashboard')

@login_required
def directory(request):
    """
    Search and filter users by name, industry, or graduation year.
    """
    query = request.GET.get('q')
    industry = request.GET.get('industry')
    year = request.GET.get('year')
    users = User.objects.all().exclude(is_superuser=True)
    
    if query:
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    if industry:
        users = users.filter(profile__industry__icontains=industry)
    if year:
        users = users.filter(Q(profile__graduation_year=year) | Q(profile__enrollment_year=year))

    return render(request, 'portal/directory.html', {'users': users})

@login_required
def profile_view(request, username):
    """
    Display a specific user's public profile.
    """
    user_obj = get_object_or_404(User, username=username)
    return render(request, 'portal/profile.html', {'profile_user': user_obj})

@login_required
def edit_profile(request):
    """
    Allow the current user to update their profile information.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'portal/edit_profile.html', {'form': form})

# --- Jobs Module ---

@login_required
def job_portal(request):
    """
    List all active jobs and identify which ones the current user has
    already applied to.
    """
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    applied_job_ids = JobApplication.objects.filter(applicant=request.user).values_list('job_id', flat=True)
    return render(request, 'portal/jobs.html', {'jobs': jobs, 'applied_job_ids': applied_job_ids})

@login_required
def post_job(request):
    """
    Allow Alumni (and admins) to post new job opportunities.
    Restricts access for standard Student users.
    """
    if not request.user.is_alumni and not request.user.is_superuser:
        messages.error(request, "Only Alumni are allowed to post new job opportunities.")
        return redirect('jobs')

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs')
    else:
        form = JobForm()
    return render(request, 'portal/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    """
    Record a user's application to a specific job.
    Prevents duplicate applications.
    """
    job = get_object_or_404(Job, id=job_id)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('jobs')

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES) # request.FILES is crucial for uploads
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, f"Application submitted for {job.title}!")
            return redirect('jobs')
    else:
        form = JobApplicationForm()

    return render(request, 'portal/apply_job.html', {'form': form, 'job': job})

@login_required
def view_applicants(request, job_id):
    """
    Allow the job poster to view applicants for a specific job.
    """
    job = get_object_or_404(Job, id=job_id)
    
    # Permission check: Only the poster or superuser can view applicants
    if request.user != job.posted_by and not request.user.is_superuser:
        messages.error(request, "You do not have permission to view applicants for this job.")
        return redirect('jobs')
    
    applicants = JobApplication.objects.filter(job=job).select_related('applicant', 'applicant__profile')
    
    return render(request, 'portal/view_applicants.html', {'job': job, 'applicants': applicants})

# --- Events Module ---

@login_required
def event_list(request):
    """
    List all upcoming events ordered by date.
    """
    events = Event.objects.all().order_by('date_time')
    return render(request, 'portal/events.html', {'events': events})

@login_required
def add_event(request):

    """
    Allow Alumni (and admins) to create new events.
    Restricts access for standard Student users.
    """
    # Allow Alumni and Admin to create events
    if not request.user.is_alumni and not request.user.is_superuser:
        messages.error(request, "Only Alumni can organize events.")
        return redirect('events')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('events')
    else:
        form = EventForm()
    return render(request, 'portal/add_event.html', {'form': form})


@login_required
def rsvp_event(request, event_id):
    """
    NEW: Toggle attendance for an event.
    """
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
        messages.info(request, "You are no longer attending.")
    else:
        event.attendees.add(request.user)
        messages.success(request, "RSVP Confirmed!")
    return redirect('events')


@login_required
def delete_post(request, post_id):
    """Allow authors to delete their own posts."""
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author or request.user.is_superuser:
        post.delete()
        messages.success(request, "Post deleted.")
    return redirect('dashboard')