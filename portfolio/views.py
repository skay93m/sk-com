from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404
from .models import WorkingIdentity, IdentityFeed


class PortfolioView(TemplateView):
    template_name = "portfolio.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        identities = WorkingIdentity.objects.all()
        
        for identity in identities:
            identity.status_text = identity.description
            latest = identity.latest_entry()
            if latest:
                identity.latest_entry_text = latest.status
                identity.next_action_text = latest.next_action
            else:
                identity.latest_entry_text = "No entries yet"
                identity.next_action_text = ""
        
        context['identities'] = identities
        return context


class IdentityDetailView(TemplateView):
    template_name = "identity_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        identity_slug = self.kwargs.get('identity')
        working_identity = get_object_or_404(WorkingIdentity, identity=identity_slug)
        feed_entries = IdentityFeed.objects.filter(working_identity=working_identity)
        
        context['working_identity'] = working_identity
        context['feed_entries'] = feed_entries
        return context