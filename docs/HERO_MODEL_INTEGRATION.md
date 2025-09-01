# Hero Model Integration

This document describes the integration of the Hero model data into the homepage template.

## Overview

The homepage template (`home/templates/index.html`) has been updated to use dynamic content from the Hero model instead of hardcoded text.

## Changes Made

### Template Updates (`home/templates/index.html`)

**Before (Hardcoded):**

```html
<h1 class="main-name">Hi, I'm Syafiq!</h1>
<div class="main-intro">
    <p>I am a pharmacist, aspiring barrister, and technology enthusiast based in the UK...</p>
</div>
```

**After (Dynamic):**

```html
<h1 class="main-name">{{ header }}</h1>
<div class="main-intro">
    <p>{{ tagline }}</p>
</div>
```

### Data Flow

1. **Model**: `Hero` model with `header`, `tagline`, and `cta` fields
2. **View**: `home.views.home()` fetches first Hero record and passes to template
3. **Template**: Uses `{{ header }}` and `{{ tagline }}` variables
4. **Fallback**: If no Hero exists, defaults to "Welcome" and "Personal Portfolio & Blog"

## Hero Model Structure

```python
class Hero(models.Model):
    header = models.CharField(max_length=255)      # Main title/heading
    tagline = models.TextField()                   # Description/subtitle
    cta = models.CharField(max_length=255)         # Call-to-action text
    updated_at = models.DateTimeField(auto_now=True)
```

## Admin Management

- **Access**: `/admin/` → Heroes section
- **CRUD**: Create, Read, Update, Delete hero sections
- **Ordering**: Most recent first (`-updated_at`)
- **Display**: Shows header, truncated tagline, CTA, and update date

## Content Management

### Creating New Hero Content

1. Access Django admin interface
2. Navigate to Heroes section
3. Click "Add Hero"
4. Fill in:
   - **Header**: Main title (e.g., "Hi, I'm Syafiq!")
   - **Tagline**: Detailed description paragraph
   - **CTA**: Call-to-action text (optional)

### Current Hero Record

A default Hero record has been created with:

- **Header**: "Hi, I'm Syafiq!"
- **Tagline**: Original hardcoded content about pharmacy, law, and technology
- **CTA**: "Get In Touch"

## Benefits

1. **Dynamic Content**: Homepage content can be updated without code changes
2. **Admin Interface**: Non-technical users can manage hero content
3. **Version Control**: Hero updates are tracked with timestamps
4. **Fallback Safety**: Default content prevents blank homepage
5. **Flexible Structure**: CTA field available for future use

## Usage Examples

### Updating Homepage Content

1. Log into admin interface
2. Edit existing Hero record or create new one
3. Save changes
4. Homepage automatically reflects new content

### Multiple Heroes

- System uses first Hero record (`Hero.objects.first()`)
- Ordered by most recent update
- Can maintain multiple heroes for A/B testing or backup

## Technical Notes

- **View Logic**: `home/views.py` line 15-16
- **Template Logic**: Uses Django template variables
- **Database**: Hero model with proper field types
- **Migration**: Standard Django model migration applied

## Date

September 1, 2025

## Feature Branch

feature/hero-integration
