/* Main App - Application initialization and core functionality */

// Application initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('🚀 Initializing Divine Tribe Marketing Hub');
    
    // Load initial data
    loadProducts();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize UI components
    initializeUIComponents();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Check application status
    checkApplicationStatus();
    
    console.log('✅ Application initialized successfully');
}

function setupEventListeners() {
    // Modal event listeners
    setupModalEventListeners();
    
    // Window resize handler
    window.addEventListener('resize', handleWindowResize);
    
    // Before unload handler
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Focus/blur handlers for better UX
    window.addEventListener('focus', handleWindowFocus);
    window.addEventListener('blur', handleWindowBlur);
}

function initializeUIComponents() {
    // Initialize tooltips for elements with title attributes
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            if (!e.target.title) return;
            const tooltip = showTooltip(e.target, e.target.title);
            
            element.addEventListener('mouseleave', function() {
                hideTooltip();
            }, { once: true });
        });
    });
    
    // Initialize progress indicators
    initializeProgressSystem();
    
    // Setup auto-refresh for product count
    setInterval(updateProductCount, 30000); // Update every 30 seconds
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Global shortcuts
        if (event.ctrlKey || event.metaKey) {
            switch(event.key.toLowerCase()) {
                case 'r':
                    event.preventDefault();
                    loadProducts();
                    showToast('Refreshed product gallery', 'info');
                    break;
                case 'n':
                    event.preventDefault();
                    showCustomUrlModal();
                    break;
                case 'i':
                    if (selectedProductIndex !== null) {
                        event.preventDefault();
                        generateInstagram();
                    }
                    break;
                case 'f':
                    if (selectedProductIndex !== null) {
                        event.preventDefault();
                        generateFacebook();
                    }
                    break;
                case 'e':
                    event.preventDefault();
                    exportProductData();
                    break;
            }
        }
        
        // Function key shortcuts
        switch(event.key) {
            case 'F1':
                event.preventDefault();
                showKeyboardShortcuts();
                break;
            case 'F5':
                event.preventDefault();
                location.reload();
                break;
        }
        
        // Navigation shortcuts
        if (!event.ctrlKey && !event.metaKey && !event.altKey) {
            switch(event.key) {
                case 'Delete':
                    if (selectedProductIndex !== null && !isModalOpen()) {
                        deleteProduct(selectedProductIndex);
                    }
                    break;
                case 'ArrowDown':
                    if (!isModalOpen()) {
                        event.preventDefault();
                        navigateSelection(1);
                    }
                    break;
                case 'ArrowUp':
                    if (!isModalOpen()) {
                        event.preventDefault();
                        navigateSelection(-1);
                    }
                    break;
                case 'Enter':
                    if (selectedProductIndex !== null && !isModalOpen()) {
                        event.preventDefault();
                        generateInstagram();
                    }
                    break;
                case 'Escape':
                    closeAllModals();
                    break;
            }
        }
    });
}

function isModalOpen() {
    const modals = ['custom-url-modal', 'alert-overlay'];
    return modals.some(modalId => {
        const modal = document.getElementById(modalId);
        return modal && modal.style.display !== 'none';
    }) || window.currentFolderModal;
}

function closeAllModals() {
    hideCustomUrlModal();
    document.getElementById('alert-overlay').style.display = 'none';
    closeFolderModal();
}

function handleWindowResize() {
    // Adjust UI for different screen sizes
    const sidebar = document.querySelector('.sidebar');
    const mainContainer = document.querySelector('.main-container');
    
    if (window.innerWidth < 768) {
        sidebar.classList.add('mobile-sidebar');
        mainContainer.classList.add('mobile-layout');
    } else {
        sidebar.classList.remove('mobile-sidebar');
        mainContainer.classList.remove('mobile-layout');
    }
}

function handleBeforeUnload(event) {
    // Warn user if scraping is active
    if (isScrapingActive) {
        event.preventDefault();
        event.returnValue = 'Scraping is in progress. Are you sure you want to leave?';
        return event.returnValue;
    }
}

function handleWindowFocus() {
    // Refresh data when window regains focus
    if (!isScrapingActive) {
        loadProducts();
    }
}

function handleWindowBlur() {
    // Hide tooltips when window loses focus
    hideTooltip();
}

function initializeProgressSystem() {
    // Setup progress polling system
    if (progressCheckInterval) {
        clearInterval(progressCheckInterval);
        progressCheckInterval = null;
    }
}

function checkApplicationStatus() {
    // Check if all required components are loaded
    const requiredElements = [
        'products-scroll',
        'products-count', 
        'status-text',
        'progress-overlay',
        'custom-url-modal',
        'alert-overlay'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.error('Missing required elements:', missingElements);
        showToast('Application initialization incomplete', 'error');
        return false;
    }
    
    return true;
}

function showKeyboardShortcuts() {
    const shortcuts = `
Keyboard Shortcuts:

Navigation:
- ↑/↓ Arrow Keys - Navigate products
- Enter - Generate Instagram post
- Delete - Delete selected product
- Escape - Close modals

Actions:
- Ctrl+R - Refresh gallery
- Ctrl+N - New custom URL
- Ctrl+I - Generate Instagram
- Ctrl+F - Generate Facebook
- Ctrl+E - Export data

Other:
- F1 - Show this help
- F5 - Reload page
    `;
    
    showAlert(shortcuts.trim());
}

// Error handling and reporting
function handleError(error, context = 'Unknown') {
    console.error(`Error in ${context}:`, error);
    
    // Log error for debugging
    const errorDetails = {
        context: context,
        message: error.message || error,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
    };
    
    console.log('Error details:', errorDetails);
    
    // Show user-friendly error message
    let userMessage = 'An error occurred. Please try again.';
    
    if (error.message) {
        if (error.message.includes('fetch')) {
            userMessage = 'Network error. Please check your connection.';
        } else if (error.message.includes('JSON')) {
            userMessage = 'Data format error. Please refresh the page.';
        }
    }
    
    showToast(userMessage, 'error');
}

// Application state management
function getApplicationState() {
    return {
        products: products,
        selectedProductIndex: selectedProductIndex,
        isScrapingActive: isScrapingActive,
        timestamp: Date.now()
    };
}

function saveApplicationState() {
    try {
        const state = getApplicationState();
        localStorage.setItem('divineTribeAppState', JSON.stringify(state));
    } catch (error) {
        console.warn('Could not save application state:', error);
    }
}

function restoreApplicationState() {
    try {
        const saved = localStorage.getItem('divineTribeAppState');
        if (saved) {
            const state = JSON.parse(saved);
            // Only restore if recent (within 1 hour)
            if (Date.now() - state.timestamp < 3600000) {
                selectedProductIndex = state.selectedProductIndex;
                console.log('Restored application state');
            }
        }
    } catch (error) {
        console.warn('Could not restore application state:', error);
    }
}

// Performance monitoring
function measurePerformance(name, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
}

// Cleanup and optimization
function cleanup() {
    // Clear intervals
    if (progressCheckInterval) {
        clearInterval(progressCheckInterval);
        progressCheckInterval = null;
    }
    
    // Remove event listeners
    window.removeEventListener('resize', handleWindowResize);
    window.removeEventListener('beforeunload', handleBeforeUnload);
    window.removeEventListener('focus', handleWindowFocus);
    window.removeEventListener('blur', handleWindowBlur);
    
    // Close modals
    closeAllModals();
    
    console.log('Application cleanup completed');
}

// Register cleanup on page unload
window.addEventListener('unload', cleanup);

// Expose global functions for debugging
window.divineApp = {
    getState: getApplicationState,
    saveState: saveApplicationState,
    restoreState: restoreApplicationState,
    cleanup: cleanup,
    showShortcuts: showKeyboardShortcuts,
    exportData: exportProductData
};

// Auto-save state periodically
setInterval(saveApplicationState, 60000); // Save every minute

// Initialize performance monitoring
if (window.performance && window.performance.mark) {
    performance.mark('app-init-start');
    
    window.addEventListener('load', function() {
        performance.mark('app-init-end');
        performance.measure('app-initialization', 'app-init-start', 'app-init-end');
        
        const measure = performance.getEntriesByName('app-initialization')[0];
        console.log(`App initialization completed in ${measure.duration.toFixed(2)}ms`);
    });
}

console.log('🎉 Divine Tribe Marketing Hub loaded successfully');
console.log('📖 Press F1 for keyboard shortcuts');

