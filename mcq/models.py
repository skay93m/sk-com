from django.db import models
from django.utils import timezone
from datetime import timedelta

class MCQ(models.Model):
    DIFFICULTY_CHOICES = [
        (1, "Recall"),
        (2, "Application"),
        (3, "Reasoning"),
    ]
    question_text = models.TextField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    explanation_general = models.TextField(blank=True)
    
    def __str__(self):
        return self.question_text[:80]
    
class Choice(models.Model):
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=400)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.text[:60]} ({'✅' if self.is_correct else '❌'})"

class ReviewSchedule(models.Model):
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE, related_name="schedule")
    next_review = models.DateTimeField(default=timezone.now)
    interval_days = models.IntegerField(default=1)
    ease_factor = models.FloatField(default=2.5)
    
    def schedule_again(self, correct: bool):
        # Simple SM-2-lite
        if correct:
            self.ease_factor = max(1.3, self.ease_factor + 0.1)
            self.interval_days = 1 if self.interval_days == 1 else int(self.interval_days * self.ease_factor)
            if self.interval_days == 1:
                self.interval_days = 3 # first successful review jump
        else:
            self.ease_factor = max(1.2, self.ease_factor - 0.2)
            self.interval_days = 1
        self.next_review = timezone.now() + timedelta(days=self.interval_days)
        self.save()