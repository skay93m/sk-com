from django.shortcuts import render
from .models import Credentials

def cv_main(request):
    context = {
        "credentials": Credentials.objects.all()
    }

    return render(request, 'cv_main.html', context)