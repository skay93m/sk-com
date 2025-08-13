from django.db import models

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('now', 'Current'),
        ('backburner', 'Backburner'),
        ('someday', 'Someday'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='someday')
    description = models.TextField(blank=False, help_text='Explain what you intend to accomplish with the project.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
