# Acknowledgment Feature - CSS Changes

This document records the CSS changes made to support the footer acknowledgment feature, which cannot be tracked in git due to .gitignore settings.

## Files Modified

- `sk/static/css/main_nav.css`

## Changes Made

### Added Acknowledgment Styles

```css
.main-footer-acknowledgment {
    margin: 0.75rem 0;
}

.acknowledgment-text {
    font-size: 0.8rem;
    color: var(--delft-blue);
    opacity: 0.7;
    margin: 0;
    text-align: center;
}

.acknowledgment-link {
    color: var(--cambridge-blue);
    text-decoration: none;
    transition: color 0.2s ease;
}

.acknowledgment-link:hover {
    color: var(--burnt-sienna);
    text-decoration: underline;
}
```

### Added Dark Mode Support

```css
/* Inside @media (prefers-color-scheme: dark) */
.acknowledgment-text {
    color: var(--eggshell);
}

.acknowledgment-link {
    color: var(--cambridge-blue);
}

.acknowledgment-link:hover {
    color: var(--sunset);
}
```

## Description

- Added styling for the footer acknowledgment section
- Maintains consistency with existing footer design
- Includes responsive design and dark mode support
- Uses the established color palette variables
- Provides hover effects for acknowledgment links

## Date

September 1, 2025

## Feature Branch

feature/acknowledgment
