from django.shortcuts import get_object_or_404, render, redirect
from .models import Credentials
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CredentialForm

def cv_main(request):
    context = {
        "credentials": Credentials.objects.all()
    }

    return render(request, 'cv_main.html', context)

def credential_list(request):
    '''Display list of all credentials'''
    credentials = Credentials.objects.all
    return render(request, 'credential_detail.html', context={credentials,})

@login_required
def credential_create(request):
    '''Create a new credential'''
    if request.method == 'POST':
        form = CredentialForm(request.POST)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.save()
            messages.success(request, f'Credential "{credential.title}" created successfully!')
            return redirect('cv:credential_detail', pk=credential.pk)
    else:
        form = CredentialForm()
    
    context = {
        'form': form,
        'title': 'Create New Credential',
    }
    return render(request, 'credential_form.html', context)

@login_required
def credential_edit(request, pk):
    credential = get_object_or_404(Credentials, pk=pk)
    
    # only allow staff to edit
    if credential.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this writing.')
        return redirect('cv:cv_main')
    
    if request.method == 'POST':
        form = CredentialForm(request.POST, instance=credential)
        if form.is_valid():
            credential = form.save(commit=False)
            credential.save()
            messages.success(request, f'Credential "{credential.title}" updated successfully!')
            return redirect('cv:credential_detail', pk=credential.pk)
    else:
        form = CredentialForm(instance=credential)
        
    context = {
        'form': form,
        'credential': credential,
        'title': f'Edit: {credential.title}',
    }
    return render(request, 'credential_form.html', context)

@login_required
def credential_delete(request, pk):
    '''Delete a credential'''
    credential = get_object_or_404(Credentials, pk=pk)
    
    # only allow author or staff to delete
    if credential.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete credentials.')
        return redirect('cv:credential_detail', pk=pk)
    
    if request.method == 'POST':
        title = credential.title
        credential.delete()
        messages.success(request, f'Writing "{title}" deleted successfully!')
        return redirect('cv:cv_main')
    
    context = {
        'credential': credential,
    }
    return render(request, 'credential_delete.html', context)