// Custom JavaScript for Escola Morvan Figueiredo Acquisition System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
            alertInstance.close();
        }, 5000);
    });

    // File upload preview and validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            const maxSize = 16 * 1024 * 1024; // 16MB
            const allowedTypes = ['application/pdf', 'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel', 
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'image/png', 'image/jpeg', 'image/jpg'];
            
            let validFiles = [];
            let errors = [];
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                
                // Check file size
                if (file.size > maxSize) {
                    errors.push(`${file.name}: Arquivo muito grande (máx. 16MB)`);
                    continue;
                }
                
                // Check file type
                if (!allowedTypes.includes(file.type)) {
                    errors.push(`${file.name}: Tipo de arquivo não permitido`);
                    continue;
                }
                
                validFiles.push(file);
            }
            
            // Show errors if any
            if (errors.length > 0) {
                showAlert('Erro nos arquivos selecionados:\n' + errors.join('\n'), 'danger');
            }
            
            // Update file input label
            updateFileInputLabel(input, validFiles);
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 'Tem certeza que deseja excluir?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Initial resize
        textarea.style.height = (textarea.scrollHeight) + 'px';
    });

    // Search form enhancements
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="text"]');
        if (searchInput) {
            // Add search icon
            const searchIcon = document.createElement('i');
            searchIcon.className = 'fas fa-search position-absolute';
            searchIcon.style.right = '10px';
            searchIcon.style.top = '50%';
            searchIcon.style.transform = 'translateY(-50%)';
            searchIcon.style.pointerEvents = 'none';
            
            const inputGroup = searchInput.parentElement;
            inputGroup.style.position = 'relative';
            inputGroup.appendChild(searchIcon);
            
            searchInput.style.paddingRight = '30px';
        }
    }

    // Status filter change handler
    const statusFilter = document.querySelector('select[name="status_filter"]');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            // Auto-submit form when status changes
            this.form.submit();
        });
    }

    // Responsible filter change handler
    const responsibleFilter = document.querySelector('select[name="responsible_filter"]');
    if (responsibleFilter) {
        responsibleFilter.addEventListener('change', function() {
            // Auto-submit form when responsible changes
            this.form.submit();
        });
    }

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });

    // Dashboard statistics animations
    animateStatNumbers();

    // Request status color coding
    applyStatusColors();

    // Initialize drag and drop for file uploads
    initializeDragAndDrop();
});

// Helper function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message.replace(/\n/g, '<br>')}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
        alertInstance.close();
    }, 5000);
}

// Helper function to update file input label
function updateFileInputLabel(input, files) {
    const label = input.nextElementSibling;
    if (label && label.tagName === 'LABEL') {
        if (files.length === 0) {
            label.textContent = 'Escolher arquivos...';
        } else if (files.length === 1) {
            label.textContent = files[0].name;
        } else {
            label.textContent = `${files.length} arquivos selecionados`;
        }
    }
}

// Animate statistics numbers
function animateStatNumbers() {
    const statNumbers = document.querySelectorAll('.stats-number, .text-primary, .text-info, .text-success');
    statNumbers.forEach(function(element) {
        const text = element.textContent.trim();
        const number = parseInt(text);
        
        if (!isNaN(number) && number > 0) {
            element.textContent = '0';
            
            const increment = number / 30; // 30 frames
            let current = 0;
            
            const timer = setInterval(function() {
                current += increment;
                if (current >= number) {
                    element.textContent = number;
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current);
                }
            }, 50);
        }
    });
}

// Apply status-specific colors
function applyStatusColors() {
    const statusBadges = document.querySelectorAll('.badge');
    statusBadges.forEach(function(badge) {
        const text = badge.textContent.toLowerCase();
        if (text.includes('orçamento')) {
            badge.classList.add('status-orcamento');
        } else if (text.includes('compra')) {
            badge.classList.add('status-fase-compra');
        } else if (text.includes('caminho')) {
            badge.classList.add('status-a-caminho');
        } else if (text.includes('finalizado')) {
            badge.classList.add('status-finalizado');
        }
    });
}

// Initialize drag and drop for file uploads
function initializeDragAndDrop() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        const container = input.closest('.mb-3') || input.parentElement;
        
        // Add drag and drop events
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        container.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        container.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            input.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        });
    });
}

// Form validation enhancements
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Auto-save draft functionality (localStorage)
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(function(form) {
        const formId = form.getAttribute('data-autosave');
        const inputs = form.querySelectorAll('input, textarea, select');
        
        // Load saved data
        const savedData = localStorage.getItem(`draft_${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            inputs.forEach(function(input) {
                if (data[input.name]) {
                    input.value = data[input.name];
                }
            });
        }
        
        // Save data on input
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                const data = {};
                inputs.forEach(function(inp) {
                    data[inp.name] = inp.value;
                });
                localStorage.setItem(`draft_${formId}`, JSON.stringify(data));
            });
        });
        
        // Clear draft on submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`draft_${formId}`);
        });
    });
}

// Initialize auto-save on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeAutoSave();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+N for new request
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        const newRequestLink = document.querySelector('a[href*="request/new"]');
        if (newRequestLink) {
            window.location.href = newRequestLink.href;
        }
    }
    
    // Ctrl+D for dashboard
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        const dashboardLink = document.querySelector('a[href*="dashboard"]');
        if (dashboardLink) {
            window.location.href = dashboardLink.href;
        }
    }
    
    // Escape to close modals/alerts
    if (e.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
            alertInstance.close();
        });
    }
});

// Print functionality
function printPage() {
    window.print();
}

// Export functionality (basic CSV export)
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Mobile menu enhancement
function initializeMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// Initialize mobile menu on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeMobileMenu();
});
