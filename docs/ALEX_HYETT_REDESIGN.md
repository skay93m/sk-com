# Alex Hyett-Inspired Website Redesign

## Overview

This document outlines the redesign of the SK-COM website to match the clean, minimalist design of Alex Hyett's website while retaining our existing color palette and core functionality.

## Design Philosophy

The Alex Hyett design follows these principles:

- **Typography-first approach**: Clean, readable fonts with clear hierarchy
- **Minimal visual clutter**: Focus on content, not decorative elements
- **Content organization**: Clear sectioning of different types of content
- **Personal branding**: Direct, professional introduction
- **Accessibility**: High contrast, clear navigation, semantic HTML

## Key Changes

### 1. Homepage Layout (`index_alex_hyett.html`)

**New Structure:**

- **Hero Section**: Personal introduction ("Hi, I'm Syafiq!")
- **Active Projects**: Current ongoing work
- **Recently Finished Projects**: Completed initiatives
- **Latest Writings**: Recent blog posts/articles
- **Professional Expertise**: Skills and background
- **Quick Links**: Direct navigation

**Content Organization:**

- Simple card-based layout for projects
- Chronological list format for writings
- Icon-based expertise display
- Direct contact information and social links

### 2. Navigation (`_navbar_alex.html` + `alex_nav.css`)

**Features:**

- Minimalist horizontal layout
- Clean typography with proper spacing
- Sticky navigation with subtle background
- Responsive mobile menu
- Simplified auth section

**Styling:**

- Uses existing color palette
- Subtle hover effects with color transitions
- Focus states for accessibility
- Dark mode support

### 3. Color Palette Integration

**Maintained Existing Colors:**

- `--delft-blue` (#3d405bff): Primary text and accents
- `--cambridge-blue` (#81b29aff): Links and highlights
- `--eggshell` (#f4f1deff): Background and cards
- `--burnt-sienna` (#e07a5fff): Warning/admin elements
- `--sunset` (#f2cc8fff): Info accents

**Design Approach:**

- Typography-focused with minimal use of colors
- High contrast for readability
- Consistent color application across components

### 4. Typography & Spacing

**Font Stack:**

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**Typography Scale:**

- Hero title: 2.5rem (40px)
- Section titles: 1.5rem (24px)
- Body text: 1.1rem (17.6px)
- Small text: 0.9rem (14.4px)

**Spacing System:**

- Container max-width: 800px (matches Alex Hyett)
- Section spacing: 4rem (64px)
- Card padding: 1.5rem (24px)
- Line height: 1.7 for readability

## Technical Implementation

### Files Created/Modified

1. **Templates:**
   - `home/templates/index_alex_hyett.html` - New homepage layout
   - `sk/templates/_navbar_alex.html` - New navigation
   - `sk/templates/base.html` - Updated to use new navigation
   - `sk/templates/_footer.html` - Simplified footer

2. **Stylesheets:**
   - `home/static/css/alex_hyett_style.css` - Main homepage styling
   - `sk/static/css/alex_nav.css` - Navigation and footer styling

3. **Views:**
   - `home/views.py` - Updated to use new template and fetch recent posts

### Responsive Design

**Breakpoints:**

- Mobile: < 768px
- Tablet/Desktop: ≥ 768px

**Mobile Adaptations:**

- Collapsible navigation
- Stacked content layout
- Reduced typography scale
- Optimized touch targets

### Accessibility Features

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **Focus States**: Visible focus indicators for all interactive elements
- **Color Contrast**: High contrast ratios maintained
- **Alternative Text**: Meaningful alt text for images
- **Keyboard Navigation**: Full keyboard accessibility

## Performance Considerations

- **Minimal CSS**: Only essential styles loaded
- **CSS Variables**: Efficient color management
- **Optimized Images**: Proper sizing and compression
- **Progressive Enhancement**: Works without JavaScript

## Browser Support

- **Modern Browsers**: Full support for Chrome, Firefox, Safari, Edge
- **CSS Variables**: Fallbacks for older browsers
- **Flexbox/Grid**: Progressive enhancement approach

## Future Enhancements

1. **Dark Mode Toggle**: Explicit user control
2. **Animation**: Subtle micro-interactions
3. **Search Functionality**: Site-wide content search
4. **RSS Feed**: Integration with writings section
5. **Performance Metrics**: Core Web Vitals optimization

## Comparison with Original Design

| Aspect | Original Design | Alex Hyett Design |
|--------|----------------|-------------------|
| Layout | Complex grid with multiple sections | Simple single-column layout |
| Hero | Large background with overlay | Clean typography-focused intro |
| Navigation | Bootstrap navbar with icons | Minimal text-based navigation |
| Colors | Full palette usage | Selective, high-contrast usage |
| Typography | Mixed scales | Consistent hierarchy |
| Content | Statistics and charts | Content and projects focus |

## Maintenance

- **CSS Variables**: Centralized color management in `colours.css`
- **Modular Styles**: Separate files for different components
- **Documentation**: Inline comments for complex styles
- **Version Control**: Proper git flow with feature branches

## Testing Checklist

- [ ] Homepage loads correctly
- [ ] Navigation works on all devices
- [ ] All links function properly
- [ ] Color contrast meets WCAG guidelines
- [ ] Mobile responsiveness verified
- [ ] Performance metrics acceptable
- [ ] Cross-browser compatibility confirmed

---

*Created: September 1, 2025*  
*Author: GitHub Copilot*  
*Branch: feature/alex-hyett-design-redesign*
