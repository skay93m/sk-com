/**
 * MCQ App JavaScript
 * Handles quiz interactions, form validations, and topic management
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeMCQFunctionality();
});

/**
 * Initialize all MCQ-related functionality
 */
function initializeMCQFunctionality() {
    // Initialize topic selection functionality
    initializeTopicSelection();
    
    // Initialize quiz form functionality
    initializeQuizForm();
    
    // Initialize MCQ creation/editing forms
    initializeMCQForm();
    
    // Initialize topic management
    initializeTopicManagement();
    
    // Initialize question answering
    initializeQuestionAnswering();
    
    // Initialize dynamic topic badge colors
    initializeDynamicTopicColors();
}

/**
 * Initialize topic selection functionality
 */
function initializeTopicSelection() {
    const selectAllBtn = document.getElementById('select-all');
    const clearAllBtn = document.getElementById('clear-all');
    const checkboxes = document.querySelectorAll('input[name="topics"]');
    
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            checkboxes.forEach(cb => cb.checked = true);
            updateSelectionCount();
        });
    }
    
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function() {
            checkboxes.forEach(cb => cb.checked = false);
            updateSelectionCount();
        });
    }
    
    // Add change listeners to individual checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionCount);
    });
    
    // Initial count update
    updateSelectionCount();
}

/**
 * Update the selection count display
 */
function updateSelectionCount() {
    const checkboxes = document.querySelectorAll('input[name="topics"]:checked');
    const countDisplay = document.getElementById('selection-count');
    
    if (countDisplay) {
        countDisplay.textContent = `${checkboxes.length} topic(s) selected`;
    }
}

/**
 * Initialize quiz form functionality
 */
function initializeQuizForm() {
    const quizForm = document.getElementById('quiz-form');
    if (!quizForm) return;
    
    quizForm.addEventListener('submit', function(e) {
        const selectedTopics = document.querySelectorAll('input[name="topics"]:checked');
        
        if (selectedTopics.length === 0) {
            e.preventDefault();
            showAlert('Please select at least one topic to start the quiz.', 'warning');
            return false;
        }
        
        // Show loading state
        const submitBtn = quizForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Generating Quiz...';
            
            // Re-enable after timeout
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 10000);
        }
    });
}

/**
 * Initialize MCQ creation/editing form functionality
 */
function initializeMCQForm() {
    const mcqForm = document.getElementById('mcq-form');
    if (!mcqForm) return;
    
    // Add option functionality
    initializeOptionManagement();
    
    // Form validation
    mcqForm.addEventListener('submit', function(e) {
        if (!validateMCQForm()) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        const submitBtn = mcqForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Saving...';
            
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 10000);
        }
    });
}

/**
 * Initialize option management for MCQ forms
 */
function initializeOptionManagement() {
    const addOptionBtn = document.getElementById('add-option');
    const optionsContainer = document.getElementById('options-container');
    
    if (addOptionBtn && optionsContainer) {
        addOptionBtn.addEventListener('click', function() {
            addNewOption();
        });
        
        // Add remove functionality to existing options
        updateOptionRemoveButtons();
    }
}

/**
 * Add a new option to the MCQ form
 */
function addNewOption() {
    const optionsContainer = document.getElementById('options-container');
    if (!optionsContainer) return;
    
    const optionCount = optionsContainer.children.length;
    const maxOptions = 6; // Reasonable limit
    
    if (optionCount >= maxOptions) {
        showAlert(`Maximum ${maxOptions} options allowed.`, 'warning');
        return;
    }
    
    const optionHtml = `
        <div class="option-group mb-3">
            <div class="input-group">
                <div class="input-group-text">
                    <input type="radio" name="correct_option" value="${optionCount}" class="form-check-input">
                </div>
                <input type="text" name="option_${optionCount}" class="form-control" placeholder="Enter option ${optionCount + 1}" required>
                <button type="button" class="btn btn-outline-danger remove-option">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    optionsContainer.insertAdjacentHTML('beforeend', optionHtml);
    updateOptionRemoveButtons();
}

/**
 * Update remove button functionality for options
 */
function updateOptionRemoveButtons() {
    const removeButtons = document.querySelectorAll('.remove-option');
    
    removeButtons.forEach(button => {
        button.onclick = function() {
            const optionGroup = this.closest('.option-group');
            if (optionGroup) {
                optionGroup.remove();
                updateOptionNumbers();
            }
        };
    });
}

/**
 * Update option numbers after removal
 */
function updateOptionNumbers() {
    const optionGroups = document.querySelectorAll('.option-group');
    
    optionGroups.forEach((group, index) => {
        const input = group.querySelector('input[type="text"]');
        const radio = group.querySelector('input[type="radio"]');
        
        if (input) {
            input.name = `option_${index}`;
            input.placeholder = `Enter option ${index + 1}`;
        }
        
        if (radio) {
            radio.value = index;
        }
    });
}

/**
 * Validate MCQ form
 */
function validateMCQForm() {
    const errors = [];
    
    // Check question text
    const questionText = document.getElementById('id_question');
    if (questionText && !questionText.value.trim()) {
        errors.push('Question text is required.');
    }
    
    // Check options
    const options = document.querySelectorAll('input[name^="option_"]');
    const filledOptions = Array.from(options).filter(opt => opt.value.trim());
    
    if (filledOptions.length < 2) {
        errors.push('At least 2 options are required.');
    }
    
    // Check correct answer selection
    const correctOption = document.querySelector('input[name="correct_option"]:checked');
    if (!correctOption) {
        errors.push('Please select the correct answer.');
    }
    
    // Check topic selection
    const topicSelect = document.getElementById('id_topic');
    if (topicSelect && !topicSelect.value) {
        errors.push('Please select a topic.');
    }
    
    if (errors.length > 0) {
        showAlert('Please fix the following errors:\n• ' + errors.join('\n• '), 'danger');
        return false;
    }
    
    return true;
}

/**
 * Initialize topic management functionality
 */
function initializeTopicManagement() {
    const topicForm = document.getElementById('topic-form');
    if (!topicForm) return;
    
    // Color picker functionality
    const colorPicker = document.getElementById('id_color');
    const colorPreview = document.getElementById('color-preview');
    
    if (colorPicker && colorPreview) {
        colorPicker.addEventListener('input', function() {
            colorPreview.style.backgroundColor = this.value;
        });
        
        // Initialize preview
        colorPreview.style.backgroundColor = colorPicker.value;
    }
    
    // Form validation
    topicForm.addEventListener('submit', function(e) {
        const topicName = document.getElementById('id_name');
        
        if (topicName && !topicName.value.trim()) {
            e.preventDefault();
            showAlert('Topic name is required.', 'danger');
            return false;
        }
    });
}

/**
 * Initialize question answering functionality
 */
function initializeQuestionAnswering() {
    const questionForm = document.getElementById('question-form');
    if (!questionForm) return;
    
    const answerOptions = document.querySelectorAll('input[name="selected_answer"]');
    
    answerOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Visual feedback for selection
            const allLabels = document.querySelectorAll('.answer-option');
            allLabels.forEach(label => label.classList.remove('selected'));
            
            const selectedLabel = this.closest('.answer-option');
            if (selectedLabel) {
                selectedLabel.classList.add('selected');
            }
        });
    });
    
    // Auto-submit functionality (optional)
    const autoSubmit = document.getElementById('auto-submit');
    if (autoSubmit && autoSubmit.checked) {
        answerOptions.forEach(option => {
            option.addEventListener('change', function() {
                setTimeout(() => {
                    questionForm.submit();
                }, 500); // Small delay for visual feedback
            });
        });
    }
}

/**
 * Utility function to show alerts
 */
function showAlert(message, type = 'info') {
    // Remove existing alerts
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
    
    // Insert at top of main content
    const mainContent = document.querySelector('.container') || document.querySelector('main') || document.body;
    mainContent.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-dismiss info and success alerts
    if (type === 'info' || type === 'success') {
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

/**
 * Initialize quiz timer functionality
 */
function initializeQuizTimer() {
    const timerElement = document.getElementById('quiz-timer');
    if (!timerElement) return;
    
    const duration = parseInt(timerElement.dataset.duration) || 300; // 5 minutes default
    let timeRemaining = duration;
    
    const timer = setInterval(() => {
        timeRemaining--;
        
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Warning when less than 1 minute
        if (timeRemaining <= 60) {
            timerElement.classList.add('text-danger');
        }
        
        // Auto-submit when time is up
        if (timeRemaining <= 0) {
            clearInterval(timer);
            const form = document.getElementById('question-form') || document.getElementById('quiz-form');
            if (form) {
                form.submit();
            }
        }
    }, 1000);
}

/**
 * Initialize dynamic topic badge colors
 */
function initializeDynamicTopicColors() {
    const topicBadges = document.querySelectorAll('.topic-badge-dynamic');
    
    topicBadges.forEach(badge => {
        const color = badge.dataset.topicColor;
        if (color) {
            badge.style.backgroundColor = color;
        }
    });
}

// Export functions for external use
window.MCQApp = {
    showAlert,
    updateSelectionCount,
    addNewOption,
    initializeQuizTimer
};

// Additional form styling for edit MCQ
document.addEventListener('DOMContentLoaded', function() {
    // Add classes to form fields
    const formControls = document.querySelectorAll('input[type="text"], textarea, select');
    formControls.forEach(function(control) {
        control.classList.add('form-control');
    });
    
    // Add classes to checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.classList.add('form-check-input');
    });
    
    // Smooth scroll on form submission
    const mcqForm = document.getElementById('mcq-form');
    if (mcqForm) {
        mcqForm.addEventListener('submit', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // Print functionality
    const printBtn = document.querySelector('.print-list-btn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
});