"""
Path Utilities - Universal file and folder management
Handles path creation, normalization, and validation across multiple sites
"""
import os
import re
from pathlib import Path
import unicodedata

class PathManager:
    """Centralized path management for the application"""
    
    def __init__(self, base_dir='/var/www/tools'):
        self.base_dir = Path(base_dir)
        self.products_dir = self.base_dir / 'data' / 'products'
        self.temp_dir = self.base_dir / 'temp_ads'
        self.static_dir = self.base_dir / 'static'
        
        # Ensure all base directories exist
        self.products_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        (self.temp_dir / 'instagram').mkdir(exist_ok=True)
        (self.temp_dir / 'facebook').mkdir(exist_ok=True)

def sanitize_filename(filename):
    """Convert any string to a safe filename"""
    if not filename:
        return 'unknown'
    
    # Remove or replace problematic characters
    filename = str(filename)
    
    # Normalize unicode characters
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove HTML tags if any
    filename = re.sub(r'<[^>]+>', '', filename)
    
    # Replace problematic characters with safe alternatives
    replacements = {
        ' ': '-',
        '_': '-',
        '/': '-',
        '\\': '-',
        ':': '-',
        '*': '',
        '?': '',
        '"': '',
        '<': '',
        '>': '',
        '|': '-',
        '&': 'and',
        '%': 'percent',
        '#': 'num',
        '@': 'at',
        '+': 'plus',
        '=': 'equals',
        '[': '',
        ']': '',
        '{': '',
        '}': '',
        '(': '',
        ')': '',
        ';': '',
        ',': '',
        '!': '',
        '$': '',
        '^': '',
        '~': '',
        '`': ''
    }
    
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    # Remove non-ASCII characters
    filename = re.sub(r'[^\x00-\x7F]+', '', filename)
    
    # Clean up multiple dashes
    filename = re.sub(r'-+', '-', filename)
    
    # Remove leading/trailing dashes and dots
    filename = filename.strip('-.')
    
    # Ensure it's not empty and not too long
    if not filename:
        filename = 'unknown'
    
    # Limit length (filesystem limitation)
    if len(filename) > 200:
        filename = filename[:200]
    
    # Ensure it doesn't end with a dash
    filename = filename.rstrip('-')
    
    return filename.lower()

def slugify(text):
    """Convert text to URL-friendly slug"""
    if not text:
        return 'unknown'
    
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    
    return text.strip('-')

def create_product_folders(product_title, base_products_dir):
    """Create folder structure for a product with enhanced safety"""
    try:
        # Generate safe folder name
        safe_name = sanitize_filename(product_title)
        
        # Ensure unique folder name
        base_folder = Path(base_products_dir) / safe_name
        product_folder = base_folder
        counter = 1
        
        while product_folder.exists():
            product_folder = Path(f"{base_folder}_{counter}")
            counter += 1
        
        # Create the folders
        product_folder.mkdir(parents=True, exist_ok=True)
        images_folder = product_folder / 'images'
        images_folder.mkdir(exist_ok=True)
        
        print(f"  ✓ Created folders: {product_folder.name}")
        
        return str(product_folder), str(images_folder), safe_name
        
    except Exception as e:
        print(f"❌ Folder creation error: {e}")
        # Fallback to a generic folder
        fallback_folder = Path(base_products_dir) / f"product_{len(os.listdir(base_products_dir)) if os.path.exists(base_products_dir) else 0}"
        fallback_folder.mkdir(parents=True, exist_ok=True)
        images_folder = fallback_folder / 'images'
        images_folder.mkdir(exist_ok=True)
        
        return str(fallback_folder), str(images_folder), fallback_folder.name

def normalize_image_path(image_path):
    """Convert any image path to VPS-compatible path"""
    if not image_path:
        return None
    
    # Handle string paths
    path_str = str(image_path)
    
    # Skip already normalized paths
    if path_str.startswith('/var/www/tools/'):
        return path_str
    
    # Handle old macOS paths
    if path_str.startswith('/Users/matthewmacosko/'):
        # Extract the relevant parts after the user directory
        parts = path_str.split('/')
        if 'data' in parts and 'products' in parts:
            try:
                data_index = parts.index('data')
                relevant_parts = parts[data_index:]
                normalized_path = '/var/www/tools/' + '/'.join(relevant_parts)
                return normalized_path
            except (ValueError, IndexError):
                pass
    
    # Handle relative paths
    if not path_str.startswith('/'):
        if path_str.startswith('data/'):
            return '/var/www/tools/' + path_str
        elif path_str.startswith('products/'):
            return '/var/www/tools/data/' + path_str
        else:
            # Default to products directory
            return '/var/www/tools/data/products/' + path_str
    
    # Handle other absolute paths - try to map them
    if '/data/products/' in path_str:
        parts = path_str.split('/data/products/')
        if len(parts) > 1:
            return '/var/www/tools/data/products/' + parts[1]
    
    # If all else fails, return as-is (might be a valid path)
    return path_str

def validate_path_security(path):
    """Ensure path is within allowed directories"""
    try:
        # Convert to absolute path and resolve
        abs_path = Path(path).resolve()
        allowed_base = Path('/var/www/tools').resolve()
        
        # Check if path is within allowed directory
        return str(abs_path).startswith(str(allowed_base))
        
    except Exception:
        return False

def clean_temp_directory(platform=None):
    """Clean temporary files with optional platform filter"""
    try:
        temp_base = Path('/var/www/tools/temp_ads')
        
        if platform:
            # Clean specific platform directory
            platform_dir = temp_base / platform
            if platform_dir.exists():
                import shutil
                shutil.rmtree(platform_dir)
                platform_dir.mkdir()
                print(f"✓ Cleaned {platform} temp directory")
        else:
            # Clean all temp directories
            if temp_base.exists():
                import shutil
                shutil.rmtree(temp_base)
                temp_base.mkdir()
                (temp_base / 'instagram').mkdir()
                (temp_base / 'facebook').mkdir()
                print("✓ Cleaned all temp directories")
        
        return True
        
    except Exception as e:
        print(f"❌ Temp cleanup error: {e}")
        return False

def get_relative_web_path(full_path):
    """Convert full VPS path to web-accessible relative path"""
    if not full_path:
        return None
    
    path_str = str(full_path)
    
    # Handle product images
    if '/var/www/tools/data/products/' in path_str:
        return path_str.replace('/var/www/tools/data/products/', 'data/products/')
    
    # Handle temp files
    if '/var/www/tools/temp_ads/' in path_str:
        return path_str.replace('/var/www/tools/temp_ads/', 'temp_ads/')
    
    # Handle static files
    if '/var/www/tools/static/' in path_str:
        return path_str.replace('/var/www/tools/static/', 'static/')
    
    return path_str

def ensure_directory_structure():
    """Ensure all required directories exist"""
    required_dirs = [
        '/var/www/tools/data',
        '/var/www/tools/data/products',
        '/var/www/tools/data/backups',
        '/var/www/tools/temp_ads',
        '/var/www/tools/temp_ads/instagram',
        '/var/www/tools/temp_ads/facebook',
        '/var/www/tools/static/css',
        '/var/www/tools/static/js',
        '/var/www/tools/templates'
    ]
    
    created_dirs = []
    for dir_path in required_dirs:
        path_obj = Path(dir_path)
        if not path_obj.exists():
            path_obj.mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_path)
    
    if created_dirs:
        print(f"✓ Created {len(created_dirs)} missing directories")
    
    return True

def get_file_info(file_path):
    """Get comprehensive file information"""
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            return None
        
        stat = path_obj.stat()
        return {
            'name': path_obj.name,
            'size': stat.st_size,
            'size_human': format_file_size(stat.st_size),
            'modified': stat.st_mtime,
            'is_file': path_obj.is_file(),
            'is_dir': path_obj.is_dir(),
            'extension': path_obj.suffix.lower(),
            'parent': str(path_obj.parent)
        }
        
    except Exception as e:
        print(f"❌ File info error: {e}")
        return None

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def find_files_by_pattern(directory, pattern, recursive=True):
    """Find files matching a pattern"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        return [str(f) for f in files]
        
    except Exception as e:
        print(f"❌ File search error: {e}")
        return []

# Initialize directory structure on import
ensure_directory_structure()

# Test functionality
if __name__ == '__main__':
    print("Path Utils Test")
    print("=" * 30)
    
    # Test sanitize_filename
    test_names = [
        "Test Product: Special & Amazing!",
        "Product with (parentheses) and [brackets]",
        "Unicode: café naïve résumé",
        "",
        "Very long product name that exceeds normal filesystem limitations and should be truncated appropriately"
    ]
    
    print("Filename Sanitization:")
    for name in test_names:
        safe_name = sanitize_filename(name)
        print(f"  '{name}' -> '{safe_name}'")
    
    # Test slugify function
    print("\nSlugify Test:")
    for name in test_names:
        slug = slugify(name)
        print(f"  '{name}' -> '{slug}'")
    
    # Test path normalization
    test_paths = [
        "/Users/matthewmacosko/Desktop/data/products/test/image1.jpg",
        "data/products/test-product/images/img.png",
        "/var/www/tools/data/products/existing/photo.jpg"
    ]
    
    print("\nPath Normalization:")
    for path in test_paths:
        normalized = normalize_image_path(path)
        print(f"  '{path}' -> '{normalized}'")
    
    # Test directory structure
    print(f"\nDirectory Structure:")
    print("✓ All required directories verified/created")