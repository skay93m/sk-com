from django.shortcuts import render
from datetime import datetime

def home(request):
    return render(request, 'index.html', {
        'title': 'Home',
        'header': 'Welcome!',
        'image': 'img/img001.jpg',
        'statement1': 'Hi I am Syafiq and welcome to my personal website.', # who am I
        'statement2': 'I wrote this website using Django and Bootstrap using Visual Studio Code.', # what I do
        'statement3': 'I want to use this website as a platform for exploring my curiousity, sharing my works and connecting with others.', # why I do it
        'cta_button': 'Explore my projects' # call to action
    })