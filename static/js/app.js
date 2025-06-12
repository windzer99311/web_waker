// Main JavaScript functionality for the Uptime Monitor application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation for URL inputs
    const urlInputs = document.querySelectorAll('input[type="url"]');
    urlInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateUrl(this);
        });
    });
    
    // Add protocol to URLs if missing
    urlInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            let url = this.value.trim();
            if (url && !url.match(/^https?:\/\//)) {
                this.value = 'https://' + url;
            }
        });
    });
    
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            validateFileUpload(this);
        });
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-bs-target*="deleteModal"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Additional confirmation could be added here
        });
    });
    
    // Real-time status updates (if on dashboard)
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        initializeStatusUpdates();
    }
});

/**
 * Validate URL format
 */
function validateUrl(input) {
    const url = input.value.trim();
    const urlPattern = /^https?:\/\/.+/;
    
    if (url && !urlPattern.test(url)) {
        input.classList.add('is-invalid');
        showFieldError(input, 'Please enter a valid URL starting with http:// or https://');
    } else {
        input.classList.remove('is-invalid');
        hideFieldError(input);
    }
}

/**
 * Validate file upload
 */
function validateFileUpload(input) {
    const file = input.files[0];
    
    if (file) {
        if (!file.name.endsWith('.txt')) {
            input.classList.add('is-invalid');
            showFieldError(input, 'Please select a .txt file');
            return false;
        }
        
        if (file.size > 1024 * 1024) { // 1MB limit
            input.classList.add('is-invalid');
            showFieldError(input, 'File size must be less than 1MB');
            return false;
        }
        
        input.classList.remove('is-invalid');
        hideFieldError(input);
    }
    
    return true;
}

/**
 * Show field error message
 */
function showFieldError(input, message) {
    // Remove existing error message
    hideFieldError(input);
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-error-for', input.id || input.name);
    
    // Insert after input
    input.parentNode.insertBefore(errorDiv, input.nextSibling);
}

/**
 * Hide field error message
 */
function hideFieldError(input) {
    const errorElement = input.parentNode.querySelector(`[data-error-for="${input.id || input.name}"]`);
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Initialize status updates for dashboard
 */
function initializeStatusUpdates() {
    // Add smooth transitions for status changes
    const statusBadges = document.querySelectorAll('.badge');
    statusBadges.forEach(function(badge) {
        badge.style.transition = 'all 0.3s ease';
    });
    
    // Add progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        // Animate progress bar on load
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });
}

/**
 * Format response time for display
 */
function formatResponseTime(seconds) {
    if (seconds < 1) {
        return Math.round(seconds * 1000) + 'ms';
    } else {
        return seconds.toFixed(2) + 's';
    }
}

/**
 * Format uptime percentage
 */
function formatUptimePercentage(percentage) {
    if (percentage >= 99) {
        return 'text-success';
    } else if (percentage >= 95) {
        return 'text-warning';
    } else {
        return 'text-danger';
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Refresh page data without full reload
 */
function refreshData() {
    // Simple page reload for now - could be enhanced with AJAX
    window.location.reload();
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send error reports to server here
});

// Handle form submissions with loading states
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.tagName === 'FORM') {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            
            // Re-enable button after 3 seconds (fallback)
            setTimeout(function() {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 3000);
        }
    }
});
