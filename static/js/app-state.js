/* Application State Management - Global variables and state */

// Global state variables
let products = [];
let selectedProductIndex = null;
let progressCheckInterval = null;
let isScrapingActive = false;
let alertResolve = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
});

// Load products from server
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const data = await response.json();
        products = data.products;
        selectedProductIndex = data.selected_index;
        renderProducts();
        updateProductCount();
    } catch (error) {
        updateStatus('❌ Error loading products: ' + error.message);
    }
}

// Render products with description character limit
function renderProducts() {
    const container = document.getElementById('products-scroll');
    if (products.length === 0) {
        container.innerHTML = `
            <div class="no-products">
                <h3>🚀 Ready to Start</h3>
                <p>Use the sidebar to scrape products from a website and build your gallery!</p>
            </div>
        `;
        return;
    }
    container.innerHTML = products.map((product, index) => {
        let imageSrc = '';
        if (product.local_images && product.local_images.length > 0) {
            let imagePath = product.local_images[0];
            if (imagePath.includes('/')) {
                const parts = imagePath.split('data/products/');
                if (parts.length > 1) {
                    imageSrc = `/data/products/${parts[parts.length - 1]}`;
                } else {
                    imageSrc = `/data/products/${imagePath.split('/').pop()}`;
                }
            } else {
                imageSrc = `/data/products/${imagePath}`;
            }
        }
        return `
            <div class="product-card ${index === selectedProductIndex ? 'selected' : ''}"
                 onclick="selectProduct(${index})">
                <div class="product-thumbnail">
                    ${imageSrc ?
                      `<img src="${imageSrc}" alt="${product.title}" onerror="this.style.display='none'; this.parentNode.innerHTML='📦';">` :
                      '📦'}
                </div>
                <div class="product-info">
                    <div class="product-title">${product.title || 'Unknown Product'}</div>
                    <div class="product-price">${product.price || 'Price not available'}</div>
                    <div class="product-description">${truncateText(product.description || '', 320)}</div>
                </div>
                <div class="product-actions">
                    <div class="trash-icon" onclick="deleteProduct(${index}); event.stopPropagation();">🗑️</div>
                    <button class="action-btn folder-btn" onclick="openProductFolder(${index}); event.stopPropagation();">📁 Folder</button>
                    ${product.url ? `<button class="action-btn url-btn" onclick="openProductUrl('${product.url}'); event.stopPropagation();">🔗 URL</button>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Character limit for descriptions
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function updateProductCount() {
    const totalProducts = products.length;
    const totalImages = products.reduce((sum, p) => sum + (p.local_images ? p.local_images.length : 0), 0);
    document.getElementById('products-count').textContent = `${totalProducts} products • ${totalImages} images`;
}

function updateStatus(message) {
    document.getElementById('status-text').textContent = message;
}

// Product selection
async function selectProduct(index) {
    try {
        const response = await fetch('/api/select_product', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_index: index })
        });
        const data = await response.json();
        if (data.success) {
            selectedProductIndex = index;
            renderProducts();
            updateStatus(`✅ Selected: ${products[index].title.substring(0, 30)}...`);
        }
    } catch (error) {
        updateStatus('❌ Selection failed: ' + error.message);
    }
}

// Navigation functions
function navigateSelection(direction) {
    if (products.length === 0) return;
    let newIndex;
    if (selectedProductIndex === null) {
        newIndex = 0;
    } else {
        newIndex = selectedProductIndex + direction;
        newIndex = Math.max(0, Math.min(products.length - 1, newIndex));
    }
    selectProduct(newIndex);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (event.key === 'Delete' && selectedProductIndex !== null) {
        deleteProduct(selectedProductIndex);
    } else if (event.key === 'ArrowDown') {
        navigateSelection(1);
    } else if (event.key === 'ArrowUp') {
        navigateSelection(-1);
    } else if (event.key === 'Enter' && selectedProductIndex !== null) {
        generateInstagram();
    } else if (event.key === 'Escape') {
        hideCustomUrlModal();
        document.getElementById('alert-overlay').style.display = 'none';
        closeFolderModal();
    }
});

// Utility function for opening product URLs
function openProductUrl(url) {
    window.open(url, '_blank');
}

