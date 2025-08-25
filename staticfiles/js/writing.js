/**
 * Writing App JavaScript
 * Handles writing form interactions and validations
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeWritingFunctionality();
});

/**
 * Initialize all writing-related functionality
 */
function initializeWritingFunctionality() {
    // Initialize form functionality
    initializeWritingForm();
    
    // Initialize delete confirmations
    initializeDeleteConfirmation();
    
    // Initialize tag input functionality
    initializeTagInput();
    
    // Initialize content preview
    initializeContentPreview();
}

/**
 * Initialize writing form functionality
 */
function initializeWritingForm() {
    // Auto-generate slug from title
    initializeSlugGeneration();
    
    // Form validation
    initializeFormValidation();
    
    // Character count for excerpt
    initializeCharacterCount();
}

/**
 * Initialize automatic slug generation from title
 */
function initializeSlugGeneration() {
    const titleField = document.getElementById('id_title');
    const slugField = document.getElementById('id_slug');
    
    if (titleField && slugField && !slugField.value) {
        titleField.addEventListener('input', function() {
            const title = this.value;
            const slug = generateSlug(title);
            slugField.value = slug;
            
            // Visual feedback
            slugField.classList.add('slug-generated');
            setTimeout(() => {
                slugField.classList.remove('slug-generated');
            }, 300);
        });
    }
}

/**
 * Generate URL-friendly slug from text
 */
function generateSlug(text) {
    return text.toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-+|-+$/g, '');
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const form = document.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Clear previous validation
        clearValidationClasses();
        
        // Validate required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                markFieldAsInvalid(field, 'This field is required.');
                isValid = false;
            } else {
                markFieldAsValid(field);
            }
        });
        
        // Validate slug uniqueness (if needed)
        const slugField = document.getElementById('id_slug');
        if (slugField && slugField.value) {
            if (!isValidSlug(slugField.value)) {
                markFieldAsInvalid(slugField, 'Slug can only contain letters, numbers, and hyphens.');
                isValid = false;
            }
        }
        
        // Validate content length
        const contentField = document.getElementById('id_content');
        if (contentField && contentField.value.trim().length < 10) {
            markFieldAsInvalid(contentField, 'Content must be at least 10 characters long.');
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            showAlert('Please fix the form errors before submitting.', 'danger');
            
            // Scroll to first error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
            
            return false;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Saving...';
            
            // Re-enable after timeout
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 10000);
        }
    });
}

/**
 * Clear all validation classes
 */
function clearValidationClasses() {
    const fields = document.querySelectorAll('.is-valid, .is-invalid');
    fields.forEach(field => {
        field.classList.remove('is-valid', 'is-invalid');
    });
    
    // Clear custom error messages
    const errorMessages = document.querySelectorAll('.custom-error-message');
    errorMessages.forEach(msg => msg.remove());
}

/**
 * Mark field as invalid with custom message
 */
function markFieldAsInvalid(field, message) {
    field.classList.remove('is-valid');
    field.classList.add('is-invalid');
    
    // Add custom error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback custom-error-message';
    errorDiv.textContent = message;
    
    // Insert after field
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
}

/**
 * Mark field as valid
 */
function markFieldAsValid(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
}

/**
 * Validate slug format
 */
function isValidSlug(slug) {
    return /^[a-z0-9-]+$/.test(slug) && !slug.startsWith('-') && !slug.endsWith('-');
}

/**
 * Initialize character count for excerpt field
 */
function initializeCharacterCount() {
    const excerptField = document.getElementById('id_excerpt');
    if (!excerptField) return;
    
    const maxLength = 200; // Reasonable excerpt length
    
    // Create counter element
    const counter = document.createElement('div');
    counter.className = 'form-text character-counter';
    counter.textContent = `0 / ${maxLength} characters`;
    
    // Insert after excerpt field
    excerptField.parentNode.appendChild(counter);
    
    // Update counter on input
    excerptField.addEventListener('input', function() {
        const length = this.value.length;
        counter.textContent = `${length} / ${maxLength} characters`;
        
        if (length > maxLength) {
            counter.classList.add('text-danger');
            this.classList.add('is-invalid');
        } else {
            counter.classList.remove('text-danger');
            this.classList.remove('is-invalid');
        }
    });
    
    // Initial count
    excerptField.dispatchEvent(new Event('input'));
}

/**
 * Initialize tag input functionality
 */
function initializeTagInput() {
    const tagField = document.getElementById('id_tags');
    if (!tagField) return;
    
    // Add helper text
    const helpText = document.createElement('div');
    helpText.className = 'form-text';
    helpText.innerHTML = 'Enter tags separated by commas. <small>Example: technology, web, programming</small>';
    
    tagField.parentNode.appendChild(helpText);
    
    // Format tags on blur
    tagField.addEventListener('blur', function() {
        const tags = this.value.split(',').map(tag => tag.trim()).filter(tag => tag);
        this.value = tags.join(', ');
    });
    
    // Visual feedback for tag input
    tagField.addEventListener('input', function() {
        const tags = this.value.split(',').map(tag => tag.trim()).filter(tag => tag);
        
        if (tags.length > 10) {
            markFieldAsInvalid(this, 'Maximum 10 tags allowed.');
        } else {
            this.classList.remove('is-invalid');
        }
    });
}

/**
 * Initialize content preview functionality
 */
function initializeContentPreview() {
    const contentField = document.getElementById('id_content');
    if (!contentField) return;
    
    // Add preview button
    const previewBtn = document.createElement('button');
    previewBtn.type = 'button';
    previewBtn.className = 'btn btn-outline-secondary btn-sm mt-2';
    previewBtn.innerHTML = '<i class="bi bi-eye"></i> Preview';
    
    contentField.parentNode.appendChild(previewBtn);
    
    previewBtn.addEventListener('click', function() {
        showContentPreview(contentField.value);
    });
}

/**
 * Show content preview in modal
 */
function showContentPreview(content) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('content-preview-modal');
    
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'content-preview-modal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Content Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="preview-content" class="writing-content"></div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // Update content
    const previewContent = document.getElementById('preview-content');
    previewContent.innerHTML = content.replace(/\n/g, '<br>');
    
    // Show modal
    if (typeof bootstrap !== 'undefined') {
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }
}

/**
 * Initialize delete confirmation
 */
function initializeDeleteConfirmation() {
    const deleteForm = document.getElementById('delete-form');
    if (!deleteForm) return;
    
    deleteForm.addEventListener('submit', function(e) {
        const confirmed = confirm('Are you sure you want to delete this writing? This action cannot be undone.');
        
        if (!confirmed) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Deleting...';
        }
    });
}

/**
 * Utility function to show alerts
 */
function showAlert(message, type = 'info') {
    const existingAlert = document.querySelector('.dynamic-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show dynamic-alert" role="alert">
            <i class="bi bi-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.querySelector('.container') || document.querySelector('main') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-dismiss success/info alerts
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            const alert = document.querySelector('.dynamic-alert');
            if (alert) alert.remove();
        }, 5000);
    }
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'danger': 'exclamation-triangle-fill'
    };
    return icons[type] || 'info-circle';
}

// Export functions for external use
window.WritingApp = {
    generateSlug,
    showAlert,
    showContentPreview,
    markFieldAsValid,
    markFieldAsInvalid
};
