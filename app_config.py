"""
App Configuration - Universal WooCommerce Support
Handles path setup, component initialization, and user management
"""
import os
import sys
from pathlib import Path

# User credentials for authentication - Updated with Divine/Adwork
USERS = {
      
}

def setup_app_paths():
    """Setup application paths for VPS environment"""
    base_dir = Path('/var/www/tools')
    
    # Ensure all required directories exist
    required_dirs = [
        base_dir / 'data',
        base_dir / 'data' / 'products',
        base_dir / 'temp_ads',
        base_dir / 'temp_ads' / 'instagram',
        base_dir / 'temp_ads' / 'facebook',
        base_dir / 'static' / 'css',
        base_dir / 'static' / 'js',
        base_dir / 'templates'
    ]
    
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Add base directory to Python path if not already there
    base_str = str(base_dir)
    if base_str not in sys.path:
        sys.path.insert(0, base_str)
    
    print(f"✅ App paths configured: {base_dir}")
    return base_dir

def initialize_components():
    """Initialize scraper and generator components with error handling"""
    scraper_module = None
    instagram_generator_module = None
    
    # Try to import scraper module
    try:
        import unified_scraper
        scraper_module = unified_scraper
        print("✅ Universal scraper module loaded")
    except ImportError as e:
        print(f"❌ Scraper import error: {e}")
    except Exception as e:
        print(f"❌ Scraper initialization error: {e}")
    
    # Try to import Instagram generator
    try:
        import instagram_generator
        instagram_generator_module = instagram_generator
        print("✅ Instagram generator module loaded")
    except ImportError as e:
        print(f"❌ Instagram generator import error: {e}")
    except Exception as e:
        print(f"❌ Instagram generator initialization error: {e}")
    
    return scraper_module, instagram_generator_module

def get_supported_sites():
    """Get configuration for all supported WooCommerce sites"""
    return {
        'ineedhemp': {
            'name': 'I Need Hemp',
            'domain': 'ineedhemp.com',
            'base_url': 'https://ineedhemp.com',
            'description': 'Premium vaporizer and concentrate products'
        },
        'nicedreamz': {
            'name': 'Nice Dreamz Wholesale',
            'domain': 'nicedreamzwholesale.com', 
            'base_url': 'https://nicedreamzwholesale.com',
            'description': 'Wholesale vaporizer products and accessories'
        },
        'tribeseed': {
            'name': 'Tribe Seed Bank',
            'domain': 'tribeseedbank.com',
            'base_url': 'https://tribeseedbank.com', 
            'description': 'Premium seeds and growing supplies'
        }
    }

def validate_environment():
    """Validate that the environment is properly configured"""
    issues = []
    
    # Check if we're in the correct directory
    current_dir = Path.cwd()
    expected_dir = Path('/var/www/tools')
    
    if current_dir != expected_dir:
        issues.append(f"Working directory should be {expected_dir}, but is {current_dir}")
    
    # Check for required files
    required_files = [
        'flask_wrapper.py',
        'product_scraper_core.py',
        'unified_scraper.py',
        'database_manager.py',
        'path_utils.py'
    ]
    
    for filename in required_files:
        filepath = expected_dir / filename
        if not filepath.exists():
            issues.append(f"Missing required file: {filename}")
    
    # Check for .env file
    env_file = expected_dir / '.env'
    if not env_file.exists():
        issues.append("Missing .env file with API credentials")
    
    # Check virtual environment
    venv_path = expected_dir / 'new-flask-env'
    if not venv_path.exists():
        issues.append("Virtual environment 'new-flask-env' not found")
    
    if issues:
        print("⚠️ Environment validation issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Environment validation passed")
        return True

def get_app_info():
    """Get application information and status"""
    return {
        'name': 'Dreamz Social Media Marketing Hub',
        'version': '3.0-universal',
        'description': 'Universal WooCommerce scraping and social media content generation',
        'supported_sites': len(get_supported_sites()),
        'features': [
            'Multi-site WooCommerce scraping',
            'Instagram post generation',
            'Facebook post generation', 
            'Product image processing',
            'Automated content creation'
        ]
    }

# Initialize on import
if __name__ == '__main__':
    print("App Configuration Test")
    print("=" * 30)
    
    # Test path setup
    base_dir = setup_app_paths()
    
    # Test environment validation
    is_valid = validate_environment()
    
    # Test component initialization
    scraper, instagram = initialize_components()
    
    # Show app info
    app_info = get_app_info()
    print(f"\nApp: {app_info['name']} v{app_info['version']}")
    print(f"Supported sites: {app_info['supported_sites']}")
    print("Features:")
    for feature in app_info['features']:
        print(f"  - {feature}")
    
    # Show supported sites
    print("\nSupported Sites:")
    sites = get_supported_sites()
    for key, site in sites.items():
        print(f"  - {site['name']} ({site['domain']})")
