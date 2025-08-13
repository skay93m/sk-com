from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Writing(models.Model):
    """Model for writing pieces such as articles, blog posts, stories, etc."""
    
    WRITING_TYPES = [
        ('article', 'Article'),
        ('blog', 'Blog Post'),
        ('story', 'Story'),
        ('poem', 'Poem'),
        ('essay', 'Essay'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writings')
    writing_type = models.CharField(max_length=20, choices=WRITING_TYPES, default='article')
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short description or preview")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Writing'
        verbose_name_plural = 'Writings'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('writing:writing_detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
