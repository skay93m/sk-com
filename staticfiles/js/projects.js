/**
 * Projects App JavaScript
 * Handles project interactions and form validations
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeProjectFunctionality();
});

/**
 * Initialize all project-related functionality
 */
function initializeProjectFunctionality() {
    // Initialize delete confirmation
    initializeProjectDeleteConfirmation();
    
    // Initialize project filters
    initializeProjectFilters();
    
    // Initialize project form functionality
    initializeProjectForm();
    
    // Initialize project cards animations
    initializeProjectAnimations();
}

/**
 * Initialize project delete confirmation
 */
function initializeProjectDeleteConfirmation() {
    const confirmInput = document.getElementById('confirm-title');
    const deleteButton = document.getElementById('delete-button');
    const deleteForm = document.getElementById('project-delete-form');
    
    // Get expected title from data attribute instead of window variable
    const expectedTitle = deleteForm ? deleteForm.dataset.projectTitle : null;
    
    if (confirmInput && deleteButton && expectedTitle) {
        confirmInput.addEventListener('input', function() {
            if (this.value === expectedTitle) {
                deleteButton.disabled = false;
                deleteButton.classList.remove('btn-outline-danger');
                deleteButton.classList.add('btn-danger');
            } else {
                deleteButton.disabled = true;
                deleteButton.classList.remove('btn-danger');
                deleteButton.classList.add('btn-outline-danger');
            }
        });
    }
    
    // Additional delete form handling
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            const confirmed = confirm('Are you sure you want to delete this project? This action cannot be undone.');
            
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
}

/**
 * Initialize project filters
 */
function initializeProjectFilters() {
    const filterButtons = document.querySelectorAll('.filter-tab');
    const projectCards = document.querySelectorAll('.project-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter projects
            filterProjects(filter, projectCards);
        });
    });
}

/**
 * Filter projects based on status
 */
function filterProjects(filter, projectCards) {
    projectCards.forEach(card => {
        const projectStatus = card.dataset.status;
        
        if (filter === 'all' || filter === projectStatus) {
            card.style.display = 'block';
            card.classList.add('fade-in');
        } else {
            card.style.display = 'none';
            card.classList.remove('fade-in');
        }
    });
    
    // Update counts
    updateFilterCounts();
}

/**
 * Update project count displays
 */
function updateFilterCounts() {
    const visibleCards = document.querySelectorAll('.project-card[style*="display: block"], .project-card:not([style*="display: none"])');
    const countDisplay = document.getElementById('project-count');
    
    if (countDisplay) {
        countDisplay.textContent = `${visibleCards.length} project(s)`;
    }
}

/**
 * Initialize project form functionality
 */
function initializeProjectForm() {
    const projectForm = document.getElementById('project-form');
    if (!projectForm) return;
    
    // Auto-generate slug from title
    initializeProjectSlugGeneration();
    
    // Form validation
    projectForm.addEventListener('submit', function(e) {
        if (!validateProjectForm()) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Saving...';
            
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 10000);
        }
    });
}

/**
 * Initialize project slug generation
 */
function initializeProjectSlugGeneration() {
    const titleField = document.getElementById('id_title');
    const slugField = document.getElementById('id_slug');
    
    if (titleField && slugField && !slugField.value) {
        titleField.addEventListener('input', function() {
            const title = this.value;
            const slug = generateSlug(title);
            slugField.value = slug;
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
 * Validate project form
 */
function validateProjectForm() {
    const errors = [];
    
    // Required field validation
    const titleField = document.getElementById('id_title');
    if (titleField && !titleField.value.trim()) {
        errors.push('Project title is required.');
        markFieldAsInvalid(titleField);
    }
    
    const descriptionField = document.getElementById('id_description');
    if (descriptionField && !descriptionField.value.trim()) {
        errors.push('Project description is required.');
        markFieldAsInvalid(descriptionField);
    }
    
    const statusField = document.getElementById('id_status');
    if (statusField && !statusField.value) {
        errors.push('Please select a project status.');
        markFieldAsInvalid(statusField);
    }
    
    // URL validation
    const linkField = document.getElementById('id_link');
    if (linkField && linkField.value && !isValidUrl(linkField.value)) {
        errors.push('Please enter a valid URL for the project link.');
        markFieldAsInvalid(linkField);
    }
    
    const repoField = document.getElementById('id_repository_url');
    if (repoField && repoField.value && !isValidUrl(repoField.value)) {
        errors.push('Please enter a valid URL for the repository.');
        markFieldAsInvalid(repoField);
    }
    
    if (errors.length > 0) {
        showAlert('Please fix the following errors:\n• ' + errors.join('\n• '), 'danger');
        return false;
    }
    
    return true;
}

/**
 * Initialize project card animations
 */
function initializeProjectAnimations() {
    const projectCards = document.querySelectorAll('.project-card');
    
    // Intersection Observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('animate-in');
                    }, index * 100); // Staggered animation
                }
            });
        }, {
            threshold: 0.1
        });
        
        projectCards.forEach(card => {
            observer.observe(card);
        });
    }
    
    // Hover effects for project links
    const projectLinks = document.querySelectorAll('.project-link');
    projectLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Initialize project search functionality
 */
function initializeProjectSearch() {
    const searchInput = document.getElementById('project-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const projectCards = document.querySelectorAll('.project-card');
        
        projectCards.forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const description = card.querySelector('.card-text').textContent.toLowerCase();
            const technologies = Array.from(card.querySelectorAll('.tech-tag')).map(tag => tag.textContent.toLowerCase());
            
            const matches = title.includes(searchTerm) || 
                          description.includes(searchTerm) || 
                          technologies.some(tech => tech.includes(searchTerm));
            
            if (matches) {
                card.style.display = 'block';
                highlightSearchTerm(card, searchTerm);
            } else {
                card.style.display = 'none';
            }
        });
        
        updateFilterCounts();
    });
}

/**
 * Highlight search terms in project cards
 */
function highlightSearchTerm(card, searchTerm) {
    if (!searchTerm) return;
    
    const textElements = card.querySelectorAll('.card-title, .card-text');
    textElements.forEach(element => {
        const text = element.textContent;
        const highlightedText = text.replace(
            new RegExp(`(${searchTerm})`, 'gi'),
            '<mark>$1</mark>'
        );
        element.innerHTML = highlightedText;
    });
}

/**
 * Validate URL format
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
 * Mark field as invalid
 */
function markFieldAsInvalid(field) {
    field.classList.remove('is-valid');
    field.classList.add('is-invalid');
}

/**
 * Mark field as valid
 */
function markFieldAsValid(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const existingAlert = document.querySelector('.dynamic-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show dynamic-alert" role="alert">
            <i class="bi bi-${getAlertIcon(type)} me-2"></i>
            ${message.replace(/\n/g, '<br>')}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.querySelector('.container') || document.querySelector('main') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
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
window.ProjectsApp = {
    generateSlug,
    showAlert,
    filterProjects,
    updateFilterCounts,
    initializeProjectSearch
};

/**
 * Initialize project detail page functionality
 * Handles milestone toggles and task status updates
 */
function initializeProjectDetailFunctionality() {
    initializeMilestoneToggles();
    initializeTaskStatusUpdates();
}

/**
 * Initialize milestone completion toggle functionality
 */
function initializeMilestoneToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-milestone');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const milestoneId = this.dataset.milestoneId;
            const projectId = this.dataset.projectId;
            
            if (!milestoneId || !projectId) {
                console.error('Missing milestone or project ID');
                return;
            }
            
            const url = `/projects/${projectId}/milestones/${milestoneId}/toggle-complete/`;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    showAlert('Error updating milestone status', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error updating milestone status', 'danger');
            });
        });
    });
}

/**
 * Initialize task status update functionality
 */
function initializeTaskStatusUpdates() {
    const updateButtons = document.querySelectorAll('.update-task-status');
    
    updateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const projectId = this.dataset.projectId;
            const status = this.dataset.status;
            
            if (!taskId || !projectId || !status) {
                console.error('Missing task, project ID, or status');
                return;
            }
            
            const url = `/projects/${projectId}/tasks/${taskId}/update-status/`;
            
            const formData = new FormData();
            formData.append('status', status);
            formData.append('csrfmiddlewaretoken', getCsrfToken());
            
            fetch(url, {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    showAlert('Error updating task status', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error updating task status', 'danger');
            });
        });
    });
}

/**
 * Get CSRF token from the page
 */
function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Initialize project detail functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a project detail page
    if (document.querySelector('.toggle-milestone') || document.querySelector('.update-task-status')) {
        initializeProjectDetailFunctionality();
    }
});
