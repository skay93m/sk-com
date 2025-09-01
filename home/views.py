from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from home.forms import HeroForm
from home.models import Hero
from cv.models import Credentials
from projects.models import Project
from writing.models import Writing
from mcq.models import MCQ

def home(request):
    # Get stats for the homepage
    hero = Hero.objects.first()
    total_credentials = Credentials.objects.count()
    total_projects = Project.objects.count()
    current_projects = Project.objects.filter(category='now').count()
    total_writings = Writing.objects.filter(status='published').count()
    featured_writings = Writing.objects.filter(featured=True, status='published').count()
    total_mcqs = MCQ.objects.count()
    
    # Get recent posts for Alex Hyett style
    recent_posts = Writing.objects.filter(status='published').order_by('-created_at')[:10]
    
    # Project breakdown by category
    project_stats = Project.objects.values('category').annotate(count=Count('category'))
    project_breakdown = {stat['category']: stat['count'] for stat in project_stats}
    
    # Writing breakdown by type
    writing_stats = Writing.objects.filter(status='published').values('writing_type').annotate(count=Count('writing_type'))
    writing_breakdown = {stat['writing_type']: stat['count'] for stat in writing_stats}
    
    context = {
        'title': 'Home',
        'header': hero.header if hero else 'Welcome',
        'tagline': hero.tagline if hero else 'Personal Portfolio & Blog',
        'recent_posts': recent_posts,
        'stats': {
            'credentials': total_credentials,
            'projects': total_projects,
            'current_projects': current_projects,
            'writings': total_writings,
            'featured_writings': featured_writings,
            'mcqs': total_mcqs,
        },
        'project_breakdown': project_breakdown,
        'writing_breakdown': writing_breakdown,
    }
    return render(request, 'index.html', context)

def hero(request):
    return render(request, 'hero.html', {'hero': Hero.objects.first()})

@login_required
def hero_list(request):
    heroes = Hero.objects.all()
    context = {
        'title': 'Hero Sections',
        'heroes': heroes,
    }
    return render(request, 'hero_list.html', context)

@login_required
def hero_form(request):
    if request.method == 'POST':
        form = HeroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero section created successfully!')
            return redirect('hero_list')
    else:
        form = HeroForm()
    context = {
        'title': 'Create Hero Section',
        'form': form,
    }
    return render(request, 'hero_form.html', context)

@login_required
def hero_delete(request, hero_id):
    hero = get_object_or_404(Hero, id=hero_id)
    if request.method == 'POST':
        hero_title = hero.header
        hero.delete()
        messages.success(request, f'Hero section "{hero_title}" deleted successfully!')
        return redirect('hero_list')
    return redirect('hero_list')

