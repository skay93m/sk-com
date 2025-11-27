from django.db import models

class WorkingIdentity(models.Model):
    IDENTITY_CHOICES = [
        ('pharmacy', 'Pharmacy'),
        ('law', 'Law'),
        ('cybersecurity', 'Cybersecurity'),
        ('actuary', 'Actuary'),
    ]
    
    identity = models.CharField(max_length=50, choices=IDENTITY_CHOICES, unique=True)
    description = models.CharField(max_length=200, help_text="e.g., 'Foundation identity', 'Study phase'")
    experiment_plan = models.TextField(help_text="Aim, hypothesis, methods of this working identity test")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Working Identities"
        ordering = ['identity']
    
    def __str__(self):
        return self.get_identity_display()
    
    def latest_entry(self):
        """Fetch most recent feed entry for this identity"""
        return self.feed_entries.latest('date') if self.feed_entries.exists() else None


class IdentityFeed(models.Model):
    working_identity = models.ForeignKey(WorkingIdentity, on_delete=models.CASCADE, related_name='feed_entries')
    date = models.DateTimeField(auto_now_add=True)
    status = models.TextField()
    next_action = models.TextField()
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Identity Feed Entries"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.working_identity.get_identity_display()} - {self.date.strftime('%Y-%m-%d')}"