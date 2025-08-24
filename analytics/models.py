"""
Simple Analytics Models for tracking HTTP requests and page views.
"""
from django.db import models
from django.utils import timezone
import uuid


class PageView(models.Model):
    """
    Track individual page views with basic analytics data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Request details
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default='GET')
    status_code = models.IntegerField(null=True, blank=True)
    
    # Client information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referer = models.URLField(max_length=500, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(default=timezone.now)
    response_time_ms = models.IntegerField(null=True, blank=True)  # Response time in milliseconds
    
    # User tracking (optional)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Geographic info (can be enhanced later)
    country = models.CharField(max_length=2, blank=True)  # ISO country code
    
    # Content info
    is_bot = models.BooleanField(default=False)
    is_mobile = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_bot']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.ip_address} - {self.timestamp}"


class DailyStats(models.Model):
    """
    Aggregated daily statistics for performance.
    """
    date = models.DateField(unique=True)
    
    # Counts
    total_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    bot_requests = models.IntegerField(default=0)
    mobile_views = models.IntegerField(default=0)
    
    # Popular content
    top_page = models.CharField(max_length=500, blank=True)
    top_page_views = models.IntegerField(default=0)
    
    # Performance
    avg_response_time = models.FloatField(null=True, blank=True)
    
    # Status codes
    status_200 = models.IntegerField(default=0)
    status_404 = models.IntegerField(default=0)
    status_500 = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}: {self.total_views} views"


class PopularPage(models.Model):
    """
    Track most popular pages over time.
    """
    path = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=200, blank=True)
    
    # Counters
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    
    # Timing
    first_viewed = models.DateTimeField(auto_now_add=True)
    last_viewed = models.DateTimeField(auto_now=True)
    
    # Performance
    avg_response_time = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-total_views']
    
    def __str__(self):
        return f"{self.path} ({self.total_views} views)"
