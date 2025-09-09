"""
Enhanced Image Processor - FIXED to Only Get Main Product Images
Prevents all types of duplicates and excludes related product images
"""

import requests
import os
import time
import re
from urllib.parse import urlparse

class EnhancedImageProcessor:
    def __init__(self, headers=None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        print("✓ Enhanced image processor loaded - no duplicates")
    
    def extract_image_urls(self, soup, base_url):
        """FIXED: Extract ONLY main product gallery images - no related products"""
        images = []
        seen_urls = set()
        seen_base_names = set()
        
        print("  Extracting images with enhanced duplicate prevention...")
        
        # FIXED: Product-specific selectors only (no broad selectors)
        main_product_selectors = [
            '.woocommerce-product-gallery img',           # Main product gallery
            '.product-images img',                        # Theme-specific main gallery
            'img[data-large_image]',                      # WooCommerce large images
            '.wp-post-image',                             # WordPress featured image
            '.attachment-woocommerce_single img',         # WooCommerce single product
            'img[data-zoom-image]',                       # Zoom plugin images
            '.flex-viewport img',                         # Flexible slider main images
            '.product-image-main img',                    # Main product image container
            '#product-images img'                         # Product images by ID
        ]
        
        # Containers to EXCLUDE (related products, recommendations)
        excluded_containers = [
            '.related-products',
            '.upsells',
            '.cross-sells', 
            '.you-may-also-like',
            '.recommended-products',
            '.similar-products',
            '.recently-viewed',
            '.product-recommendations',
            '.woocommerce-tabs',
            '.reviews',
            '.related',
            'aside',
            '.sidebar',
            '.footer'
        ]
        
        for selector in main_product_selectors:
            for img in soup.select(selector):
                # FIXED: Check if image is in excluded container
                if self.is_in_excluded_container(img, excluded_containers):
                    continue
                
                # Try multiple attributes for image URL
                found_url = None
                for attr in ['data-large_image', 'data-zoom-image', 'src', 'data-src', 'data-original']:
                    src = img.get(attr)
                    if src:
                        src = self.clean_image_url(src)
                        
                        if src and self.is_valid_image_url(src):
                            found_url = src
                            break
                
                if found_url:
                    # Enhanced duplicate prevention
                    if found_url in seen_urls:
                        continue
                    
                    # Check for size variations
                    base_name = self.get_image_base_name(found_url)
                    if base_name in seen_base_names:
                        # Replace with larger image if current is bigger
                        self.replace_with_larger_image(found_url, images, seen_urls)
                        continue
                    
                    # Add to collections
                    images.append(found_url)
                    seen_urls.add(found_url)
                    seen_base_names.add(base_name)
        
        print(f"  Found {len(images)} unique images after duplicate filtering")
        return images
    
    def is_in_excluded_container(self, img, excluded_containers):
        """Check if image is inside an excluded container"""
        parent = img.parent
        
        # Walk up the DOM tree to check for excluded containers
        while parent:
            if parent.name:
                # Check class names
                parent_classes = parent.get('class', [])
                for excluded in excluded_containers:
                    excluded_clean = excluded.replace('.', '')
                    if excluded_clean in parent_classes:
                        return True
                
                # Check IDs
                parent_id = parent.get('id', '')
                for excluded in excluded_containers:
                    excluded_clean = excluded.replace('#', '').replace('.', '')
                    if excluded_clean in parent_id:
                        return True
            
            parent = parent.parent
        
        return False
    
    def get_image_base_name(self, url):
        """Extract base image name without size indicators"""
        # Get filename from URL
        filename = url.split('/')[-1].split('?')[0]
        
        # Remove size patterns
        base = filename
        size_patterns = [
            r'-\d+x\d+',      # -300x300, -768x768, etc.
            r'_\d+x\d+',      # _300x300, _768x768, etc.
            r'-scaled',       # WordPress scaled images
            r'-\d+$'          # Just numbers at end
        ]
        
        for pattern in size_patterns:
            base = re.sub(pattern, '', base)
        
        return base
    
    def extract_image_dimensions(self, url):
        """Extract width and height from URL"""
        # Look for size patterns like -300x300
        size_match = re.search(r'-(\d+)x(\d+)', url)
        if size_match:
            width, height = map(int, size_match.groups())
            return width * height
        
        # Images without size indicators are likely original/large
        return 999999
    
    def replace_with_larger_image(self, new_url, images, seen_urls):
        """Replace existing image with larger version if new one is bigger"""
        new_base = self.get_image_base_name(new_url)
        new_size = self.extract_image_dimensions(new_url)
        
        for i, existing_url in enumerate(images):
            existing_base = self.get_image_base_name(existing_url)
            
            if new_base == existing_base:
                existing_size = self.extract_image_dimensions(existing_url)
                
                # Replace if new image is larger
                if new_size > existing_size:
                    seen_urls.remove(existing_url)
                    seen_urls.add(new_url)
                    images[i] = new_url
                    print(f"    Replaced with larger version: {new_base}")
                break
    
    def clean_image_url(self, url):
        """Clean and normalize image URL"""
        if not url:
            return None
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        # Handle relative URLs
        elif url.startswith('/'):
            url = 'https://ineedhemp.com' + url
        
        # Remove query parameters
        if '?' in url:
            url = url.split('?')[0]
        
        return url
    
    def is_valid_image_url(self, url):
        """Validate image URL with stricter filtering"""
        if not url:
            return False
        
        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(ext in url.lower() for ext in valid_extensions):
            return False
        
        # Exclude unwanted images (more comprehensive)
        exclude_terms = [
            'logo', 'favicon', 'placeholder', 'loading', 'spinner', 
            'icon', 'badge', 'social', 'payment', 'shipping',
            'security', 'guarantee', 'arrow', 'button'
        ]
        
        url_lower = url.lower()
        if any(term in url_lower for term in exclude_terms):
            return False
        
        # Must be from the main domain
        if 'ineedhemp.com' not in url:
            return False
        
        # Exclude very small images
        if any(size in url for size in ['-50x50', '-100x100', '-75x75', '-25x25', '-150x150']):
            return False
        
        return True
    
    def download_images(self, image_urls, images_folder):
        """Download images with comprehensive duplicate checking"""
        downloaded = []
        
        # Check existing images
        existing_files = {}
        existing_sizes = {}
        
        if os.path.exists(images_folder):
            for filename in os.listdir(images_folder):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    filepath = os.path.join(images_folder, filename)
                    existing_files[filename] = filepath
                    
                    try:
                        file_size = os.path.getsize(filepath)
                        existing_sizes[file_size] = filepath
                    except:
                        pass
        
        print(f"  Downloading {len(image_urls)} unique images...")
        
        for i, url in enumerate(image_urls):
            try:
                # Generate filename
                ext = 'jpg'
                if url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                    ext = url.split('.')[-1].lower().split('?')[0]
                
                filename = f"image_{i+1}.{ext}"
                filepath = os.path.join(images_folder, filename)
                
                # Skip if exists
                if filename in existing_files:
                    print(f"    Skipped existing: {filename}")
                    downloaded.append(existing_files[filename])
                    continue
                
                # Download
                response = requests.get(url, timeout=15, headers=self.headers)
                response.raise_for_status()
                
                content_size = len(response.content)
                
                # Skip tiny images
                if content_size < 2000:
                    print(f"    Skipped tiny image: {filename} ({content_size} bytes)")
                    continue
                
                # Check for duplicate content by size
                if content_size in existing_sizes:
                    print(f"    Skipped duplicate content: {filename}")
                    downloaded.append(existing_sizes[content_size])
                    continue
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                downloaded.append(filepath)
                existing_files[filename] = filepath
                existing_sizes[content_size] = filepath
                
                print(f"    Downloaded: {filename} ({content_size} bytes)")
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    Failed image {i+1}: {e}")
                continue
        
        print(f"✓ Enhanced image processing prevented duplicates")
        print(f"  Downloaded {len(downloaded)} total images")
        return downloaded
    
    def validate_downloaded_images(self, downloaded_images):
        """Validate downloaded images"""
        valid_images = []
        
        for image_path in downloaded_images:
            try:
                if os.path.exists(image_path) and os.path.getsize(image_path) > 1000:
                    valid_images.append(image_path)
                else:
                    if os.path.exists(image_path):
                        os.remove(image_path)
            except Exception as e:
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except:
                        pass
        
        return valid_images

# Test function
def test_enhanced_processor():
    """Test the enhanced image processor"""
    print("Testing Enhanced Image Processor (Main Product Only)...")
    print("=" * 60)
    
    processor = EnhancedImageProcessor()
    
    # Test HTML with main product and related products
    test_html = """
    <div class="woocommerce-product-gallery">
        <img src="https://ineedhemp.com/wp-content/uploads/main-product.jpg" data-large_image="https://ineedhemp.com/wp-content/uploads/main-product-768x768.jpg">
        <img src="https://ineedhemp.com/wp-content/uploads/main-product-2.jpg">
    </div>
    
    <div class="related-products">
        <img src="https://ineedhemp.com/wp-content/uploads/related-product-1.jpg">
        <img src="https://ineedhemp.com/wp-content/uploads/related-product-2.jpg">
    </div>
    
    <div class="upsells">
        <img src="https://ineedhemp.com/wp-content/uploads/upsell-product.jpg">
    </div>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(test_html, 'html.parser')
    
    image_urls = processor.extract_image_urls(soup, "https://ineedhemp.com")
    
    print(f"Extracted {len(image_urls)} main product images (should be 2-3):")
    for i, url in enumerate(image_urls, 1):
        print(f"  {i}. {url}")
    
    print("\nShould exclude related products and upsells!")

if __name__ == "__main__":
    test_enhanced_processor()