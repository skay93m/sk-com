from django.db import models
from django.utils import timezone
from datetime import timedelta

class Topic(models.Model):
    """Topics/tags for organizing MCQs"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code for the topic badge')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_mcq_count(self):
        return self.mcqs.count()

class MCQ(models.Model):
    DIFFICULTY_CHOICES = [
        (1, "Recall"),
        (2, "Application"),
        (3, "Reasoning"),
    ]
    question_text = models.TextField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    explanation_general = models.TextField(blank=True)
    topics = models.ManyToManyField(Topic, blank=True, related_name='mcqs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    # WaniKani-style SRS stages
    SRS_STAGES = [
        (0, "New"),
        (1, "Apprentice I"),
        (2, "Apprentice II"), 
        (3, "Apprentice III"),
        (4, "Apprentice IV"),
        (5, "Guru I"),
        (6, "Guru II"),
        (7, "Master"),
        (8, "Enlightened"),
        (9, "Burned"),
    ]
    
    # WaniKani intervals (in hours)
    SRS_INTERVALS = {
        0: 0,      # New - immediate
        1: 4,      # Apprentice I - 4 hours
        2: 8,      # Apprentice II - 8 hours
        3: 24,     # Apprentice III - 1 day
        4: 48,     # Apprentice IV - 2 days
        5: 168,    # Guru I - 1 week
        6: 336,    # Guru II - 2 weeks
        7: 720,    # Master - 1 month (30 days)
        8: 2880,   # Enlightened - 4 months (120 days)
        9: None,   # Burned - never review
    }
    
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE, related_name="schedule")
    next_review = models.DateTimeField(default=timezone.now)
    srs_stage = models.IntegerField(choices=SRS_STAGES, default=0)
    consecutive_correct = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Keep these for backwards compatibility and additional data
    interval_days = models.IntegerField(default=1)  # Deprecated but kept
    ease_factor = models.FloatField(default=2.5)    # Deprecated but kept
    
    def schedule_again(self, correct: bool):
        """WaniKani-style SRS scheduling"""
        self.total_reviews += 1
        
        if correct:
            self.consecutive_correct += 1
            
            # Advance to next SRS stage
            if self.srs_stage < 9:  # Don't advance beyond Burned
                self.srs_stage += 1
                
            # Set next review time based on SRS stage
            if self.srs_stage == 9:  # Burned
                # Never review again - set far future date
                self.next_review = timezone.now() + timedelta(days=365 * 10)
            else:
                hours = self.SRS_INTERVALS[self.srs_stage]
                self.next_review = timezone.now() + timedelta(hours=hours)
                
        else:
            # Incorrect answer - reset to Apprentice I but keep some progress
            self.consecutive_correct = 0
            
            if self.srs_stage >= 5:  # Guru I or higher
                # Drop back to Apprentice II (keep some progress)
                self.srs_stage = 2
            elif self.srs_stage >= 2:  # Apprentice II or higher  
                # Drop back to Apprentice I
                self.srs_stage = 1
            else:
                # Already at low stage, stay at Apprentice I
                self.srs_stage = 1
                
            # Schedule for immediate re-review (4 hours for Apprentice I)
            hours = self.SRS_INTERVALS[self.srs_stage]
            self.next_review = timezone.now() + timedelta(hours=hours)
        
        # Update deprecated fields for backwards compatibility
        if self.srs_stage <= 4:
            self.interval_days = max(1, self.SRS_INTERVALS[self.srs_stage] // 24)
        else:
            self.interval_days = self.SRS_INTERVALS[self.srs_stage] // 24
            
        self.save()
    
    def get_srs_stage_display_with_color(self):
        """Get SRS stage with appropriate color class"""
        stage_colors = {
            0: 'secondary',     # New
            1: 'danger',        # Apprentice I
            2: 'danger',        # Apprentice II  
            3: 'warning',       # Apprentice III
            4: 'warning',       # Apprentice IV
            5: 'info',          # Guru I
            6: 'info',          # Guru II
            7: 'primary',       # Master
            8: 'success',       # Enlightened
            9: 'dark',          # Burned
        }
        return {
            'stage': self.get_srs_stage_display(),
            'color': stage_colors.get(self.srs_stage, 'secondary')
        }
    
    def __str__(self):
        return f"{self.mcq.question_text[:30]}... - {self.get_srs_stage_display()}"

class QuestionGeneration(models.Model):
    """Track LLM question generation sessions"""
    GENERATION_STATUS = [
        ('pending', 'Pending Review'),
        ('reviewing', 'Under Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    prompt_text = models.TextField(help_text="The prompt sent to the LLM")
    llm_response = models.TextField(help_text="Raw response from the LLM")
    status = models.CharField(max_length=20, choices=GENERATION_STATUS, default='pending')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.IntegerField(choices=MCQ.DIFFICULTY_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Generation {self.id} - {self.get_status_display()}"

class GeneratedQuestion(models.Model):
    """Individual questions generated by LLM, pending review"""
    REVIEW_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('needs_edit', 'Needs Editing'),
    ]
    
    generation_session = models.ForeignKey(QuestionGeneration, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    difficulty = models.IntegerField(choices=MCQ.DIFFICULTY_CHOICES)
    explanation_general = models.TextField(blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    
    # Review fields
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='pending')
    reviewer_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Link to final MCQ if approved
    final_mcq = models.OneToOneField(MCQ, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.question_text[:50]}... - {self.get_status_display()}"

class GeneratedChoice(models.Model):
    """Choices for generated questions"""
    generated_question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=400)
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.text[:60]} ({'✅' if self.is_correct else '❌'})"