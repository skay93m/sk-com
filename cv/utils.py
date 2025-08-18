import os
from django.conf import settings
from django.templatetags.static import static

def get_available_icons():
    """Get list of all available icons with their static URLs"""
    icon_dir = os.path.join(settings.BASE_DIR, 'cv', 'static', 'icon')
    icons = []
    
    if os.path.exists(icon_dir):
        for filename in os.listdir(icon_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                icons.append({
                    'filename': filename,
                    'url': static(f'icon/{filename}'),
                    'name': os.path.splitext(filename)[0]
                })
    
    return sorted(icons, key=lambda x: x['name'])
