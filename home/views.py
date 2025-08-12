from django.shortcuts import render
from datetime import datetime

def home(request):
    context = {
        'title': 'Home',
        'header': 'Welcome!',
        'statement1': 'Pharmacist → Aspiring Barrister | Tech Enthusiast | Lifelong Learner', # who am I
        'statement2': (
            "Welcome to my website (coming soon)"
        ), # what I do
        'cta_button': 'Explore (coming soon)', # call to action
        'portfolio1': '',
        'portfolio2': '',
        'portfolio3': '',
        'portfolio4': '',
        'portfolio5': '',
        'portfolio6': '',
        'portfolio7': '',
        'portfolio8': '',
        'project1': '',
        'project1_description': '',
        'project2': '',
        'project2_description': '',
        'project3': '',
        'project3_description': '',
        'project4': '',
        'project4_description': '',
    }
    return render(request, 'index.html', context)