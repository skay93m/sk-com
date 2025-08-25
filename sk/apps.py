from django.apps import AppConfig
from django.contrib import admin


class SkConfig(AppConfig):
    name = 'sk'
    verbose_name = 'SK Portfolio'

    def ready(self):
        # Import here to avoid import issues
        from django.contrib.sessions.models import Session
        
        # Customize the admin site headers
        admin.site.site_header = "SK Portfolio Administration"
        admin.site.site_title = "SK Admin"
        admin.site.index_title = "Welcome to SK Portfolio Admin"
        
        # Register Session model if not already registered
        if not admin.site.is_registered(Session):
            @admin.register(Session)
            class SessionAdmin(admin.ModelAdmin):
                """Admin interface for Django sessions."""
                list_display = ('session_key', 'expire_date', 'get_decoded')
                list_filter = ('expire_date',)
                search_fields = ('session_key',)
                readonly_fields = ('session_key', 'session_data', 'expire_date', 'get_decoded')
                
                def get_decoded(self, obj):
                    """Display decoded session data in a readable format."""
                    try:
                        decoded = obj.get_decoded()
                        return str(decoded)[:100] + "..." if len(str(decoded)) > 100 else str(decoded)
                    except:
                        return "Unable to decode"
                get_decoded.short_description = "Session Data"
                
                def has_add_permission(self, request):
                    """Disable adding sessions through admin."""
                    return False
