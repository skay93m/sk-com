from django.shortcuts import get_object_or_404, render, redirect
from .models import Credentials
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CredentialForm
from .utils import get_available_icons

def cv_main(request):
    context = {
        "credentials": Credentials.objects.all()
    }

    return render(request, 'cv_main.html', context)

def credential_list(request):
    '''Display list of all credentials'''
    credentials = Credentials.objects.all()
    return render(request, 'credential_list.html', context={'credentials': credentials})

@login_required
def credential_detail(request, pk):
    '''Display a single credential'''
    credential = get_object_or_404(Credentials, pk=pk)
    context = {
        'credential': credential,
    }
    return render(request, 'credential_detail.html', context)

@login_required
def credential_create(request):
    '''Create a new credential'''
    if request.method == 'POST':
        form = CredentialForm(request.POST, request.FILES)  # Added request.FILES for file upload
        if form.is_valid():
            try:
                credential = form.save(commit=False)
                credential.save()
                messages.success(request, f'Credential "{credential.title}" created successfully!')
                return redirect('cv:credential_detail', pk=credential.pk)
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error saving credential: {str(e)}')
                
                messages.error(request, f'An error occurred while saving the credential: {str(e)}')
        else:
            # Add form errors to messages
            if form.errors:
                error_messages = []
                for field, errors in form.errors.items():
                    if field == '__all__':
                        error_messages.extend(errors)
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title()
                        for error in errors:
                            error_messages.append(f'{field_name}: {error}')
                
                if error_messages:
                    messages.error(request, 'Please correct the following errors: ' + '; '.join(error_messages))
    else:
        form = CredentialForm()
    
    context = {
        'form': form,
        'title': 'Create New Credential',
        'available_icons': get_available_icons(),
    }
    return render(request, 'credential_form.html', context)

@login_required
def credential_edit(request, pk):
    credential = get_object_or_404(Credentials, pk=pk)
    
    # only allow staff to edit credentials
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit credentials.')
        return redirect('cv:cv_main')
    
    if request.method == 'POST':
        form = CredentialForm(request.POST, request.FILES, instance=credential)  # Added request.FILES for file upload
        if form.is_valid():
            try:
                credential = form.save(commit=False)
                credential.save()
                messages.success(request, f'Credential "{credential.title}" updated successfully!')
                return redirect('cv:credential_detail', pk=credential.pk)
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error updating credential: {str(e)}')
                
                messages.error(request, f'An error occurred while updating the credential: {str(e)}')
        else:
            # Add form errors to messages
            if form.errors:
                error_messages = []
                for field, errors in form.errors.items():
                    if field == '__all__':
                        error_messages.extend(errors)
                    else:
                        field_name = form.fields[field].label or field.replace('_', ' ').title()
                        for error in errors:
                            error_messages.append(f'{field_name}: {error}')
                
                if error_messages:
                    messages.error(request, 'Please correct the following errors: ' + '; '.join(error_messages))
    else:
        form = CredentialForm(instance=credential)
        
    context = {
        'form': form,
        'credential': credential,
        'title': f'Edit: {credential.title}',
        'available_icons': get_available_icons(),
    }
    return render(request, 'credential_form.html', context)

@login_required
def credential_delete(request, pk):
    '''Delete a credential'''
    credential = get_object_or_404(Credentials, pk=pk)
    
    # only allow staff to delete credentials
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete credentials.')
        return redirect('cv:credential_detail', pk=pk)
    
    if request.method == 'POST':
        title = credential.title
        credential.delete()
        messages.success(request, f'Credential "{title}" deleted successfully!')
        return redirect('cv:cv_main')
    
    context = {
        'credential': credential,
    }
    return render(request, 'credential_delete.html', context)
