from django.shortcuts import render, redirect
from home.forms import HeroForm
from home.models import Hero

def home(request):
    context = {
        'title': 'Home',
        'header': Hero.objects.first().header if Hero.objects.exists() else 'Syafiq Kay',
        'tagline': Hero.objects.first().tagline if Hero.objects.exists() else 'Pharmacist → Aspiring Barrister | Tech Enthusiast | Lifelong Learner',
        'cta_button': Hero.objects.first().cta if Hero.objects.exists() else '(coming soon)',
    }
    return render(request, 'index.html', context)

def hero(request):
    return render(request, 'hero.html', {'hero': Hero.objects.first()})

def hero_form(request):
    if request.method == 'POST':
        form = HeroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = HeroForm()
    return render(request, 'hero_form.html', {'form': form})

