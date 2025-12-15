from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, Job

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_user_creation(self):
        """Test that a user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('password'))

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)

    def test_dashboard_view(self):
        """Test that the dashboard loads for logged in users"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_jobs_view(self):
        """Test that the jobs page loads"""
        response = self.client.get(reverse('jobs'))
        self.assertEqual(response.status_code, 200)

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(author=self.user, content="Test Post")

    def test_post_creation(self):
        """Test post content"""
        self.assertEqual(self.post.content, "Test Post")
        self.assertEqual(self.post.author.username, "testuser")

    def test_view_applicants(self):
        """Test that the job poster can view applicants"""
        # Create a job
        job = Job.objects.create(
            title="Test Job",
            company_name="Test Co",
            description="Desc",
            requirements="Reqs",
            posted_by=self.user
        )
        
        # Access applicants page
        self.client.force_login(self.user)
        response = self.client.get(reverse('view_applicants', args=[job.id]))
        self.assertEqual(response.status_code, 200)