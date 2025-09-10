/* ChatGPT Core Integration - Universal Cross-Platform Base Class
 * Handles device detection, clipboard access, and ChatGPT opening logic
 * Used by all social media review templates
 */

class ChatGPTCore {
    constructor() {
        this.platform = this.detectPlatform();
        this.currentProductData = null;
        this.isInitialized = false;
    }

    detectPlatform() {
        const userAgent = navigator.userAgent;
        return {
            isMobile: /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent),
            isIOS: /iPad|iPhone|iPod/.test(userAgent),
            isAndroid: /Android/i.test(userAgent),
            isSafari: /Safari/.test(userAgent) && !/Chrome/.test(userAgent),
            isChrome: /Chrome/.test(userAgent),
            hasClipboard: !!(navigator.clipboard && navigator.clipboard.writeText),
            isBrave: !!(navigator.brave && navigator.brave.isBrave)
        };
    }

    init(productData) {
        this.currentProductData = productData;
        this.isInitialized = true;
        
        // Clear Brave browser cache if detected
        if (this.platform.isBrave) {
            localStorage.clear();
            sessionStorage.clear();
        }
        
        console.log('ChatGPT Core initialized for platform:', this.platform);
    }

    getProductText(textareaId = 'caption-text') {
        const textarea = document.getElementById(textareaId);
        let productText = textarea ? textarea.value : '';
        
        // Fallback to current product data if textarea is empty
        if (!productText.trim() && this.currentProductData) {
            productText = this.currentProductData.caption || '';
            if (textarea) {
                textarea.value = productText;
            }
            console.log('Using fallback product data for ChatGPT');
        }
        
        return productText;
    }

    async copyToClipboard(text) {
        if (this.platform.hasClipboard) {
            try {
                await navigator.clipboard.writeText(text);
                return true;
            } catch (error) {
                console.warn('Clipboard write failed:', error);
                return false;
            }
        }
        return false;
    }

    openChatGPTWeb(prompt = '') {
        const baseUrl = 'https://chat.openai.com/';
        const urlWithPrompt = prompt ? `${baseUrl}?q=${encodeURIComponent(prompt)}` : baseUrl;
        
        try {
            window.open(urlWithPrompt, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
            return true;
        } catch (error) {
            console.error('Failed to open ChatGPT web:', error);
            return false;
        }
    }

    showPromptModal(prompt, promptType) {
        const modal = document.createElement('div');
        modal.id = 'chatgpt-prompt-modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.9); z-index: 10000; display: flex; 
            align-items: center; justify-content: center; padding: 20px;
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: linear-gradient(135deg, #1e2a54 0%, #252545 100%);
            border-radius: 15px; padding: 25px; max-width: 90%; max-height: 80%; 
            overflow-y: auto; color: white; border: 2px solid #00ccff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        `;
        
        content.innerHTML = `
            <h3 style="margin-bottom: 20px; color: #00ccff; text-align: center; font-size: 18px;">
                Copy Prompt for ChatGPT (${promptType})
            </h3>
            <textarea readonly id="prompt-text" style="width: 100%; height: 250px; padding: 15px; 
                background: #252545; color: white; border: 2px solid #00ccff; 
                border-radius: 10px; font-family: 'Segoe UI', sans-serif; font-size: 13px; 
                line-height: 1.4; resize: none;">${prompt}</textarea>
            <div style="margin-top: 20px; text-align: center;">
                <button id="copy-prompt-btn" style="padding: 12px 25px; background: #00ccff; color: #1e2a54; 
                    border: none; border-radius: 8px; font-weight: bold; margin-right: 15px; 
                    cursor: pointer; font-size: 14px;">Copy & Open ChatGPT</button>
                <button id="open-only-btn" style="padding: 12px 25px; background: #0066ff; color: white; 
                    border: none; border-radius: 8px; font-weight: bold; margin-right: 15px; 
                    cursor: pointer; font-size: 14px;">Open ChatGPT</button>
                <button id="close-modal-btn" style="padding: 12px 25px; background: #6c5ce7; color: white; 
                    border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 14px;">Close</button>
            </div>
            <p style="margin-top: 15px; font-size: 12px; color: #aaa; text-align: center; line-height: 1.3;">
                ${this.platform.isMobile ? 
                    'Tap and hold the text above to select all, then copy and paste into ChatGPT' :
                    'Click "Copy & Open ChatGPT" to copy the prompt and open ChatGPT in a new tab'
                }
            </p>
        `;
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
        // Event listeners
        const promptTextarea = content.querySelector('#prompt-text');
        const copyBtn = content.querySelector('#copy-prompt-btn');
        const openBtn = content.querySelector('#open-only-btn');
        const closeBtn = content.querySelector('#close-modal-btn');
        
        copyBtn.onclick = async () => {
            const copied = await this.copyToClipboard(prompt);
            if (copied) {
                copyBtn.textContent = 'Copied! Opening...';
                copyBtn.style.background = '#00ff88';
                setTimeout(() => {
                    this.openChatGPTWeb();
                    modal.remove();
                }, 500);
            } else {
                // Fallback: select text for manual copy
                promptTextarea.select();
                copyBtn.textContent = 'Text Selected - Copy It';
            }
        };
        
        openBtn.onclick = () => {
            this.openChatGPTWeb(prompt);
            modal.remove();
        };
        
        closeBtn.onclick = () => modal.remove();
        
        // Auto-select text on desktop
        if (!this.platform.isMobile) {
            setTimeout(() => promptTextarea.select(), 100);
        }
        
        // ESC key to close
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    async handleDesktop(prompt, promptType) {
        console.log('Handling desktop ChatGPT integration');
        
        if (this.platform.hasClipboard) {
            const copied = await this.copyToClipboard(prompt);
            if (copied) {
                this.openChatGPTWeb();
                console.log(`ChatGPT ${promptType} opened with clipboard content`);
            } else {
                // Fallback to URL with prompt
                this.openChatGPTWeb(prompt);
            }
        } else {
            // Old browser fallback
            this.openChatGPTWeb(prompt);
        }
    }

    async handleMobile(prompt, promptType) {
        console.log('Handling mobile ChatGPT integration');
        
        if (this.platform.hasClipboard) {
            const copied = await this.copyToClipboard(prompt);
            if (copied) {
                alert('Prompt copied to clipboard! Opening ChatGPT...');
                
                if (this.platform.isIOS) {
                    // iOS: Try app first, then web
                    window.location.href = 'chatgpt://';
                    setTimeout(() => this.openChatGPTWeb(), 1500);
                } else {
                    // Android: Direct to web
                    this.openChatGPTWeb(prompt);
                }
            } else {
                // Show modal for manual copy
                this.showPromptModal(prompt, promptType);
            }
        } else {
            // No clipboard support: Show modal
            this.showPromptModal(prompt, promptType);
        }
    }

    async openPrompt(promptTemplate, promptType, textareaId = 'caption-text') {
        if (!this.isInitialized) {
            console.error('ChatGPT Core not initialized. Call init() first.');
            return;
        }
        
        try {
            const productText = this.getProductText(textareaId);
            
            if (!productText.trim()) {
                alert('Please enter some caption content first');
                return;
            }
            
            if (!promptTemplate) {
                alert('Invalid prompt type');
                return;
            }
            
            const fullPrompt = promptTemplate.replace('{product_text}', productText);
            
            // Route to appropriate handler
            if (this.platform.isMobile) {
                await this.handleMobile(fullPrompt, promptType);
            } else {
                await this.handleDesktop(fullPrompt, promptType);
            }
            
        } catch (error) {
            console.error('Failed to open ChatGPT:', error);
            // Final fallback
            this.openChatGPTWeb();
        }
    }
}

// Global instance
window.ChatGPTCore = new ChatGPTCore();

