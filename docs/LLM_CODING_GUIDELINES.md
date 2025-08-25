# LLM Coding Guidelines for Django Project

## Overview
This document provides coding standards and best practices for LLM assistants when making modifications to this Django project. Following these guidelines ensures code consistency, maintainability, and adherence to modern web development practices.

## Table of Contents
1. [CSS and JavaScript Organization](#css-and-javascript-organization)
2. [Django Template Best Practices](#django-template-best-practices)
3. [File Structure and Naming](#file-structure-and-naming)
4. [Code Quality Standards](#code-quality-standards)
5. [Security Considerations](#security-considerations)
6. [Documentation Requirements](#documentation-requirements)

---

## CSS and JavaScript Organization

### 🎯 Primary Rule: External Files Only
**ALWAYS put custom CSS and JavaScript in their respective static files. NEVER use inline styles or embedded scripts.**

#### CSS Guidelines

1. **Location**: Place all CSS in `app_name/static/css/app_name.css`
   ```
   home/static/css/home.css
   mcq/static/css/mcq.css
   cv/static/css/cv.css
   projects/static/css/projects.css
   analytics/static/css/analytics.css
   writing/static/css/writing.css
   ```

2. **Template Integration**: Always use the `extra_css` block
   ```django
   {% block extra_css %}
   <link rel="stylesheet" href="{% static 'css/app_name.css' %}">
   {% endblock %}
   ```

3. **Prohibited Practices**:
   ```django
   <!-- ❌ NEVER DO THIS -->
   <div style="color: red; margin: 10px;">Content</div>
   
   <!-- ❌ NEVER DO THIS -->
   <style>
   .my-class { color: blue; }
   </style>
   
   <!-- ✅ DO THIS INSTEAD -->
   <div class="text-danger my-custom-margin">Content</div>
   ```

4. **CSS Organization Structure**:
   ```css
   /* app_name.css structure */
   
   /* App-specific styles */
   
   /* Header and navigation styles */
   .app-header-gradient { }
   
   /* Card and component styles */
   .custom-card { }
   
   /* Form styles */
   .custom-form-control { }
   
   /* Button styles */
   .custom-btn { }
   
   /* Utility classes */
   .utility-class { }
   
   /* Responsive styles */
   @media (max-width: 768px) { }
   ```

#### JavaScript Guidelines

1. **Location**: Place all JavaScript in `app_name/static/js/app_name.js`
   ```
   home/static/js/home.js
   mcq/static/js/mcq.js
   cv/static/js/cv.js
   projects/static/js/projects.js
   analytics/static/js/analytics.js
   writing/static/js/writing.js
   ```

2. **Template Integration**: Always use the `extra_js` block
   ```django
   {% block extra_js %}
   <script src="{% static 'js/app_name.js' %}"></script>
   {% endblock %}
   ```

3. **Prohibited Practices**:
   ```django
   <!-- ❌ NEVER DO THIS -->
   <button onclick="myFunction()">Click me</button>
   
   <!-- ❌ NEVER DO THIS -->
   <script>
   function myFunction() { alert('Hello'); }
   </script>
   
   <!-- ✅ DO THIS INSTEAD -->
   <button class="my-custom-btn" data-action="click-handler">Click me</button>
   ```

4. **JavaScript Organization Structure**:
   ```javascript
   /**
    * App Name JavaScript
    * Description of functionality
    */
   
   document.addEventListener('DOMContentLoaded', function() {
       initializeAppFunctionality();
   });
   
   /**
    * Initialize all app-related functionality
    */
   function initializeAppFunctionality() {
       // Initialize components
   }
   
   // Utility functions
   function utilityFunction() { }
   
   // Event handlers
   function handleEvent() { }
   ```

---

## Django Template Best Practices

### Template Structure
1. **Always extend base template**:
   ```django
   {% extends "base.html" %}
   {% load static %}
   ```

2. **Use semantic block structure**:
   ```django
   {% block extra_css %}
   <!-- App-specific CSS -->
   {% endblock %}
   
   {% block title %}Page Title - Syafiq Kay{% endblock %}
   
   {% block content %}
   <!-- Page content -->
   {% endblock %}
   
   {% block extra_js %}
   <!-- App-specific JavaScript -->
   {% endblock %}
   ```

### HTML Class Naming
1. **Use semantic, descriptive class names**:
   ```django
   <!-- ✅ Good -->
   <div class="mcq-header-gradient">
   <div class="choice-number">
   <div class="sticky-sidebar-top">
   
   <!-- ❌ Avoid -->
   <div class="red-box">
   <div class="div1">
   ```

2. **Follow BEM-like naming for complex components**:
   ```css
   .mcq-edit-header { }
   .choice-item { }
   .choice-item__number { }
   .choice-item--selected { }
   ```

---

## File Structure and Naming

### Static Files Organization
```
app_name/
├── static/
│   ├── css/
│   │   └── app_name.css
│   ├── js/
│   │   └── app_name.js
│   └── images/
│       └── app_specific_images/
├── templates/
│   └── app_name/
│       └── template_name.html
└── other_app_files.py
```

### Naming Conventions
1. **CSS Classes**: Use kebab-case
   - `mcq-header-gradient`
   - `choice-number`
   - `sticky-sidebar-top`

2. **JavaScript Functions**: Use camelCase
   - `initializeMCQFunctionality()`
   - `handleFormSubmission()`
   - `validateUserInput()`

3. **File Names**: Use snake_case for Python, kebab-case for static files
   - `edit_mcq.html`
   - `mcq.css`
   - `mcq.js`

---

## Code Quality Standards

### CSS Quality
1. **Use consistent indentation** (2 or 4 spaces)
2. **Group related styles together**
3. **Use comments to separate sections**
4. **Prefer classes over IDs for styling**
5. **Use CSS custom properties for repeated values**:
   ```css
   :root {
       --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
       --card-shadow: 0 6px 20px rgba(0,0,0,0.1);
   }
   ```

### JavaScript Quality
1. **Use `const` and `let`, avoid `var`**
2. **Add JSDoc comments for functions**
3. **Use meaningful variable names**
4. **Handle errors gracefully**
5. **Use event delegation for dynamic content**

### Bootstrap Integration
1. **Prefer Bootstrap classes when available**
2. **Extend Bootstrap with custom classes, don't override**
3. **Use Bootstrap's utility classes for simple styling**:
   ```django
   <!-- ✅ Good: Use Bootstrap utilities -->
   <div class="d-flex justify-content-between align-items-center mb-3">
   
   <!-- ✅ Good: Custom class for complex styling -->
   <div class="mcq-header-gradient">
   ```

---

## Security Considerations

### Template Security
1. **Always escape user input**:
   ```django
   {{ user_input|escape }}
   {{ user_input|safe }}  <!-- Only when absolutely necessary -->
   ```

2. **Use CSRF protection**:
   ```django
   <form method="post">
       {% csrf_token %}
       <!-- form fields -->
   </form>
   ```

### JavaScript Security
1. **Validate data before processing**
2. **Use textContent instead of innerHTML when possible**
3. **Sanitize any user input used in DOM manipulation**

---

## Documentation Requirements

### CSS Documentation
```css
/* Section Description */
/* Brief explanation of what this section styles */

/* Component: Choice Number Styling */
/* Creates gradient backgrounds for MCQ choice numbers */
.choice-number {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    /* Additional properties */
}
```

### JavaScript Documentation
```javascript
/**
 * Initialize MCQ form functionality
 * Sets up event listeners for form validation and choice management
 * @param {string} formId - The ID of the form to initialize
 */
function initializeMCQForm(formId) {
    // Implementation
}
```

---

## Enforcement Checklist

Before making any changes, verify:

- [ ] ✅ No inline `style=""` attributes in HTML
- [ ] ✅ No `<style>` blocks in templates
- [ ] ✅ No inline `onclick=""` or similar attributes
- [ ] ✅ No `<script>` blocks in templates (except external includes)
- [ ] ✅ CSS properly organized in `app_name/static/css/app_name.css`
- [ ] ✅ JavaScript properly organized in `app_name/static/js/app_name.js`
- [ ] ✅ Proper use of `{% block extra_css %}` and `{% block extra_js %}`
- [ ] ✅ Semantic, descriptive class names used
- [ ] ✅ Bootstrap classes utilized where appropriate
- [ ] ✅ Code properly commented and documented

---

## Common Patterns

### Adding New Styling
1. Identify the app the template belongs to
2. Add CSS rules to `app_name/static/css/app_name.css`
3. Create semantic class names
4. Apply classes to HTML elements
5. Ensure `{% block extra_css %}` includes the CSS file

### Adding New JavaScript Functionality
1. Add function to `app_name/static/js/app_name.js`
2. Use proper event listeners (no inline handlers)
3. Document the function with JSDoc
4. Ensure `{% block extra_js %}` includes the JS file
5. Test functionality across browsers

### Refactoring Existing Code
1. Identify inline styles/scripts to extract
2. Move to appropriate static files
3. Replace with semantic class names
4. Test to ensure functionality remains intact
5. Remove all inline code

---

## Examples

### Before (❌ Incorrect)
```django
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px;">
    <h2 onclick="toggleContent()">Header</h2>
</div>

<style>
.my-style { color: red; }
</style>

<script>
function toggleContent() { /* code */ }
</script>
```

### After (✅ Correct)
```django
<!-- Template -->
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/app_name.css' %}">
{% endblock %}

<div class="custom-header-gradient p-4">
    <h2 class="toggle-header" data-action="toggle-content">Header</h2>
</div>

{% block extra_js %}
<script src="{% static 'js/app_name.js' %}"></script>
{% endblock %}
```

```css
/* app_name.css */
.custom-header-gradient {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
```

```javascript
/* app_name.js */
document.addEventListener('DOMContentLoaded', function() {
    const toggleHeaders = document.querySelectorAll('.toggle-header');
    toggleHeaders.forEach(header => {
        header.addEventListener('click', toggleContent);
    });
});

function toggleContent() {
    // Implementation
}
```

---

This guideline ensures clean, maintainable, and professional code organization that follows modern web development best practices.
