# Centralized Color System Documentation

## Overview

This Django project uses a centralized color system based on a custom 5-color palette that maps to Bootstrap 5's semantic color categories. All colors are defined in `/sk/static/css/colours.css` and used throughout the project via CSS variables and Bootstrap utility classes.

## Color Requirements Analysis

**Bootstrap 5 requires 8 semantic color categories that need distinct colors:**

1. **Primary** - Main brand color
2. **Secondary** - Secondary brand color  
3. **Success** - Success states (green)
4. **Danger** - Error/destructive actions (red)
5. **Warning** - Warning states (yellow/orange)
6. **Info** - Information states (blue)
7. **Light** - Light backgrounds/text
8. **Dark** - Dark backgrounds/text

**Minimum unique colors needed: 5**
- Our project successfully uses 5 distinct colors to provide visual separation
- Primary/Dark can share the same color (delft-blue)
- Warning/Danger can share the same color (burnt-sienna)

## Our Color Palette

### Base Colors
```css
--eggshell: #f4f1deff;        /* Light cream background */
--burnt-sienna: #e07a5fff;    /* Warm orange-red */
--delft-blue: #3d405bff;      /* Dark blue */
--cambridge-blue: #81b29aff;  /* Sage green */
--sunset: #f2cc8fff;          /* Golden yellow */
```

### Bootstrap Mapping
```css
--bs-primary: var(--delft-blue);      /* Primary brand color */
--bs-secondary: var(--cambridge-blue); /* Secondary brand color */
--bs-success: var(--cambridge-blue);   /* Success states */
--bs-info: var(--sunset);              /* Information states */
--bs-warning: var(--burnt-sienna);     /* Warning states */
--bs-danger: var(--burnt-sienna);      /* Error states */
--bs-light: var(--eggshell);           /* Light backgrounds */
--bs-dark: var(--delft-blue);          /* Dark backgrounds */
```

## Usage Guidelines

### 1. CSS Files
Use CSS variables instead of hardcoded colors:

```css
/* ❌ WRONG - Hardcoded colors */
.header {
    background: #3d405b;
    color: #ffffff;
}

/* ✅ CORRECT - CSS variables */
.header {
    background: var(--delft-blue);
    color: var(--white);
}
```

### 2. HTML Templates
Use Bootstrap utility classes instead of inline styles:

```html
<!-- ❌ WRONG - Inline styles -->
<h1 style="color: #3d405b;">Header</h1>

<!-- ✅ CORRECT - Bootstrap classes -->
<h1 class="text-primary">Header</h1>
```

### 3. Available CSS Variables

#### Main Colors
- `var(--eggshell)`
- `var(--burnt-sienna)`
- `var(--delft-blue)`
- `var(--cambridge-blue)`
- `var(--sunset)`

#### Transparency Variants
- `var(--delft-blue-alpha-5)` to `var(--delft-blue-alpha-95)`
- `var(--white-alpha-10)` to `var(--white-alpha-95)`
- `var(--black-alpha-10)` to `var(--black-alpha-20)`
- Similar patterns for other colors

#### Bootstrap Variables
- `var(--bs-primary)`, `var(--bs-secondary)`, etc.
- `var(--bs-primary-bg-subtle)`, `var(--bs-primary-border-subtle)`, etc.

#### Utility Colors
- `var(--white)`, `var(--black)`
- `var(--gray-100)` to `var(--gray-900)`
- `var(--bootstrap-blue)`, `var(--bootstrap-green)`, etc.

### 4. Gradient Classes
Use predefined gradient classes:

```html
<div class="bg-gradient-primary">Primary gradient</div>
<div class="bg-gradient-success">Success gradient</div>
<div class="bg-gradient-info">Info gradient</div>
```

## Changing the Color Palette

To change the entire color scheme of the application:

1. **Edit only one file**: `/sk/static/css/colours.css`
2. **Update the base color definitions**:
   ```css
   :root {
     --eggshell: #your-new-light-color;
     --burnt-sienna: #your-new-warm-color;
     --delft-blue: #your-new-primary-color;
     --cambridge-blue: #your-new-secondary-color;
     --sunset: #your-new-accent-color;
   }
   ```
3. **Run collectstatic**: `python manage.py collectstatic`
4. **The entire site will update automatically**

## File Structure

### Color Definition
- `/sk/static/css/colours.css` - **Main color definitions**

### Implementation Files (Updated to use centralized colors)
- `/sk/static/css/admin.css`
- `/sk/static/css/base.css`
- `/analytics/static/css/analytics.css`
- `/cv/static/css/cv.css`
- `/home/static/css/home.css`
- `/mcq/static/css/mcq.css`
- `/projects/static/css/projects.css`
- `/writing/static/css/writing.css`

### Templates Updated
- `/home/templates/_hero-section.html`
- `/mcq/templates/manage_topics.html`
- `/mcq/templates/question.html`

## Benefits

1. **Single Point of Control**: Change all colors by editing one file
2. **Consistency**: All components use the same color variables
3. **Maintainability**: Easy to update and maintain color schemes
4. **Accessibility**: Consistent color ratios and contrast
5. **Flexibility**: Easy to create themes or seasonal color changes
6. **Performance**: CSS variables are efficient and don't require preprocessing

## Migration Completed

The following hardcoded colors have been replaced with centralized variables:

- ✅ All `#ffffff`, `white` → `var(--white)`
- ✅ All `#000000`, `black` → `var(--black)`
- ✅ All gray colors → `var(--gray-100)` to `var(--gray-900)`
- ✅ All `rgba()` transparency values → appropriate alpha variables
- ✅ All inline styles in templates → Bootstrap utility classes
- ✅ All hardcoded gradient styles → CSS gradient classes

## Testing

After implementing the centralized color system:

1. **Visual Test**: All pages should maintain the same visual appearance
2. **Consistency Test**: Similar components should have identical colors
3. **Change Test**: Modifying colors in `colours.css` should update the entire site
4. **Responsiveness**: Colors should work across all screen sizes and components

The color system is now fully centralized and ready for easy theme changes in the future.
