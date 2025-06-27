// Main JavaScript for Attendance Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips (only on non-touch devices)
    if (!('ontouchstart' in window)) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Mobile-specific improvements
    if (window.innerWidth <= 768) {
        // Auto-collapse navbar after clicking a link on mobile
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });

        // Prevent zoom on input focus for iOS
        const inputs = document.querySelectorAll('input[type="number"], input[type="text"], input[type="email"], textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (input.style.fontSize !== '16px') {
                    input.style.fontSize = '16px';
                }
            });
        });
    }

    // Touch-friendly number inputs
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        // Add touch-friendly increment/decrement buttons
        const wrapper = document.createElement('div');
        wrapper.className = 'input-group';

        const decrementBtn = document.createElement('button');
        decrementBtn.className = 'btn btn-outline-secondary';
        decrementBtn.type = 'button';
        decrementBtn.innerHTML = '<i class="fas fa-minus"></i>';
        decrementBtn.addEventListener('click', () => {
            const currentValue = parseInt(input.value) || 0;
            if (currentValue > 0) {
                input.value = currentValue - 1;
                input.dispatchEvent(new Event('input'));
            }
        });

        const incrementBtn = document.createElement('button');
        incrementBtn.className = 'btn btn-outline-secondary';
        incrementBtn.type = 'button';
        incrementBtn.innerHTML = '<i class="fas fa-plus"></i>';
        incrementBtn.addEventListener('click', () => {
            const currentValue = parseInt(input.value) || 0;
            input.value = currentValue + 1;
            input.dispatchEvent(new Event('input'));
        });

        // Only add buttons on mobile devices
        if (window.innerWidth <= 768) {
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(decrementBtn);
            wrapper.appendChild(input);
            wrapper.appendChild(incrementBtn);
        }
    });
});

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Attendance calculation helpers
function calculateTotal(men, women, children) {
    return (parseInt(men) || 0) + (parseInt(women) || 0) + (parseInt(children) || 0);
}

function updateAttendanceTotal() {
    const menInput = document.getElementById('men_count');
    const womenInput = document.getElementById('women_count');
    const childrenInput = document.getElementById('children_count');
    const totalDisplay = document.getElementById('total-count');
    
    if (menInput && womenInput && childrenInput && totalDisplay) {
        const total = calculateTotal(menInput.value, womenInput.value, childrenInput.value);
        totalDisplay.textContent = total;
        
        // Add visual feedback for the total
        totalDisplay.className = total > 0 ? 'fw-bold text-success' : 'text-muted';
    }
}

// Export functionality
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    const csvRows = data.map(row => 
        headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        }).join(',')
    );
    
    return [csvHeaders, ...csvRows].join('\n');
}

// Loading state management
function showLoading(element) {
    const loadingHtml = `
        <div class="loading-overlay">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    element.style.position = 'relative';
    element.insertAdjacentHTML('beforeend', loadingHtml);
}

function hideLoading(element) {
    const loadingOverlay = element.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// API helpers
async function fetchMeetingStats(meetingId) {
    try {
        const response = await fetch(`/api/meetings/${meetingId}/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        return await response.json();
    } catch (error) {
        console.error('Error fetching meeting stats:', error);
        return null;
    }
}

// Form helpers
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
}

function validateAttendanceForm() {
    const men = parseInt(document.getElementById('men_count')?.value) || 0;
    const women = parseInt(document.getElementById('women_count')?.value) || 0;
    const children = parseInt(document.getElementById('children_count')?.value) || 0;
    
    const total = men + women + children;
    
    if (total === 0) {
        alert('Please enter at least one person in attendance.');
        return false;
    }
    
    return true;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + N for new meeting
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        window.location.href = '/meeting/new';
    }
    
    // Ctrl/Cmd + H for home
    if ((event.ctrlKey || event.metaKey) && event.key === 'h') {
        event.preventDefault();
        window.location.href = '/';
    }
});

// Auto-save functionality (for future enhancement)
function enableAutoSave(formId, saveEndpoint) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('change', debounce(() => {
            // Auto-save logic would go here
            console.log('Auto-saving form data...');
        }, 1000));
    });
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
