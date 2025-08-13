from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Writing

class WritingModelTest(TestCase):
    """Test cases for the Writing model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_writing_creation(self):
        """Test creating a writing instance"""
        writing = Writing.objects.create(
            title='Test Writing',
            slug='test-writing',
            author=self.user,
            writing_type='article',
            content='This is test content',
            status='published'
        )
        
        self.assertEqual(writing.title, 'Test Writing')
        self.assertEqual(writing.slug, 'test-writing')
        self.assertEqual(writing.author, self.user)
        self.assertEqual(writing.writing_type, 'article')
        self.assertEqual(writing.status, 'published')
        self.assertEqual(str(writing), 'Test Writing')
    
    def test_get_absolute_url(self):
        """Test the get_absolute_url method"""
        writing = Writing.objects.create(
            title='Test Writing',
            slug='test-writing',
            author=self.user,
            content='Test content'
        )
        
        expected_url = reverse('writing:writing_detail', kwargs={'pk': writing.pk})
        self.assertEqual(writing.get_absolute_url(), expected_url)
    
    def test_get_tags_list(self):
        """Test the get_tags_list method"""
        writing = Writing.objects.create(
            title='Test Writing',
            slug='test-writing',
            author=self.user,
            content='Test content',
            tags='python, django, web development'
        )
        
        expected_tags = ['python', 'django', 'web development']
        self.assertEqual(writing.get_tags_list(), expected_tags)
        
        # Test empty tags
        writing.tags = ''
        self.assertEqual(writing.get_tags_list(), [])

class WritingViewTest(TestCase):
    """Test cases for Writing views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.writing = Writing.objects.create(
            title='Published Writing',
            slug='published-writing',
            author=self.user,
            content='This is published content',
            status='published',
            published_at=timezone.now()
        )
        
        self.draft_writing = Writing.objects.create(
            title='Draft Writing',
            slug='draft-writing',
            author=self.user,
            content='This is draft content',
            status='draft'
        )
    
    def test_writing_list_view(self):
        """Test the writing list view"""
        response = self.client.get(reverse('writing:writing_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Writing')
        self.assertNotContains(response, 'Draft Writing')  # Drafts shouldn't appear for anonymous users
    
    def test_writing_detail_view_published(self):
        """Test the writing detail view for published content"""
        response = self.client.get(reverse('writing:writing_detail', kwargs={'pk': self.writing.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Writing')
        self.assertContains(response, 'This is published content')
    
    def test_writing_detail_view_draft_anonymous(self):
        """Test that anonymous users can't see draft content"""
        response = self.client.get(reverse('writing:writing_detail', kwargs={'pk': self.draft_writing.pk}), follow=True)
        # Should end up at writing list after redirect
        final_url = response.request['PATH_INFO']
        self.assertTrue(final_url.startswith('/writing/'))
        self.assertEqual(response.status_code, 200)
    
    def test_writing_create_view_anonymous(self):
        """Test that anonymous users can't access create view"""
        response = self.client.get(reverse('writing:writing_create'), follow=True)
        # Should redirect to login - check for login redirect
        self.assertIn('login', response.redirect_chain[-1][0])
    
    def test_writing_create_view_authenticated(self):
        """Test that authenticated users can access create view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('writing:writing_create'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Writing')
    
    def test_writing_search(self):
        """Test the search functionality"""
        response = self.client.get(reverse('writing:writing_list') + '?search=published', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Writing')
    
    def test_writing_filter_by_type(self):
        """Test filtering by writing type"""
        # Create a blog post
        blog_writing = Writing.objects.create(
            title='Blog Post',
            slug='blog-post',
            author=self.user,
            content='Blog content',
            writing_type='blog',
            status='published',
            published_at=timezone.now()
        )
        
        response = self.client.get(reverse('writing:writing_list') + '?type=blog', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Blog Post')
        self.assertNotContains(response, 'Published Writing')  # This is an article, not blog
