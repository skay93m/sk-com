/**
 * CV App JavaScript
 * Handles credential form validation and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize credential form functionality if present
    const credentialForm = document.getElementById('credential-form');
    if (credentialForm) {
        initializeCredentialForm();
    }
});

/**
 * Initialize credential form with validation and interactive features
 */
function initializeCredentialForm() {
    const iconChoiceSelect = document.getElementById('icon-choice');
    const iconUploadInput = document.getElementById('icon-upload');
    const previewDiv = document.getElementById('upload-preview');
    const previewImg = document.getElementById('preview-img');
    const existingTab = document.getElementById('existing-icon-tab');
    const uploadTab = document.getElementById('upload-icon-tab');
    const iconOptions = document.querySelectorAll('.icon-option');
    const credentialForm = document.getElementById('credential-form');
    
    // Form submission validation
    credentialForm.addEventListener('submit', function(e) {
        let errors = [];
        
        // Basic field validation
        const title = document.getElementById('id_title').value.trim();
        const institution = document.getElementById('id_institution').value.trim();
        const dateObtained = document.getElementById('id_date_obtained').value;
        const link = document.getElementById('id_link').value.trim();
        
        if (!title) {
            errors.push('Credential Title is required.');
        }
        
        if (!institution) {
            errors.push('Issuing Institution is required.');
        }
        
        if (!dateObtained) {
            errors.push('Date Obtained is required.');
        }
        
        // Icon validation
        const hasIconChoice = iconChoiceSelect && iconChoiceSelect.value !== '';
        const hasIconUpload = iconUploadInput && iconUploadInput.files.length > 0;
        
        if (!hasIconChoice && !hasIconUpload) {
            errors.push('Please either select an existing icon or upload a new one.');
        }
        
        if (hasIconChoice && hasIconUpload) {
            errors.push('Please choose either an existing icon OR upload a new one, not both.');
        }
        
        // URL validation
        if (link && !isValidUrl(link)) {
            errors.push('Please enter a valid URL for the link.');
        }
        
        // Display errors and prevent submission if any
        if (errors.length > 0) {
            e.preventDefault();
            showErrorAlert(errors);
            return false;
        }
        
        // Show loading state
        const submitBtn = credentialForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Saving...';
        
        // Re-enable button after a timeout in case of server errors
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 10000);
    });
    
    // Handle icon option clicks
    if (iconOptions.length > 0) {
        iconOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Remove active class from all options
                iconOptions.forEach(opt => opt.classList.remove('border-primary', 'bg-light'));
                // Add active class to clicked option
                this.classList.add('border-primary', 'bg-light');
                // Set the select value
                if (iconChoiceSelect) {
                    iconChoiceSelect.value = this.dataset.icon;
                }
                // Clear file upload
                if (iconUploadInput) {
                    iconUploadInput.value = '';
                    if (previewDiv) previewDiv.style.display = 'none';
                }
                
                // Clear any icon validation errors
                clearFieldError(iconChoiceSelect);
            });
        });
    }
    
    // Handle file upload preview
    if (iconUploadInput) {
        iconUploadInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    showErrorAlert(['Please upload a valid image file (PNG, JPG, JPEG, SVG, or GIF).']);
                    this.value = '';
                    return;
                }
                
                // Validate file size (limit to 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showErrorAlert(['File size must be less than 5MB.']);
                    this.value = '';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                        if (previewDiv) previewDiv.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
                
                // Clear existing icon selection
                if (iconChoiceSelect) iconChoiceSelect.value = '';
                iconOptions.forEach(opt => opt.classList.remove('border-primary', 'bg-light'));
                
                // Clear any icon validation errors
                clearFieldError(iconUploadInput);
            } else {
                if (previewDiv) previewDiv.style.display = 'none';
            }
        });
    }
    
    // Handle existing icon selection via dropdown
    if (iconChoiceSelect) {
        iconChoiceSelect.addEventListener('change', function() {
            if (this.value) {
                // Clear file upload
                if (iconUploadInput) {
                    iconUploadInput.value = '';
                    if (previewDiv) previewDiv.style.display = 'none';
                }
                
                // Highlight corresponding icon option
                iconOptions.forEach(opt => {
                    opt.classList.remove('border-primary', 'bg-light');
                    if (opt.dataset.icon === this.value) {
                        opt.classList.add('border-primary', 'bg-light');
                    }
                });
                
                // Clear any icon validation errors
                clearFieldError(this);
            } else {
                // Clear all highlights
                iconOptions.forEach(opt => opt.classList.remove('border-primary', 'bg-light'));
            }
        });
    }
    
    // Handle tab switching
    if (existingTab) {
        existingTab.addEventListener('click', function() {
            // Clear upload when switching to existing
            if (iconUploadInput) {
                iconUploadInput.value = '';
                if (previewDiv) previewDiv.style.display = 'none';
            }
        });
    }
    
    if (uploadTab) {
        uploadTab.addEventListener('click', function() {
            // Clear selection when switching to upload
            if (iconChoiceSelect) iconChoiceSelect.value = '';
            iconOptions.forEach(opt => opt.classList.remove('border-primary', 'bg-light'));
        });
    }
    
    // Initialize: highlight currently selected icon if editing
    if (iconChoiceSelect && iconChoiceSelect.value) {
        iconOptions.forEach(opt => {
            if (opt.dataset.icon === iconChoiceSelect.value) {
                opt.classList.add('border-primary', 'bg-light');
            }
        });
    }
}

/**
 * Helper function to validate URLs
 */
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

/**
 * Function to show error alerts
 */
function showErrorAlert(errors) {
    // Remove any existing error alerts
    const existingAlert = document.querySelector('.form-error-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create new error alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show form-error-alert';
    alertDiv.setAttribute('role', 'alert');
    
    let errorHtml = '<i class="bi bi-exclamation-triangle-fill me-2"></i><strong>Please fix the following errors:</strong><ul class="mb-0 mt-2">';
    errors.forEach(error => {
        errorHtml += `<li>${error}</li>`;
    });
    errorHtml += '</ul>';
    errorHtml += '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
    
    alertDiv.innerHTML = errorHtml;
    
    // Insert alert at the top of the form
    const credentialForm = document.getElementById('credential-form');
    if (credentialForm) {
        credentialForm.insertBefore(alertDiv, credentialForm.firstChild);
        
        // Scroll to the alert
        alertDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Function to show success alert
 */
function showSuccessAlert(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        <i class="bi bi-check-circle-fill me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container .row .col-lg-8');
    const headerElement = document.querySelector('h2');
    if (container && headerElement) {
        container.insertBefore(alertDiv, headerElement);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

/**
 * Helper function to clear field-specific errors
 */
function clearFieldError(field) {
    const existingAlert = document.querySelector('.form-error-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
}
