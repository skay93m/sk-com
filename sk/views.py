from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import View


class SecureAdminLoginView(LoginView):
    """
    Custom login view that sets a secure session flag for admin access.
    """
    template_name = 'admin/login.html'
    
    def form_valid(self, form):
        # Set the secure admin access flag in session
        self.request.session['secure_admin_access'] = True
        response = super().form_valid(form)
        
        # Redirect to admin or the 'next' parameter
        next_url = self.request.GET.get('next', '/admin/')
        return redirect(next_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Secure Admin Login'
        context['site_header'] = 'Secure Admin Access'
        return context


class SecureAdminLogoutView(View):
    """
    Custom logout view that clears the secure session flag.
    """
    
    def get(self, request):
        # Clear the secure admin access flag
        if 'secure_admin_access' in request.session:
            del request.session['secure_admin_access']
        
        # Redirect to Django's admin logout
        return redirect('/admin/logout/')
