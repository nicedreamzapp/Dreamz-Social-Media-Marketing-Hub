"""
Application Configuration - Setup paths and initialize components
Handles import logic and component initialization for Flask app
"""
import sys
import os
from pathlib import Path

# User credentials
USERS = {'Divine': 'Adwork'}

def setup_app_paths():
    """Setup all necessary paths for the application"""
    current_dir = Path(__file__).parent
    
    # Add all necessary paths to sys.path
    paths_to_add = [
        str(current_dir),
        str(current_dir / "core"),
        str(current_dir / "core" / "scrapers"),
        str(current_dir / "core" / "generators"),
        str(current_dir / "core" / "processors"),
        str(current_dir / "core" / "utils"),
        str(current_dir / "platforms" / "instagram"),
        str(current_dir / "ui"),
        str(current_dir / "ui" / "components"),
        str(current_dir / "data"),
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.append(path)
    
    print("✅ Application paths configured")

def initialize_components():
    """Initialize scraper and Instagram generator components"""
    
    # Try to import unified scraper
    scraper_module = None
    try:
        import unified_scraper
        print("✅ Unified scraper imported successfully")
        scraper_module = unified_scraper
    except ImportError as e:
        print(f"❌ Unified scraper import error: {e}")
    
    # Try to import Instagram generator
    instagram_module = None
    try:
        import instagram_generator
        print("✅ Instagram generator imported")
        instagram_module = instagram_generator
    except ImportError as e:
        print(f"❌ Instagram generator import error: {e}")
    
    return scraper_module, instagram_module

def get_project_directories():
    """Get standard project directory paths"""
    base_dir = '/var/www/tools'
    
    directories = {
        'base_dir': base_dir,
        'data_dir': os.path.join(base_dir, 'data'),
        'products_dir': os.path.join(base_dir, 'data', 'products'),
        'temp_dir': os.path.join(base_dir, 'temp_ads'),
        'templates_dir': os.path.join(base_dir, 'templates'),
        'master_db': os.path.join(base_dir, 'data', 'products_master.json')
    }
    
    # Create directories if they don't exist
    for key, directory in directories.items():
        if key != 'master_db':  # Don't create the JSON file, just directories
            os.makedirs(directory, exist_ok=True)
    
    return directories

def verify_component_availability():
    """Check which components are available"""
    availability = {
        'scraper_available': False,
        'instagram_available': False,
        'enhanced_images_available': False
    }
    
    try:
        import unified_scraper
        availability['scraper_available'] = True
    except ImportError:
        pass
    
    try:
        import instagram_generator
        availability['instagram_available'] = True
    except ImportError:
        pass
    
    try:
        import enhanced_image_processor
        availability['enhanced_images_available'] = True
    except ImportError:
        pass
    
    return availability

