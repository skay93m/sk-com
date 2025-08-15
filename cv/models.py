from django.db import models

class Credentials(models.Model):
    title = models.CharField(max_length=100, primary_key=True)
    institution = models.CharField(max_length=100)
    date_obtained = models.DateField()
    icon = models.CharField(
        max_length=100,
        help_text="Filename of the icon in cv/static/icon"
    )
    link = models.URLField(
        max_length=200,
        help_text="URL of the credential's official page"
    )

    def __str__(self):
        return f"{self.title} ({self.date_obtained})"
