// Main JavaScript for FA Recommendation System

// Global variables
let loadingOverlay;
let notifications = [];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Get loading overlay reference
    loadingOverlay = document.getElementById('loading-overlay');
    
    // Initialize components
    initializeAnimations();
    initializeFormValidation();
    initializeTooltips();
    initializeModals();
    initializeCharts();
    
    // Add event listeners
    addGlobalEventListeners();
    
    // Check for saved preferences
    loadUserPreferences();
    
    console.log('FA Recommendation System initialized successfully');
}

/**
 * Initialize animations and scroll effects
 */
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                // Add animation classes based on data attributes
                if (element.dataset.animation) {
                    element.classList.add(element.dataset.animation);
                } else {
                    element.classList.add('fade-in-up');
                }
                
                // Stop observing this element
                animationObserver.unobserve(element);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe elements with animation classes
    document.querySelectorAll('.card, .stat-card, .analysis-item, .assessment-card').forEach(el => {
        animationObserver.observe(el);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Add validation to all forms
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
                event.stopPropagation();
                showNotification('Please fill in all required fields correctly', 'error');
            } else {
                // Show loading for valid forms
                showLoading('Processing your request...');
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let message = '';
    
    // Check required fields
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        message = 'This field is required';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }
    }
    
    // Password validation
    if (field.type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            message = 'Password must be at least 6 characters long';
        }
    }
    
    // Number validation
    if (field.type === 'number' && value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        
        if (min && parseInt(value) < parseInt(min)) {
            isValid = false;
            message = `Value must be at least ${min}`;
        }
        
        if (max && parseInt(value) > parseInt(max)) {
            isValid = false;
            message = `Value must be no more than ${max}`;
        }
    }
    
    // Update field appearance
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        removeFieldError(field);
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, message);
    }
    
    return isValid;
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isFormValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });
    
    // Special validation for radio button groups
    const radioGroups = {};
    form.querySelectorAll('input[type="radio"][required]').forEach(radio => {
        const groupName = radio.name;
        if (!radioGroups[groupName]) {
            radioGroups[groupName] = [];
        }
        radioGroups[groupName].push(radio);
    });
    
    Object.keys(radioGroups).forEach(groupName => {
        const group = radioGroups[groupName];
        const isGroupValid = group.some(radio => radio.checked);
        
        if (!isGroupValid) {
            isFormValid = false;
            group.forEach(radio => {
                radio.classList.add('is-invalid');
            });
            showFieldError(group[0], 'Please select an option');
        } else {
            group.forEach(radio => {
                radio.classList.remove('is-invalid');
            });
        }
    });
    
    return isFormValid;
}

/**
 * Show field error message
 */
function showFieldError(field, message) {
    removeFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.dataset.fieldError = field.name || field.id;
    
    if (field.type === 'radio') {
        const radioContainer = field.closest('.form-check') || field.parentElement;
        radioContainer.appendChild(errorDiv);
    } else {
        field.parentElement.appendChild(errorDiv);
    }
}

/**
 * Remove field error message
 */
function removeFieldError(field) {
    const existing = document.querySelector(`[data-field-error="${field.name || field.id}"]`);
    if (existing) {
        existing.remove();
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add custom tooltips for form fields
    const helpIcons = document.querySelectorAll('.help-icon');
    helpIcons.forEach(icon => {
        const tooltip = new bootstrap.Tooltip(icon, {
            placement: 'right',
            trigger: 'hover focus'
        });
    });
}

/**
 * Initialize modals
 */
function initializeModals() {
    // Add modal event listeners
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            // Focus first input when modal opens
            const firstInput = this.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            // Clear form validation when modal closes
            const form = this.querySelector('form');
            if (form) {
                form.classList.remove('was-validated');
                form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
                    el.classList.remove('is-invalid', 'is-valid');
                });
                form.querySelectorAll('.invalid-feedback').forEach(el => {
                    el.remove();
                });
            }
        });
    });
}

/**
 * Initialize charts and data visualizations
 */
function initializeCharts() {
    // Set default Chart.js configuration
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6c757d';
        
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
        
        Chart.defaults.elements.arc.borderWidth = 0;
        Chart.defaults.elements.arc.hoverBorderWidth = 3;
        
        Chart.defaults.elements.bar.borderRadius = 4;
        Chart.defaults.elements.bar.borderSkipped = false;
    }
}

/**
 * Add global event listeners
 */
function addGlobalEventListeners() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Auto-hide alerts
    document.querySelectorAll('.alert').forEach(alert => {
        if (alert.classList.contains('alert-dismissible')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            createRipple(e, this);
        });
    });
    
    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Escape key closes modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
        
        // Enter key submits forms (when focused on submit button)
        if (e.key === 'Enter' && e.target.type === 'submit') {
            e.target.click();
        }
    });
}

/**
 * Create ripple effect on button click
 */
function createRipple(event, element) {
    const circle = document.createElement('span');
    const diameter = Math.max(element.clientWidth, element.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - element.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - element.offsetTop - radius}px`;
    circle.classList.add('ripple');
    
    const ripple = element.getElementsByClassName('ripple')[0];
    if (ripple) {
        ripple.remove();
    }
    
    element.appendChild(circle);
    
    // Remove ripple after animation
    setTimeout(() => {
        circle.remove();
    }, 600);
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    if (loadingOverlay) {
        const loadingText = loadingOverlay.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
        loadingOverlay.classList.remove('d-none');
    }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.classList.add('d-none');
    }
}

/**
 * Show notification/toast
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = createNotificationElement(message, type);
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
    
    // Track notifications
    notifications.push(notification);
    
    return notification;
}

/**
 * Create notification element
 */
function createNotificationElement(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        max-width: 500px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    `;
    
    const icon = getIconForType(type);
    
    notification.innerHTML = `
        <i class="fas fa-${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add close functionality
    notification.querySelector('.btn-close').addEventListener('click', () => {
        removeNotification(notification);
    });
    
    return notification;
}

/**
 * Get icon for notification type
 */
function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle',
        primary: 'info-circle'
    };
    return icons[type] || icons.info;
}

/**
 * Remove notification
 */
function removeNotification(notification) {
    notification.classList.remove('show');
    notification.classList.add('fade');
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.parentElement.removeChild(notification);
        }
        
        // Remove from tracking array
        const index = notifications.indexOf(notification);
        if (index > -1) {
            notifications.splice(index, 1);
        }
    }, 150);
}

/**
 * Load user preferences from localStorage
 */
function loadUserPreferences() {
    // Note: localStorage is not available in Claude artifacts
    // This is a placeholder for when the code is used in a real environment
    
    try {
        const preferences = JSON.parse(localStorage.getItem('faSystemPreferences') || '{}');
        
        // Apply theme
        if (preferences.theme) {
            document.body.classList.add(`theme-${preferences.theme}`);
        }
        
        // Apply accessibility preferences
        if (preferences.highContrast) {
            document.body.classList.add('high-contrast');
        }
        
        if (preferences.largeText) {
            document.body.classList.add('large-text');
        }
        
    } catch (error) {
        console.log('No saved preferences found');
    }
}

/**
 * Save user preferences to localStorage
 */
function saveUserPreferences(preferences) {
    try {
        const currentPrefs = JSON.parse(localStorage.getItem('faSystemPreferences') || '{}');
        const updatedPrefs = { ...currentPrefs, ...preferences };
        localStorage.setItem('faSystemPreferences', JSON.stringify(updatedPrefs));
        
        showNotification('Preferences saved successfully', 'success');
    } catch (error) {
        console.error('Failed to save preferences:', error);
        showNotification('Failed to save preferences', 'error');
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Date(dateString).toLocaleDateString('en-US', options);
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Throttle function for scroll events
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success', 2000);
        return true;
    } catch (err) {
        console.error('Failed to copy text: ', err);
        
        // Fallback method
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (successful) {
                showNotification('Copied to clipboard!', 'success', 2000);
                return true;
            } else {
                showNotification('Failed to copy text', 'error');
                return false;
            }
        } catch (err) {
            document.body.removeChild(textArea);
            showNotification('Failed to copy text', 'error');
            return false;
        }
    }
}

/**
 * Download data as file
 */
function downloadAsFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Validate file upload
 */
function validateFile(file, options = {}) {
    const {
        maxSize = 5 * 1024 * 1024, // 5MB default
        allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'text/csv'],
        maxFiles = 1
    } = options;
    
    const errors = [];
    
    if (file.size > maxSize) {
        errors.push(`File size must be less than ${formatFileSize(maxSize)}`);
    }
    
    if (!allowedTypes.includes(file.type)) {
        errors.push(`File type ${file.type} is not allowed`);
    }
    
    return {
        valid: errors.length === 0,
        errors
    };
}

/**
 * Handle API requests with proper error handling
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        ...options
    };
    
    try {
        showLoading('Processing request...');
        
        const response = await fetch(url, defaultOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        hideLoading();
        
        return {
            success: true,
            data
        };
        
    } catch (error) {
        hideLoading();
        console.error('API request failed:', error);
        
        showNotification(
            error.message || 'An error occurred while processing your request',
            'error'
        );
        
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Chart utilities for data visualization
 */
const ChartUtils = {
    /**
     * Generate colors for charts
     */
    generateColors(count) {
        const colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
            '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        
        return result;
    },
    
    /**
     * Create gradient for charts
     */
    createGradient(ctx, color1, color2) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    },
    
    /**
     * Default chart options
     */
    getDefaultOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#667eea',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        };
    }
};

/**
 * Form utilities
 */
const FormUtils = {
    /**
     * Serialize form data to object
     */
    serializeForm(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    },
    
    /**
     * Reset form with animation
     */
    resetForm(form, animate = true) {
        if (animate) {
            form.style.opacity = '0.5';
            form.style.transform = 'scale(0.98)';
        }
        
        setTimeout(() => {
            form.reset();
            form.classList.remove('was-validated');
            
            // Remove validation classes
            form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
                el.classList.remove('is-valid', 'is-invalid');
            });
            
            // Remove error messages
            form.querySelectorAll('.invalid-feedback').forEach(el => {
                el.remove();
            });
            
            if (animate) {
                form.style.opacity = '1';
                form.style.transform = 'scale(1)';
            }
        }, animate ? 200 : 0);
    },
    
    /**
     * Auto-save form data
     */
    enableAutoSave(form, key, interval = 30000) {
        const saveData = () => {
            const data = this.serializeForm(form);
            try {
                localStorage.setItem(key, JSON.stringify(data));
                console.log('Form data auto-saved');
            } catch (error) {
                console.error('Failed to auto-save form data:', error);
            }
        };
        
        // Save on input changes (debounced)
        const debouncedSave = debounce(saveData, 5000);
        form.addEventListener('input', debouncedSave);
        
        // Save periodically
        const intervalId = setInterval(saveData, interval);
        
        // Return cleanup function
        return () => {
            clearInterval(intervalId);
            form.removeEventListener('input', debouncedSave);
        };
    },
    
    /**
     * Restore form data from auto-save
     */
    restoreAutoSave(form, key) {
        try {
            const savedData = localStorage.getItem(key);
            if (savedData) {
                const data = JSON.parse(savedData);
                
                Object.keys(data).forEach(fieldName => {
                    const field = form.querySelector(`[name="${fieldName}"]`);
                    if (field) {
                        if (field.type === 'checkbox' || field.type === 'radio') {
                            const value = Array.isArray(data[fieldName]) ? data[fieldName] : [data[fieldName]];
                            value.forEach(val => {
                                const specificField = form.querySelector(`[name="${fieldName}"][value="${val}"]`);
                                if (specificField) {
                                    specificField.checked = true;
                                }
                            });
                        } else {
                            field.value = data[fieldName];
                        }
                    }
                });
                
                showNotification('Previous form data restored', 'info', 3000);
                return true;
            }
        } catch (error) {
            console.error('Failed to restore form data:', error);
        }
        
        return false;
    }
};

/**
 * Performance monitoring
 */
const Performance = {
    markers: {},
    
    mark(name) {
        this.markers[name] = performance.now();
    },
    
    measure(name, startMark) {
        const endTime = performance.now();
        const startTime = this.markers[startMark];
        
        if (startTime) {
            const duration = endTime - startTime;
            console.log(`${name}: ${duration.toFixed(2)}ms`);
            return duration;
        }
        
        return null;
    }
};

/**
 * Accessibility utilities
 */
const A11y = {
    /**
     * Announce text to screen readers
     */
    announce(message, priority = 'polite') {
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', priority);
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.textContent = message;
        
        document.body.appendChild(announcer);
        
        setTimeout(() => {
            document.body.removeChild(announcer);
        }, 1000);
    },
    
    /**
     * Manage focus for better keyboard navigation
     */
    manageFocus: {
        stack: [],
        
        push(element) {
            this.stack.push(document.activeElement);
            element.focus();
        },
        
        pop() {
            const element = this.stack.pop();
            if (element) {
                element.focus();
            }
        }
    },
    
    /**
     * Check if user prefers reduced motion
     */
    prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }
};

// CSS for ripple effect and other animations
const additionalCSS = `
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.btn {
    position: relative;
    overflow: hidden;
}

.sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}

.high-contrast {
    filter: contrast(150%);
}

.large-text {
    font-size: 1.2em !important;
}

@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
`;

// Inject additional CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);

// Export utilities for use in other files
window.FASystem = {
    showLoading,
    hideLoading,
    showNotification,
    apiRequest,
    ChartUtils,
    FormUtils,
    Performance,
    A11y,
    copyToClipboard,
    downloadAsFile,
    validateFile,
    formatFileSize,
    formatDate,
    debounce,
    throttle
};

console.log('FA Recommendation System utilities loaded');