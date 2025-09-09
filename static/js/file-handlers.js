/* File Handlers - File operations, downloads, and file system interactions */

// Download handling for product files
function downloadSingleImage(filename) {
    try {
        const imageUrl = `/temp_ads/${filename}`;
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log(`Downloaded: ${filename}`);
        showToast(`Downloaded: ${filename}`, 'success', 2000);
    } catch (error) {
        console.error('Failed to download image:', error);
        showToast('Failed to download image', 'error');
    }
}

function downloadAllImages() {
    try {
        const imageElements = document.querySelectorAll('.img-container img');
        let downloadCount = 0;
        
        if (imageElements.length === 0) {
            showToast('No images available to download', 'warning');
            return;
        }
        
        showToast(`Starting download of ${imageElements.length} images...`, 'info');
        
        imageElements.forEach((img, index) => {
            setTimeout(() => {
                const src = img.src;
                const filename = src.split('/').pop();
                
                const link = document.createElement('a');
                link.href = src;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                downloadCount++;
                console.log(`Downloaded ${downloadCount}/${imageElements.length}: ${filename}`);
                
                if (downloadCount === imageElements.length) {
                    showToast(`Downloaded all ${downloadCount} images!`, 'success');
                }
            }, index * 500);
        });
        
    } catch (error) {
        console.error('Failed to download all images:', error);
        showToast('Failed to download images', 'error');
    }
}

// Open image in new tab
function openImage(imagePath) {
    try {
        const filename = imagePath.split('/').pop();
        const imageUrl = `/temp_ads/${filename}`;
        window.open(imageUrl, '_blank');
    } catch (error) {
        console.error('Failed to open image:', error);
        showToast('Failed to open image', 'error');
    }
}

// File upload handling (for future features)
function handleFileUpload(files) {
    if (!files || files.length === 0) {
        showToast('No files selected', 'warning');
        return;
    }
    
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validate file type
        if (!allowedTypes.includes(file.type)) {
            showToast(`Invalid file type: ${file.name}`, 'error');
            continue;
        }
        
        // Validate file size
        if (file.size > maxSize) {
            showToast(`File too large: ${file.name}`, 'error');
            continue;
        }
        
        // Process file (placeholder for future upload functionality)
        console.log('Valid file:', file.name, file.type, file.size);
    }
}

// Drag and drop handling
function setupDragAndDrop() {
    const dropZone = document.body;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropZone.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }
    
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFileUpload(files);
    }
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
            return true;
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
            return fallbackCopyToClipboard(text);
        });
    } else {
        return fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
            showToast('Copied to clipboard!', 'success');
            return true;
        } else {
            showToast('Failed to copy to clipboard', 'error');
            return false;
        }
    } catch (err) {
        console.error('Fallback copy failed:', err);
        showToast('Failed to copy to clipboard', 'error');
        return false;
    }
}

// File validation helpers
function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!allowedTypes.includes(file.type.toLowerCase())) {
        return { valid: false, error: 'Invalid file type. Please select an image file.' };
    }
    
    if (file.size > maxSize) {
        return { valid: false, error: 'File is too large. Maximum size is 10MB.' };
    }
    
    return { valid: true };
}

function validateProductDataFile(file) {
    const allowedTypes = ['application/json', 'text/plain'];
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    if (!allowedTypes.includes(file.type)) {
        return { valid: false, error: 'Invalid file type. Please select a JSON or text file.' };
    }
    
    if (file.size > maxSize) {
        return { valid: false, error: 'File is too large. Maximum size is 5MB.' };
    }
    
    return { valid: true };
}

// File reading utilities
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(e);
        reader.readAsText(file);
    });
}

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(e);
        reader.readAsDataURL(file);
    });
}

// Export data functionality
function exportProductData() {
    try {
        const dataStr = JSON.stringify(products, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `products_export_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Product data exported successfully!', 'success');
    } catch (error) {
        console.error('Export failed:', error);
        showToast('Failed to export product data', 'error');
    }
}

// Import data functionality (placeholder for future feature)
function importProductData(file) {
    const validation = validateProductDataFile(file);
    if (!validation.valid) {
        showToast(validation.error, 'error');
        return;
    }
    
    readFileAsText(file).then(text => {
        try {
            const importedData = JSON.parse(text);
            if (Array.isArray(importedData)) {
                // Validate imported products structure
                const validProducts = importedData.filter(product => 
                    product && typeof product === 'object' && product.title
                );
                
                if (validProducts.length > 0) {
                    showConfirm(`Import ${validProducts.length} products? This will add to your current gallery.`)
                        .then(confirmed => {
                            if (confirmed) {
                                // Add to current products (API call would be needed)
                                showToast(`Would import ${validProducts.length} products`, 'info');
                            }
                        });
                } else {
                    showToast('No valid products found in file', 'error');
                }
            } else {
                showToast('Invalid file format', 'error');
            }
        } catch (error) {
            showToast('Failed to parse JSON file', 'error');
        }
    }).catch(error => {
        showToast('Failed to read file', 'error');
    });
}

// Initialize file handling on page load
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
});

// Utility function to format file sizes
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// File type detection
function getFileType(filename) {
    const ext = filename.toLowerCase().split('.').pop();
    const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'tiff'];
    const videoTypes = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'];
    const audioTypes = ['mp3', 'wav', 'flac', 'aac', 'ogg'];
    const documentTypes = ['pdf', 'doc', 'docx', 'txt', 'rtf'];
    const dataTypes = ['json', 'xml', 'csv', 'xlsx'];
    
    if (imageTypes.includes(ext)) return 'image';
    if (videoTypes.includes(ext)) return 'video';
    if (audioTypes.includes(ext)) return 'audio';
    if (documentTypes.includes(ext)) return 'document';
    if (dataTypes.includes(ext)) return 'data';
    
    return 'unknown';
}

