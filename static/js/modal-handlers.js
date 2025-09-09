/* Modal Handlers - Specialized modal window functionality */

// Enhanced keyboard shortcuts handler
function handleKeyboardShortcuts(event) {
    if (event.ctrlKey || event.metaKey) {
        switch(event.key.toLowerCase()) {
            case 'c':
                if (event.target !== document.getElementById('caption-text')) {
                    event.preventDefault();
                    copyCaptionToClipboard();
                }
                break;
        }
    }
    
    if (event.key === 'Escape') {
        hideCustomUrlModal();
        document.getElementById('alert-overlay').style.display = 'none';
        closeFolderModal();
    }
}

// Setup event listeners for modals
document.addEventListener('DOMContentLoaded', function() {
    setupModalEventListeners();
});

function setupModalEventListeners() {
    // Custom URL modal enter key support
    const customUrlInput = document.getElementById('custom-url-input');
    if (customUrlInput) {
        customUrlInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                scrapeCustomUrl();
            } else if (event.key === 'Escape') {
                hideCustomUrlModal();
            }
        });
    }
    
    // Global keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Modal animation helpers
function showModalWithAnimation(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        modal.style.opacity = '0';
        modal.style.transform = 'scale(0.9)';
        
        requestAnimationFrame(() => {
            modal.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            modal.style.opacity = '1';
            modal.style.transform = 'scale(1)';
        });
    }
}

function hideModalWithAnimation(modalId, callback) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        modal.style.opacity = '0';
        modal.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            modal.style.display = 'none';
            if (callback) callback();
        }, 300);
    }
}

// Enhanced custom URL modal with validation
function showCustomUrlModal() {
    showModalWithAnimation('custom-url-modal');
    const input = document.getElementById('custom-url-input');
    if (input) {
        input.focus();
        input.select();
    }
}

function hideCustomUrlModal() {
    hideModalWithAnimation('custom-url-modal', () => {
        document.getElementById('custom-url-input').value = '';
    });
}

// URL validation helper
function validateUrl(url) {
    if (!url || url.trim() === '') {
        return { valid: false, message: 'Please enter a URL' };
    }
    
    // Basic URL validation
    const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
    if (!urlPattern.test(url)) {
        return { valid: false, message: 'Please enter a valid URL' };
    }
    
    // Check if it looks like a product URL
    if (!url.includes('product') && !url.includes('item') && !url.includes('shop')) {
        return { 
            valid: true, 
            warning: 'This URL may not be a product page. Continue anyway?' 
        };
    }
    
    return { valid: true };
}

// Enhanced scrape custom URL with validation
async function scrapeCustomUrl() {
    const url = document.getElementById('custom-url-input').value.trim();
    const validation = validateUrl(url);
    
    if (!validation.valid) {
        await showAlert(validation.message);
        return;
    }
    
    if (validation.warning) {
        const proceed = await showConfirm(validation.warning);
        if (!proceed) return;
    }
    
    hideCustomUrlModal();
    updateStatus('🚀 Starting custom URL scraper...');
    showProgress('Scraping Custom URL', `Downloading product data and images from: ${url}`);
    
    try {
        const response = await fetch('/api/scrape_custom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await response.json();
        if (data.success) {
            updateStatus('⏳ Downloading...');
        } else {
            updateProgress(0, 'ERROR: ' + data.error);
            setTimeout(() => {
                hideProgress();
                updateStatus('❌ Scraping failed: ' + data.error);
            }, 5000);
        }
    } catch (error) {
        updateProgress(0, 'NETWORK ERROR: ' + error.message);
        setTimeout(() => {
            hideProgress();
            updateStatus('❌ Scraping failed: ' + error.message);
        }, 5000);
    }
}

// Enhanced alert system with better UX
function showAlert(message, type = 'info') {
    return new Promise((resolve) => {
        const alertOverlay = document.getElementById('alert-overlay');
        const alertMessage = document.getElementById('alert-message');
        const alertButtons = document.getElementById('alert-buttons');
        
        // Add type-specific styling
        const alertContainer = alertOverlay.querySelector('.alert-container');
        alertContainer.className = 'alert-container';
        if (type === 'error') {
            alertContainer.style.borderColor = 'rgba(255, 107, 107, 0.5)';
        } else if (type === 'success') {
            alertContainer.style.borderColor = 'rgba(0, 255, 170, 0.5)';
        } else if (type === 'warning') {
            alertContainer.style.borderColor = 'rgba(255, 193, 7, 0.5)';
        } else {
            alertContainer.style.borderColor = 'rgba(0, 204, 255, 0.5)';
        }
        
        alertMessage.textContent = message;
        alertButtons.innerHTML = `
            <button class="alert-btn alert-ok" onclick="resolveAlert(true)">OK</button>
        `;
        
        showModalWithAnimation('alert-overlay');
        alertResolve = resolve;
    });
}

function showConfirm(message, options = {}) {
    return new Promise((resolve) => {
        const alertOverlay = document.getElementById('alert-overlay');
        const alertMessage = document.getElementById('alert-message');
        const alertButtons = document.getElementById('alert-buttons');
        
        const okText = options.okText || 'OK';
        const cancelText = options.cancelText || 'Cancel';
        
        alertMessage.textContent = message;
        alertButtons.innerHTML = `
            <button class="alert-btn alert-ok" onclick="resolveAlert(true)">${okText}</button>
            <button class="alert-btn alert-cancel" onclick="resolveAlert(false)">${cancelText}</button>
        `;
        
        showModalWithAnimation('alert-overlay');
        alertResolve = resolve;
    });
}

function resolveAlert(value) {
    hideModalWithAnimation('alert-overlay', () => {
        if (alertResolve) {
            alertResolve(value);
            alertResolve = null;
        }
    });
}

// Toast notification system for quick feedback
function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #1e2a54 0%, #252545 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid rgba(0, 204, 255, 0.3);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10003;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Type-specific colors
    if (type === 'error') {
        toast.style.borderColor = 'rgba(255, 107, 107, 0.5)';
    } else if (type === 'success') {
        toast.style.borderColor = 'rgba(0, 255, 170, 0.5)';
    } else if (type === 'warning') {
        toast.style.borderColor = 'rgba(255, 193, 7, 0.5)';
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });
    
    // Auto remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// Tooltip system for enhanced UX
function showTooltip(element, text, position = 'top') {
    // Remove existing tooltip
    const existingTooltip = document.querySelector('.custom-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.style.cssText = `
        position: absolute;
        background: linear-gradient(135deg, #2a3a64 0%, #1e2a54 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        border: 1px solid rgba(0, 204, 255, 0.3);
        z-index: 10004;
        max-width: 200px;
        word-wrap: break-word;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.2s ease;
    `;
    
    tooltip.textContent = text;
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left, top;
    
    switch (position) {
        case 'top':
            left = rect.left + (rect.width - tooltipRect.width) / 2;
            top = rect.top - tooltipRect.height - 8;
            break;
        case 'bottom':
            left = rect.left + (rect.width - tooltipRect.width) / 2;
            top = rect.bottom + 8;
            break;
        case 'left':
            left = rect.left - tooltipRect.width - 8;
            top = rect.top + (rect.height - tooltipRect.height) / 2;
            break;
        case 'right':
            left = rect.right + 8;
            top = rect.top + (rect.height - tooltipRect.height) / 2;
            break;
        default:
            left = rect.left + (rect.width - tooltipRect.width) / 2;
            top = rect.bottom + 8;
    }
    
    // Keep tooltip in viewport
    left = Math.max(8, Math.min(left, window.innerWidth - tooltipRect.width - 8));
    top = Math.max(8, Math.min(top, window.innerHeight - tooltipRect.height - 8));
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
    tooltip.style.opacity = '1';
    
    return tooltip;
}

function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 200);
    }
}

