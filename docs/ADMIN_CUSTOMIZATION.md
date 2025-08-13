# Django Admin Customization Guide

## Overview
You've successfully customized your Django admin interface to match your site's base.html template. Here's what has been implemented and how to extend it further.

## What's Been Done

### 1. Custom Admin Templates Created
- **`admin/base.html`**: Main admin template that matches your site's design
- **`admin/base_site.html`**: Extends base.html for admin pages
- **`admin/index.html`**: Custom admin dashboard

### 2. Design Features
- Uses your existing Bootstrap 5 setup
- Matches your color scheme (colours.css)
- Includes your site navigation header
- Custom admin header with branding
- Consistent footer across all admin pages
- Bootstrap Icons integration

### 3. Site Header Configuration
The admin site header is configured in `sk/apps.py`:
```python
def ready(self):
    admin.site.site_header = "SK Portfolio Administration"
    admin.site.site_title = "SK Admin"
    admin.site.index_title = "Welcome to SK Portfolio Admin"
```

## How to Further Customize

### 1. Add App-Specific Templates
For specific models or apps, create templates in:
```
sk/templates/admin/[app_name]/
sk/templates/admin/[app_name]/[model_name]/
```

### 2. Override Change List Templates
To customize how model lists appear:
```html
<!-- admin/[app_name]/[model_name]/change_list.html -->
{% extends "admin/change_list.html" %}

{% block content_title %}
    <h1><i class="bi bi-list"></i> {{ opts.verbose_name_plural|capfirst }}</h1>
{% endblock %}
```

### 3. Override Change Form Templates
To customize individual model editing forms:
```html
<!-- admin/[app_name]/[model_name]/change_form.html -->
{% extends "admin/change_form.html" %}

{% block content_title %}
    <h1><i class="bi bi-pencil"></i> Edit {{ opts.verbose_name }}</h1>
{% endblock %}
```

### 4. Custom CSS Styling
Add more styling in the `<style>` section of `admin/base.html`:
```css
/* Custom admin styling */
.admin-dashboard .card {
    transition: transform 0.2s;
}
.admin-dashboard .card:hover {
    transform: translateY(-2px);
}
```

### 5. Admin ModelAdmin Customizations
In your model admin classes, you can customize further:
```python
from django.contrib import admin

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ['field1', 'field2', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    # Custom admin templates
    change_list_template = 'admin/your_app/your_model/change_list.html'
    change_form_template = 'admin/your_app/your_model/change_form.html'
```

### 6. Adding More Bootstrap Components
You can add more Bootstrap components to enhance the admin:
```html
<!-- Add alerts, modals, tooltips, etc. -->
<div class="alert alert-info" role="alert">
    <i class="bi bi-info-circle"></i> Additional information here
</div>
```

## File Structure
```
sk/
├── templates/
│   └── admin/
│       ├── base.html              # Main admin layout
│       ├── base_site.html         # Admin site base
│       ├── index.html             # Admin dashboard
│       └── includes/
│           └── fieldset.html      # Form fieldset styling
├── apps.py                        # Admin site configuration
└── static/
    └── css/
        ├── colours.css            # Your color scheme
        └── fonts.css              # Your font styling
```

## Tips for Further Customization

1. **Test Changes**: Always test admin customizations with different user permissions
2. **Backup Templates**: Keep copies of working templates before making major changes
3. **Use Django Admin Documentation**: Reference Django's admin documentation for advanced features
4. **Mobile Responsive**: Your templates use Bootstrap 5, so they're already mobile-friendly
5. **Performance**: Custom templates can impact performance; optimize when needed

## Troubleshooting

### Template Not Loading
- Check `TEMPLATES` setting in `settings.py`
- Ensure template directory is in `DIRS`
- Verify file names match Django's expected conventions

### CSS Not Applying
- Check static files configuration
- Run `collectstatic` if in production
- Verify CSS file paths in templates

### i18n Issues
- Use `{% load i18n %}` at the top of templates using translation
- Replace `{% trans %}` tags with plain text if not using internationalization
- Use `{% blocktrans %}` carefully with proper loading

The admin interface now matches your site's design while maintaining full Django admin functionality!
