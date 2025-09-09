"""
Path Utilities - Handle cross-platform path conversion and normalization
Converts Mac/Windows paths to VPS paths and manages file operations
"""
import os
import re
import unicodedata
from pathlib import Path

# For slugify function
_DASHES = {"\u2013": "-", "\u2014": "-", "\u2212": "-"}

def slugify(s: str) -> str:
    """Create a clean slug from product title"""
    if not s:
        return "unknown"
    s = "".join(_DASHES.get(ch, ch) for ch in s)
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[^\w\s\-]", "", s.lower())
    s = re.sub(r"[\s\-]+", "-", s).strip("-")
    return s or "unknown"

def normalize_image_path(image_path):
    """Convert Mac/Windows paths to VPS paths"""
    if not image_path:
        return None
    
    # Convert to string if Path object
    image_path = str(image_path)
    
    # Handle Mac paths: /Users/matthewmacosko/Desktop/ad-generator/data/products/...
    if '/Users/matthewmacosko/Desktop/ad-generator/' in image_path:
        relative_part = image_path.split('/ad-generator/', 1)[1]
        vps_path = f'/var/www/tools/{relative_part}'
        return vps_path
    
    # Handle other Mac variations
    if '/Users/matthewmacosko/' in image_path and 'data/' in image_path:
        parts = image_path.split('data/', 1)
        if len(parts) > 1:
            vps_path = f'/var/www/tools/data/{parts[1]}'
            return vps_path
    
    # Handle Windows paths: C:\Users\...\data\products\...
    if ':\\' in image_path and 'data' in image_path:
        parts = image_path.replace('\\', '/').split('/')
        if 'data' in parts:
            data_index = parts.index('data')
            relative_parts = parts[data_index:]
            vps_path = '/var/www/tools/' + '/'.join(relative_parts)
            return vps_path
    
    # If already a VPS path, return as-is
    if image_path.startswith('/var/www/tools/'):
        return image_path
    
    # If it's a relative path, make it absolute to VPS
    if not os.path.isabs(image_path):
        return f'/var/www/tools/{image_path}'
    
    return image_path

def create_product_folders(title, base_products_dir='/var/www/tools/data/products'):
    """Create organized folder structure with VPS paths"""
    # Create safe folder name
    safe_name = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')[:50]
    
    # Remove double underscores
    while '__' in safe_name:
        safe_name = safe_name.replace('__', '_')
    
    # Create folders
    product_folder = os.path.join(base_products_dir, safe_name)
    images_folder = os.path.join(product_folder, 'images')
    
    os.makedirs(product_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)
    
    print(f"  Created folders:")
    print(f"    Product: {product_folder}")
    print(f"    Images: {images_folder}")
    
    return product_folder, images_folder, safe_name

def fix_mac_to_vps_paths(products):
    """Fix all Mac paths in product list to VPS paths"""
    for product in products:
        # Fix image paths
        if 'local_images' in product:
            fixed_images = []
            for img_path in product['local_images']:
                if '/Users/matthewmacosko/Desktop/ad-generator/' in img_path:
                    relative_part = img_path.split('/ad-generator/', 1)[1]
                    vps_path = f'/var/www/tools/{relative_part}'
                    fixed_images.append(vps_path)
                elif '/Users/matthewmacosko/' in img_path and 'data/' in img_path:
                    parts = img_path.split('data/', 1)
                    if len(parts) > 1:
                        vps_path = f'/var/www/tools/data/{parts[1]}'
                        fixed_images.append(vps_path)
                    else:
                        fixed_images.append(img_path)
                else:
                    fixed_images.append(img_path)
            product['local_images'] = fixed_images
        
        # Fix folder paths
        for path_key in ['product_folder', 'images_folder', 'local_image']:
            if path_key in product and '/Users/matthewmacosko/' in product[path_key]:
                if '/ad-generator/' in product[path_key]:
                    relative_part = product[path_key].split('/ad-generator/', 1)[1]
                    product[path_key] = f'/var/www/tools/{relative_part}'
                elif 'data/' in product[path_key]:
                    parts = product[path_key].split('data/', 1)
                    if len(parts) > 1:
                        product[path_key] = f'/var/www/tools/data/{parts[1]}'
    
    return products

def to_local_path(p: str, project_root: Path) -> Path:
    """
    Normalize Windows/absolute/relative paths into a local path under project_root.
    If the string contains a 'data/...', keep from 'data' downward.
    """
    if not p:
        return Path()
    p = p.replace("\\", "/")
    # Windows drive? e.g., C:/...
    first = p.split("/", 1)[0]
    if ":" in first:
        parts = Path(p).parts
        if "data" in parts:
            parts = parts[parts.index("data"):]  # keep 'data/...'
            return (project_root / Path(*parts)).resolve()
        return (project_root / Path(*parts[1:])).resolve()
    path = Path(p)
    if path.is_absolute():
        return path
    return (project_root / path).resolve()

def ensure_vps_directory_structure():
    """Ensure all necessary VPS directories exist"""
    directories = [
        '/var/www/tools/data',
        '/var/www/tools/data/products',
        '/var/www/tools/temp_ads',
        '/var/www/tools/temp_ads/instagram',
        '/var/www/tools/templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("VPS directory structure ensured")

def get_file_icon(filename):
    """Get appropriate icon for file type"""
    ext = filename.lower().split('.')[-1]
    icon_map = {
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️',
        'json': '📊', 'txt': '📝', 'csv': '📊', 'pdf': '📕', 'doc': '📄', 'docx': '📄',
        'zip': '📦', 'rar': '📦', 'mp4': '🎥', 'mp3': '🎵', 'wav': '🎵'
    }
    return icon_map.get(ext, '📄')

def format_file_size(bytes):
    """Format file size in human readable format"""
    if bytes == 0:
        return '0 B'
    k = 1024
    sizes = ['B', 'KB', 'MB', 'GB']
    i = int(bytes / k)
    if i >= len(sizes):
        i = len(sizes) - 1
    return f"{round(bytes / (k ** i), 1)} {sizes[i]}"

