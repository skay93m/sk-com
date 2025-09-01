from django.db import models

class Hero(models.Model):
    header = models.CharField(max_length=255)
    tagline = models.TextField()
    cta = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.header

    class Meta:
        ordering = ['-updated_at']


class Expertise(models.Model):
    title = models.CharField(max_length=255, help_text="e.g., Healthcare & Pharmacy")
    description = models.TextField(help_text="Brief description of expertise area")
    icon = models.CharField(max_length=10, help_text="Emoji or Unicode character (e.g., 🏥)")
    order = models.PositiveIntegerField(default=0, help_text="Order for display (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Show on homepage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']
        verbose_name_plural = "Expertise Areas"
