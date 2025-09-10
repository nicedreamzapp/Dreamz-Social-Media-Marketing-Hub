/* UI Handlers - User interface interactions and event handling */

// Custom Alert/Confirm functions
function showAlert(message) {
    return new Promise((resolve) => {
        const alertOverlay = document.getElementById('alert-overlay');
        const alertMessage = document.getElementById('alert-message');
        const alertButtons = document.getElementById('alert-buttons');
        alertMessage.textContent = message;
        alertButtons.innerHTML = `
            <button class="alert-btn alert-ok" onclick="resolveAlert(true)">OK</button>
        `;
        alertOverlay.style.display = 'flex';
        alertResolve = resolve;
    });
}

function showConfirm(message) {
    return new Promise((resolve) => {
        const alertOverlay = document.getElementById('alert-overlay');
        const alertMessage = document.getElementById('alert-message');
        const alertButtons = document.getElementById('alert-buttons');
        alertMessage.textContent = message;
        alertButtons.innerHTML = `
            <button class="alert-btn alert-ok" onclick="resolveAlert(true)">OK</button>
            <button class="alert-btn alert-cancel" onclick="resolveAlert(false)">Cancel</button>
        `;
        alertOverlay.style.display = 'flex';
        alertResolve = resolve;
    });
}

function resolveAlert(value) {
    document.getElementById('alert-overlay').style.display = 'none';
    if (alertResolve) {
        alertResolve(value);
        alertResolve = null;
    }
}

// Custom URL modal functions
function showCustomUrlModal() {
    document.getElementById('custom-url-modal').style.display = 'block';
    document.getElementById('custom-url-input').focus();
}

function hideCustomUrlModal() {
    document.getElementById('custom-url-modal').style.display = 'none';
    document.getElementById('custom-url-input').value = '';
}

// Folder functionality - opens product folder with file browser
async function openProductFolder(index) {
    try {
        updateStatus('📁 Opening product folder...');
        
        const response = await fetch('/api/open_folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_index: index })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showFolderModal(data);
            updateStatus(`📁 Opened folder: ${data.product_title}`);
        } else {
            updateStatus('❌ Error: ' + data.error);
        }
    } catch (error) {
        updateStatus('❌ Folder access failed: ' + error.message);
    }
}

function showFolderModal(folderData) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.style.zIndex = '10002'; // Higher than alerts
    
    const filesList = folderData.contents.map(item => {
        if (item.type === 'file') {
            const sizeStr = formatFileSize(item.size);
            const fileIcon = getFileIcon(item.name);
            return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); hover: background: rgba(255,255,255,0.05);">
                    <div style="display: flex; align-items: center; flex: 1;">
                        <span style="margin-right: 10px; font-size: 16px;">${fileIcon}</span>
                        <span style="color: #fff; word-break: break-all;">${item.name}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: #ccc; font-size: 12px; min-width: 60px; text-align: right;">${sizeStr}</span>
                        <button onclick="downloadFile('${item.path.replace(/'/g, "\\'")}'); event.stopPropagation();" 
                                style="padding: 4px 12px; font-size: 11px; background: linear-gradient(135deg, #0066ff 0%, #0099ff 100%); color: white; border: none; border-radius: 6px; cursor: pointer; transition: all 0.3s ease;">
                            Download
                        </button>
                    </div>
                </div>
            `;
        } else {
            return `
                <div style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; align-items: center;">
                        <span style="margin-right: 10px; font-size: 16px;">📁</span>
                        <span style="color: #fff;">${item.name}</span>
                        <span style="color: #888; margin-left: 10px; font-size: 12px;">(folder)</span>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px; max-height: 80vh; overflow: hidden; display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h3 style="margin: 0;">📁 ${folderData.product_title}</h3>
                    <p style="color: #aaa; font-size: 12px; margin: 5px 0 0 0; word-break: break-all;">${folderData.folder_path}</p>
                </div>
                <button onclick="closeFolderModal()" style="background: #ff6b6b; color: white; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer; font-size: 16px;">×</button>
            </div>
            
            <div style="flex: 1; overflow-y: auto; border: 1px solid rgba(0, 204, 255, 0.3); border-radius: 12px; background: rgba(30, 42, 84, 0.3);">
                ${filesList || '<div style="padding: 20px; text-align: center; color: #ccc;">No files found</div>'}
            </div>
            
            <div style="margin-top: 20px; text-align: center; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1);">
                <span style="color: #aaa; font-size: 12px;">${folderData.contents.length} items total</span>
            </div>
            
            <div class="modal-buttons" style="margin-top: 15px;">
                <button class="modal-btn modal-cancel" onclick="closeFolderModal()">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentFolderModal = modal;
    
    // Add click outside to close
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeFolderModal();
        }
    });
}

function closeFolderModal() {
    if (window.currentFolderModal) {
        document.body.removeChild(window.currentFolderModal);
        window.currentFolderModal = null;
    }
}

function downloadFile(filePath) {
    const url = `/api/download_file?path=${encodeURIComponent(filePath)}`;
    window.open(url, '_blank');
    updateStatus('📥 Download started...');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function getFileIcon(filename) {
    const ext = filename.toLowerCase().split('.').pop();
    const iconMap = {
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️',
        'json': '📊', 'txt': '📝', 'csv': '📊', 'pdf': '📕', 'doc': '📄', 'docx': '📄',
        'zip': '📦', 'rar': '📦', 'mp4': '🎥', 'mp3': '🎵', 'wav': '🎵'
    };
    return iconMap[ext] || '📄';
}

// Close modal on click outside
document.getElementById('custom-url-modal').addEventListener('click', function(event) {
    if (event.target === this) {
        hideCustomUrlModal();
    }
});

// Close alert on click outside
document.getElementById('alert-overlay').addEventListener('click', function(event) {
    if (event.target === this) {
        resolveAlert(false);
    }
});