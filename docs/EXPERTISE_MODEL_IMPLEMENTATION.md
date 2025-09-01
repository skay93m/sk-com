# Professional Expertise Model Implementation

This document describes the conversion of the hardcoded Professional Expertise section to a dynamic model-based system.

## Overview

The Professional Expertise section on the homepage has been converted from hardcoded HTML content to a dynamic Django model system, allowing for easy management through the admin interface.

## Model Structure

### Expertise Model (`home/models.py`)

```python
class Expertise(models.Model):
    title = models.CharField(max_length=255)           # e.g., "Healthcare & Pharmacy"
    description = models.TextField()                   # Detailed description
    icon = models.CharField(max_length=10)             # Emoji/Unicode character
    order = models.PositiveIntegerField(default=0)     # Display order
    is_active = models.BooleanField(default=True)      # Show/hide on homepage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features:**

- **Ordering**: `order` field controls display sequence (lower numbers first)
- **Visibility**: `is_active` flag allows hiding expertise areas
- **Icons**: Support for emoji and Unicode characters
- **Timestamps**: Automatic creation and update tracking

## Admin Interface

### ExpertiseAdmin Features

- **List Display**: Title, icon, description preview, order, status, update date
- **List Editing**: In-line editing of order and active status
- **Search**: Full-text search across title and description
- **Filtering**: Filter by active status and creation date
- **Ordering**: Drag-and-drop ordering via order field

### Admin Configuration

```python
@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'description_short', 'order', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'title']
```

## Template Integration

### Before (Hardcoded)

```html
<div class="main-expertise-item">
    <span class="main-expertise-icon">🏥</span>
    <div class="main-expertise-content">
        <h3 class="main-expertise-title">Healthcare & Pharmacy</h3>
        <p class="main-expertise-description">MPharm, MRPharmS - Registered pharmacist...</p>
    </div>
</div>
```

### After (Dynamic)

```html
{% for expertise in expertise_areas %}
<div class="main-expertise-item">
    <span class="main-expertise-icon">{{ expertise.icon }}</span>
    <div class="main-expertise-content">
        <h3 class="main-expertise-title">{{ expertise.title }}</h3>
        <p class="main-expertise-description">{{ expertise.description }}</p>
    </div>
</div>
{% empty %}
<div class="main-expertise-item">
    <span class="main-expertise-icon">💼</span>
    <div class="main-expertise-content">
        <h3 class="main-expertise-title">No Expertise Areas</h3>
        <p class="main-expertise-description">Please add expertise areas in the admin panel.</p>
    </div>
</div>
{% endfor %}
```

## View Updates

### Data Fetching

```python
def home(request):
    expertise_areas = Expertise.objects.filter(is_active=True)
    # ... other context data
    context = {
        'expertise_areas': expertise_areas,
        # ... other context
    }
```

**Query Optimization:**

- Filters only active expertise areas
- Orders by `order` field, then `title`
- Minimal database queries

## Default Data

Three initial expertise areas were created matching the original hardcoded content:

1. **Healthcare & Pharmacy** (🏥, Order: 1)
   - MPharm, MRPharmS certification details
   - Pharmaceutical sciences expertise

2. **Law & Jurisprudence** (⚖️, Order: 2)
   - GDL qualification
   - Healthcare law focus

3. **Technology & Innovation** (💻, Order: 3)
   - Full-stack development
   - Digital transformation

## Management Workflows

### Adding New Expertise Area

1. Access Django admin interface
2. Navigate to "Expertise Areas"
3. Click "Add Expertise"
4. Fill in required fields:
   - **Title**: Concise area name
   - **Description**: Detailed explanation
   - **Icon**: Single emoji or Unicode character
   - **Order**: Display position (lower = earlier)
   - **Is Active**: Visibility toggle

### Reordering Expertise Areas

1. In admin list view, modify `order` values
2. Use list editing for quick updates
3. Changes reflect immediately on homepage

### Hiding/Showing Areas

- Toggle `is_active` checkbox in admin list
- Inactive areas won't appear on homepage
- Content preserved for later reactivation

## Benefits

1. **Dynamic Content Management**: No code changes needed for updates
2. **Flexible Ordering**: Easy resequencing of expertise areas
3. **Visibility Control**: Show/hide areas without deletion
4. **Search & Filter**: Admin tools for easy content management
5. **Audit Trail**: Creation and update timestamps
6. **Extensible**: Model can be expanded with additional fields

## Technical Notes

- **Database**: PostgreSQL table `home_expertise`
- **Migration**: Manual table creation due to migration conflicts
- **Forms**: `ExpertiseForm` available for frontend use
- **Validation**: Order field ensures non-negative values
- **Performance**: Efficient queries with proper indexing

## Future Enhancements

Potential additions:

- Image upload for visual icons
- Rich text editor for descriptions
- Category grouping
- URL linking to detailed pages
- SEO metadata fields

## Date

September 1, 2025

## Feature Branch

feature/expertise-model
