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
