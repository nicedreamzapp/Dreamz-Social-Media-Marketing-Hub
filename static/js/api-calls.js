/* API Calls - Server communication and data fetching */

// ACCURATE Progress tracking - polls server for real status
function showProgress(title, details) {
    document.getElementById('progress-title').textContent = title;
    document.getElementById('progress-details').textContent = details;
    document.getElementById('progress-text').textContent = 'Starting scraper...';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-overlay').style.display = 'flex';
    updateStatus('⏳ Downloading...');
    // Disable scraper buttons
    document.getElementById('best-sellers-btn').disabled = true;
    document.getElementById('featured-btn').disabled = true;
    document.getElementById('custom-url-btn').disabled = true;
    isScrapingActive = true;
    startProgressPolling();
}

function startProgressPolling() {
    progressCheckInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/scraping_status');
            const data = await response.json();
            console.log('Scraping status:', data);
            if (data.active) {
                updateProgress(data.progress || 0, data.message || 'Scraping in progress...');
                updateStatus('⏳ Downloading...');
            } else {
                updateProgress(100, 'Complete!');
                setTimeout(() => {
                    hideProgress();
                    loadProducts();
                    updateStatus('✅ Ready');
                }, 1000);
            }
        } catch (error) {
            console.log('Status endpoint error, using fallback:', error);
            const originalCount = products.length;
            await loadProducts();
            if (products.length > originalCount) {
                updateProgress(100, 'Complete!');
                setTimeout(() => {
                    hideProgress();
                    updateStatus('✅ Ready');
                }, 1000);
            } else {
                updateStatus('⏳ Downloading...');
            }
        }
    }, 2000);
}

function hideProgress() {
    document.getElementById('progress-overlay').style.display = 'none';
    if (progressCheckInterval) {
        clearInterval(progressCheckInterval);
        progressCheckInterval = null;
    }
    document.getElementById('best-sellers-btn').disabled = false;
    document.getElementById('featured-btn').disabled = false;
    document.getElementById('custom-url-btn').disabled = false;
    isScrapingActive = false;
}

function updateProgress(percentage, text) {
    document.getElementById('progress-bar').style.width = percentage + '%';
    document.getElementById('progress-text').textContent = text;
}

// Scraper functions with accurate progress
async function scrapeBestSellers() {
    if (isScrapingActive) return;
    updateStatus('🚀 Starting Best Sellers scraper...');
    showProgress('Scraping Best Sellers', 'Downloading top 15 best selling products and their images from the website.');
    try {
        const response = await fetch('/api/scrape_best_sellers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
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

async function scrapeFeatured() {
    if (isScrapingActive) return;
    updateStatus('🚀 Starting Featured Products scraper...');
    showProgress('Scraping Featured Products', 'Downloading up to 20 featured products and their images from the website.');
    try {
        const response = await fetch('/api/scrape_featured', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
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

async function scrapeCustomUrl() {
    const url = document.getElementById('custom-url-input').value.trim();
    if (!url) {
        await showAlert('Please enter a URL');
        return;
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

// Instagram generation
async function generateInstagram() {
    if (selectedProductIndex === null) {
        await showAlert('Please select a product first by clicking on it!');
        return;
    }
    updateStatus('📸 Generating Instagram post...');
    try {
        const response = await fetch('/api/generate_instagram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_index: selectedProductIndex })
        });
        const data = await response.json();
        if (data.success) {
            updateStatus('✅ Instagram post generated successfully!');
            const reviewUrl = `/instagram_review/${selectedProductIndex}`;
            window.open(reviewUrl, '_blank');
        } else {
            updateStatus('❌ Error: ' + data.error);
        }
    } catch (error) {
        updateStatus('❌ Instagram generation failed: ' + error.message);
    }
}

// Facebook generation
async function generateFacebook() {
    if (selectedProductIndex === null) {
        await showAlert('Please select a product first by clicking on it!');
        return;
    }
    updateStatus('📘 Generating Facebook post...');
    try {
        const response = await fetch('/api/generate_facebook', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_index: selectedProductIndex })
        });
        const data = await response.json();
        if (data.success) {
            updateStatus('✅ Facebook post generated successfully!');
            const reviewUrl = `/facebook_review/${selectedProductIndex}`;
            window.open(reviewUrl, '_blank');
        } else {
            updateStatus('❌ Error: ' + data.error);
        }
    } catch (error) {
        updateStatus('❌ Facebook generation failed: ' + error.message);
    }
}

// Delete product
async function deleteProduct(index) {
    const confirmed = await showConfirm('Are you sure you want to delete this product?');
    if (!confirmed) return;
    try {
        const response = await fetch('/api/delete_product', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_index: index })
        });
        const data = await response.json();
        if (data.success) {
            updateStatus(`✅ Product deleted! ${data.remaining_products} products remaining.`);
            loadProducts();
        } else {
            updateStatus('❌ Error: ' + data.error);
        }
    } catch (error) {
        updateStatus('❌ Delete failed: ' + error.message);
    }
}

// Header functions
async function clearTemp() {
    const confirmed = await showConfirm('Clear all temporary files?');
    if (!confirmed) return;
    try {
        const response = await fetch('/api/clear_temp');
        const data = await response.json();
        if (data.success) {
            updateStatus('✅ Temp folder cleared successfully!');
        } else {
            updateStatus('❌ Error: ' + data.error);
        }
    } catch (error) {
        updateStatus('❌ Clear temp failed: ' + error.message);
    }
}

// Placeholder functions
function showComingSoon(platform) {
    showAlert(`${platform} post creator coming soon!`);
}

