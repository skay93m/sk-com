#!/usr/bin/env python
"""
Sample MCQ data creation script for testing the MVP
"""
import os
import django
import sys

# Setup Django environment
sys.path.append('/workspaces/sk-com')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')
django.setup()

from mcq.models import MCQ, Choice, ReviewSchedule

def create_sample_mcqs():
    """Create sample MCQ data for testing"""
    
    # Clear existing data
    MCQ.objects.all().delete()
    
    # Sample MCQ 1 - Recall Level
    mcq1 = MCQ.objects.create(
        question_text="What is the capital of France?",
        difficulty=1,
        explanation_general="Paris has been the capital of France since 987 AD and is the country's political, economic, and cultural center."
    )
    
    Choice.objects.create(mcq=mcq1, text="London", is_correct=False, 
                         explanation="London is the capital of the United Kingdom, not France.")
    Choice.objects.create(mcq=mcq1, text="Berlin", is_correct=False,
                         explanation="Berlin is the capital of Germany.")
    Choice.objects.create(mcq=mcq1, text="Paris", is_correct=True)
    Choice.objects.create(mcq=mcq1, text="Madrid", is_correct=False,
                         explanation="Madrid is the capital of Spain.")
    
    ReviewSchedule.objects.create(mcq=mcq1)
    
    # Sample MCQ 2 - Application Level  
    mcq2 = MCQ.objects.create(
        question_text="If a Python list contains [1, 2, 3, 4, 5] and you execute list.pop(2), what will the list contain?",
        difficulty=2,
        explanation_general="The pop() method removes and returns the element at the specified index. Index 2 contains the value 3, so it gets removed."
    )
    
    Choice.objects.create(mcq=mcq2, text="[1, 2, 4, 5]", is_correct=True)
    Choice.objects.create(mcq=mcq2, text="[1, 2, 3, 4]", is_correct=False,
                         explanation="This would be the result if you used pop() without arguments or pop(-1).")
    Choice.objects.create(mcq=mcq2, text="[2, 3, 4, 5]", is_correct=False,
                         explanation="This would be the result if you used pop(0).")
    Choice.objects.create(mcq=mcq2, text="[1, 2, 3, 5]", is_correct=False,
                         explanation="This would be the result if the element at index 3 was removed.")
    
    ReviewSchedule.objects.create(mcq=mcq2)
    
    # Sample MCQ 3 - Reasoning Level
    mcq3 = MCQ.objects.create(
        question_text="A company's profit increased by 20% in Year 1, then decreased by 15% in Year 2. If the original profit was $100,000, what is the profit after Year 2?",
        difficulty=3,
        explanation_general="Year 1: $100,000 × 1.20 = $120,000. Year 2: $120,000 × 0.85 = $102,000. The net result is a 2% increase from the original."
    )
    
    Choice.objects.create(mcq=mcq3, text="$102,000", is_correct=True)
    Choice.objects.create(mcq=mcq3, text="$105,000", is_correct=False,
                         explanation="This would be the result of simply adding 20% and subtracting 15% (5% increase), but percentages don't work this way.")
    Choice.objects.create(mcq=mcq3, text="$100,000", is_correct=False,
                         explanation="This would mean no net change, but the calculations show a small increase.")
    Choice.objects.create(mcq=mcq3, text="$98,000", is_correct=False,
                         explanation="This would be the result if both percentages were applied to the original amount incorrectly.")
    
    ReviewSchedule.objects.create(mcq=mcq3)
    
    # Sample MCQ 4 - Web Development
    mcq4 = MCQ.objects.create(
        question_text="In Django, which method is used to create a new database migration file?",
        difficulty=2,
        explanation_general="The 'makemigrations' command analyzes your models and creates migration files for any changes it detects."
    )
    
    Choice.objects.create(mcq=mcq4, text="python manage.py migrate", is_correct=False,
                         explanation="This command applies migrations to the database, it doesn't create them.")
    Choice.objects.create(mcq=mcq4, text="python manage.py makemigrations", is_correct=True)
    Choice.objects.create(mcq=mcq4, text="python manage.py createmigration", is_correct=False,
                         explanation="This is not a valid Django management command.")
    Choice.objects.create(mcq=mcq4, text="python manage.py syncdb", is_correct=False,
                         explanation="This was used in older versions of Django and is now deprecated.")
    
    ReviewSchedule.objects.create(mcq=mcq4)
    
    # Sample MCQ 5 - Mathematics
    mcq5 = MCQ.objects.create(
        question_text="What is the derivative of f(x) = 3x² + 2x - 5?",
        difficulty=2,
        explanation_general="Using the power rule: d/dx[3x²] = 6x, d/dx[2x] = 2, d/dx[-5] = 0. Therefore f'(x) = 6x + 2."
    )
    
    Choice.objects.create(mcq=mcq5, text="6x + 2", is_correct=True)
    Choice.objects.create(mcq=mcq5, text="6x² + 2x", is_correct=False,
                         explanation="This would be the result if you didn't apply the power rule correctly.")
    Choice.objects.create(mcq=mcq5, text="3x + 2", is_correct=False,
                         explanation="This misses the coefficient multiplication in the power rule.")
    Choice.objects.create(mcq=mcq5, text="6x + 2x - 5", is_correct=False,
                         explanation="The derivative of a constant is 0, and 2x should become 2.")
    
    ReviewSchedule.objects.create(mcq=mcq5)
    
    print("✅ Created 5 sample MCQs successfully!")
    print(f"📊 Total MCQs in database: {MCQ.objects.count()}")
    print(f"📝 Total Choices in database: {Choice.objects.count()}")
    print(f"📅 Total Review Schedules: {ReviewSchedule.objects.count()}")

if __name__ == "__main__":
    create_sample_mcqs()
