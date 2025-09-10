/* Application State Management - Global variables and state - FIXED VERSION */

// Global state variables
let products = [];
let selectedProductIndex = null;
let progressCheckInterval = null;
let isScrapingActive = false;
let alertResolve = null;

// Initialize on page load - ONLY PLACE loadProducts() is called
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Loading products from database...');
    loadProducts();
});

// Load products from server - FIXED with better error handling
async function loadProducts() {
    try {
        console.log('📡 Fetching products from API...');
        const response = await fetch('/api/products');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📦 API Response:', data);
        
        products = data.products || [];
        selectedProductIndex = data.selected_index;
        
        console.log(`✅ Loaded ${products.length} products`);
        
        renderProducts();
        updateProductCount();
        
    } catch (error) {
        console.error('❌ Error loading products:', error);
        updateStatus('❌ Error loading products: ' + error.message);
        
        // Show fallback message
        const container = document.getElementById('products-scroll');
        if (container) {
            container.innerHTML = `
                <div class="no-products">
                    <h3>❌ Loading Error</h3>
                    <p>Could not load products: ${error.message}</p>
                    <p><button onclick="loadProducts()" style="padding: 8px 16px; background: #0066ff; color: white; border: none; border-radius: 5px; cursor: pointer;">🔄 Retry</button></p>
                </div>
            `;
        }
    }
}

// Render products - FIXED with better debugging
function renderProducts() {
    console.log(`🎨 Rendering ${products.length} products...`);
    const container = document.getElementById('products-scroll');
    
    if (!container) {
        console.error('❌ Products container not found!');
        return;
    }
    
    if (products.length === 0) {
        container.innerHTML = `
            <div class="no-products">
                <h3>🚀 Ready to Start</h3>
                <p>Use the sidebar to scrape products from a website and build your gallery!</p>
            </div>
        `;
        return;
    }
    
    try {
        container.innerHTML = products.map((product, index) => {
            let imageSrc = '';
            if (product.local_images && product.local_images.length > 0) {
                let imagePath = product.local_images[0];
                console.log(`🖼️ Processing image path: ${imagePath}`);
                
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
                
                console.log(`🖼️ Final image src: ${imageSrc}`);
            }
            
            return `
                <div class="product-card ${index === selectedProductIndex ? 'selected' : ''}"
                     onclick="selectProduct(${index})">
                    <div class="product-thumbnail">
                        ${imageSrc ?
                          `<img src="${imageSrc}" alt="${product.title}" onerror="console.log('Image load error:', this.src); this.style.display='none'; this.parentNode.innerHTML='📦';">` :
                          '📦'}
                    </div>
                    <div class="product-info">
                        <div class="product-title">${product.title || 'Unknown Product'}</div>
                        <div class="product-price">${product.price || 'Price not available'}</div>
                        <div class="product-description">${truncateText(product.description || '', 320)}</div>
                        <div class="product-source" style="font-size: 11px; color: #888; margin-top: 5px;">
                            ${product.domain ? `📍 ${product.domain}` : ''}
                        </div>
                    </div>
                    <div class="product-actions">
                        <div class="trash-icon" onclick="deleteProduct(${index}); event.stopPropagation();">🗑️</div>
                        <button class="action-btn folder-btn" onclick="openProductFolder(${index}); event.stopPropagation();">📁 Folder</button>
                        ${product.url ? `<button class="action-btn url-btn" onclick="openProductUrl('${product.url}'); event.stopPropagation();">🔗 URL</button>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        console.log('✅ Products rendered successfully');
        
    } catch (error) {
        console.error('❌ Error rendering products:', error);
        container.innerHTML = `
            <div class="no-products">
                <h3>❌ Rendering Error</h3>
                <p>Could not display products: ${error.message}</p>
            </div>
        `;
    }
}

// Character limit for descriptions
function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function updateProductCount() {
    const totalProducts = products.length;
    const totalImages = products.reduce((sum, p) => sum + (p.local_images ? p.local_images.length : 0), 0);
    const countElement = document.getElementById('products-count');
    if (countElement) {
        countElement.textContent = `${totalProducts} products • ${totalImages} images`;
    }
    console.log(`📊 Updated count: ${totalProducts} products, ${totalImages} images`);
}

function updateStatus(message) {
    const statusElement = document.getElementById('status-text');
    if (statusElement) {
        statusElement.textContent = message;
    }
    console.log('📢 Status:', message);
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