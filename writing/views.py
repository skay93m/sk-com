from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Writing
from .forms import WritingForm

def writing_list(request):
    """Display list of all published writings"""
    writings = Writing.objects.filter(status='published').order_by('-published_at', '-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        writings = writings.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by writing type
    writing_type = request.GET.get('type')
    if writing_type:
        writings = writings.filter(writing_type=writing_type)
    
    # Pagination
    paginator = Paginator(writings, 10)  # Show 10 writings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get writing types for filter dropdown
    writing_types = Writing.WRITING_TYPES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'writing_types': writing_types,
        'selected_type': writing_type,
    }
    return render(request, 'writing/writing_list.html', context)

def writing_detail(request, pk):
    """Display a single writing piece"""
    writing = get_object_or_404(Writing, pk=pk)
    
    # Only show published writings to non-staff users
    if writing.status != 'published' and not request.user.is_staff:
        return redirect('writing:writing_list')
    
    context = {
        'writing': writing,
    }
    return render(request, 'writing/writing_detail.html', context)

@login_required
def writing_create(request):
    """Create a new writing piece"""
    if request.method == 'POST':
        form = WritingForm(request.POST)
        if form.is_valid():
            writing = form.save(commit=False)
            writing.author = request.user
            
            # Auto-generate slug if not provided
            if not writing.slug:
                writing.slug = slugify(writing.title)
            
            # Set published_at if status is published
            if writing.status == 'published' and not writing.published_at:
                writing.published_at = timezone.now()
            
            writing.save()
            messages.success(request, f'Writing "{writing.title}" created successfully!')
            return redirect('writing:writing_detail', pk=writing.pk)
    else:
        form = WritingForm()
    
    context = {
        'form': form,
        'title': 'Create New Writing',
    }
    return render(request, 'writing/writing_form.html', context)

@login_required
def writing_edit(request, pk):
    """Edit an existing writing piece"""
    writing = get_object_or_404(Writing, pk=pk)
    
    # Only allow author or staff to edit
    if writing.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this writing.')
        return redirect('writing:writing_detail', pk=pk)
    
    if request.method == 'POST':
        form = WritingForm(request.POST, instance=writing)
        if form.is_valid():
            writing = form.save(commit=False)
            
            # Set published_at if status changed to published
            if writing.status == 'published' and not writing.published_at:
                writing.published_at = timezone.now()
            
            writing.save()
            messages.success(request, f'Writing "{writing.title}" updated successfully!')
            return redirect('writing:writing_detail', pk=writing.pk)
    else:
        form = WritingForm(instance=writing)
    
    context = {
        'form': form,
        'writing': writing,
        'title': f'Edit: {writing.title}',
    }
    return render(request, 'writing/writing_form.html', context)

@login_required
def writing_delete(request, pk):
    """Delete a writing piece"""
    writing = get_object_or_404(Writing, pk=pk)
    
    # Only allow author or staff to delete
    if writing.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this writing.')
        return redirect('writing:writing_detail', pk=pk)
    
    if request.method == 'POST':
        title = writing.title
        writing.delete()
        messages.success(request, f'Writing "{title}" deleted successfully!')
        return redirect('writing:writing_list')
    
    context = {
        'writing': writing,
    }
    return render(request, 'writing/writing_delete.html', context)
