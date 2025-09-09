"""
Flask Wrapper for Divine Tribe Marketing Hub - WITH FACEBOOK SUPPORT
Main Flask app with core routes including Facebook generation
"""
import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash
from flask_cors import CORS
import json
import threading
from functools import wraps

# Import from utility modules
from app_config import setup_app_paths, initialize_components, USERS
from path_utils import normalize_image_path
from database_manager import ProductDatabase
from auth_routes import setup_auth_routes

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)
app.secret_key = 'divine-tribe-marketing-hub-secret-key-2025'

# Setup authentication routes
setup_auth_routes(app, USERS)

# Setup paths and components
setup_app_paths()
scraper_module, instagram_generator_module = initialize_components()

# Import Facebook generator
facebook_generator_module = None
try:
    import facebook_generator
    print("✅ Facebook generator imported")
    facebook_generator_module = facebook_generator
except ImportError as e:
    print(f"❌ Facebook generator import error: {e}")

# Global scraping status
scraping_status = {
    'active': False,
    'progress': 0,
    'message': 'Ready',
    'start_time': None,
    'expected_duration': 0
}

class WebAppWrapper:
    """Wrapper for web app functionality with Instagram and Facebook support"""
    def __init__(self):
        self.current_products = []
        self.selected_product_index = None
        self.temp_folder = '/var/www/tools/temp_ads'
        self.database = ProductDatabase()
        
        os.makedirs(self.temp_folder, exist_ok=True)
        os.makedirs(os.path.join(self.temp_folder, 'instagram'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_folder, 'facebook'), exist_ok=True)
        
        self.load_products_data()
        
        # Initialize Instagram generator
        try:
            if instagram_generator_module:
                self.instagram_generator = instagram_generator_module.InstagramGenerator()
                print("✅ Instagram generator initialized")
            else:
                self.instagram_generator = None
        except Exception as e:
            print(f"❌ Instagram generator initialization error: {e}")
            self.instagram_generator = None
        
        # Initialize Facebook generator
        try:
            if facebook_generator_module:
                self.facebook_generator = facebook_generator_module.FacebookGenerator()
                print("✅ Facebook generator initialized")
            else:
                self.facebook_generator = None
        except Exception as e:
            print(f"❌ Facebook generator initialization error: {e}")
            self.facebook_generator = None

    def load_products_data(self):
        """Load products with path normalization"""
        self.current_products = self.database.load_products()
        
        # Normalize all image paths
        for product in self.current_products:
            if 'local_images' in product:
                normalized_images = []
                for image_path in product['local_images']:
                    normalized_path = normalize_image_path(image_path)
                    if normalized_path:
                        normalized_images.append(normalized_path)
                product['local_images'] = normalized_images
            
            # Fix other paths
            for path_key in ['local_image', 'product_folder', 'images_folder']:
                if path_key in product:
                    product[path_key] = normalize_image_path(product[path_key])

    def save_products_data(self):
        """Save products to database"""
        return self.database.save_products(self.current_products)

# Global app instance
web_app = WebAppWrapper()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/instagram_review/<int:product_index>')
@login_required
def instagram_review(product_index):
    if product_index >= len(web_app.current_products):
        return "Product not found", 404
    
    product = web_app.current_products[product_index]
    
    try:
        if not web_app.instagram_generator:
            return "Instagram generator not available", 500
            
        post_data = web_app.instagram_generator.generate_instagram_post(
            product_index,
            web_app.current_products
        )
        
        if not post_data:
            return "Failed to generate Instagram post data", 500
        
        return render_template('instagram_review.html',
                             product=product,
                             post_data=post_data,
                             product_index=product_index)
    except Exception as e:
        print(f"❌ Instagram review error: {e}")
        return f"Error generating Instagram post: {e}", 500

@app.route('/facebook_review/<int:product_index>')
@login_required
def facebook_review(product_index):
    """Facebook review page - NEW ROUTE"""
    if product_index >= len(web_app.current_products):
        return "Product not found", 404
    
    product = web_app.current_products[product_index]
    
    try:
        if not web_app.facebook_generator:
            return "Facebook generator not available", 500
            
        post_data = web_app.facebook_generator.generate_facebook_post(
            product_index,
            web_app.current_products
        )
        
        if not post_data:
            return "Failed to generate Facebook post data", 500
        
        return render_template('facebook_review.html',
                             product=product,
                             post_data=post_data,
                             product_index=product_index)
    except Exception as e:
        print(f"❌ Facebook review error: {e}")
        return f"Error generating Facebook post: {e}", 500

@app.route('/api/products')
@login_required
def get_products():
    return jsonify({
        'products': web_app.current_products,
        'selected_index': web_app.selected_product_index,
        'total_count': len(web_app.current_products)
    })

@app.route('/api/scraping_status')
@login_required
def get_scraping_status():
    global scraping_status
    
    if scraping_status['active'] and scraping_status['start_time']:
        import time
        elapsed = time.time() - scraping_status['start_time']
        expected = scraping_status['expected_duration']
        if expected > 0:
            estimated_progress = min(95, (elapsed / expected) * 100)
            scraping_status['progress'] = max(scraping_status['progress'], estimated_progress)
    
    return jsonify(scraping_status)

def run_scraper_in_background(scraper_type, **kwargs):
    """Generic background scraper runner"""
    global scraping_status
    
    def run_scraper():
        global scraping_status
        try:
            if not scraper_module or not scraper_module.CleanProductScraper:
                scraping_status = {
                    'active': False, 'progress': 0,
                    'message': 'Scraper not available',
                    'start_time': None, 'expected_duration': 0
                }
                return

            scraper = scraper_module.CleanProductScraper()
            
            if scraper_type == 'best_sellers':
                urls = scraper.get_product_urls('best_sellers', 15)
                scraping_status['message'] = f'Found {len(urls)} best sellers to scrape'
                new_products = scraper.scrape_products(urls, "Best Sellers (Top 15)")
                
            elif scraper_type == 'featured':
                urls = scraper.get_product_urls('featured', 20)
                scraping_status['message'] = f'Found {len(urls)} featured products to scrape'
                new_products = scraper.scrape_products(urls, "Featured Products (Max 20)")
                
            elif scraper_type == 'custom':
                url = kwargs.get('url', '')
                urls = scraper.scrape_custom_url(url)
                scraping_status['message'] = f'Processing custom URL: {url}'
                new_products = scraper.scrape_products(urls, "Custom URL")
            
            if new_products:
                # Normalize paths in new products
                for product in new_products:
                    if 'local_images' in product:
                        normalized_images = []
                        for image_path in product['local_images']:
                            normalized_path = normalize_image_path(image_path)
                            if normalized_path:
                                normalized_images.append(normalized_path)
                        product['local_images'] = normalized_images
                    
                    for path_key in ['product_folder', 'images_folder', 'local_image']:
                        if path_key in product:
                            product[path_key] = normalize_image_path(product[path_key])
                
                web_app.current_products.extend(new_products)
                web_app.save_products_data()
                
                scraping_status = {
                    'active': False, 'progress': 100,
                    'message': f'Complete! Scraped {len(new_products)} products',
                    'start_time': None, 'expected_duration': 0
                }
            else:
                scraping_status = {
                    'active': False, 'progress': 0,
                    'message': 'No new products found',
                    'start_time': None, 'expected_duration': 0
                }
                
        except Exception as e:
            scraping_status = {
                'active': False, 'progress': 0,
                'message': f'Scraping failed: {str(e)}',
                'start_time': None, 'expected_duration': 0
            }
            print(f"❌ Scraper error: {e}")
    
    threading.Thread(target=run_scraper, daemon=True).start()

@app.route('/api/scrape_best_sellers', methods=['POST'])
@login_required
def scrape_best_sellers():
    global scraping_status
    import time
    scraping_status = {
        'active': True, 'progress': 0,
        'message': 'Starting Best Sellers scraper...',
        'start_time': time.time(), 'expected_duration': 90
    }
    run_scraper_in_background('best_sellers')
    return jsonify({'success': True, 'message': 'Best sellers scraping started'})

@app.route('/api/scrape_featured', methods=['POST'])
@login_required
def scrape_featured():
    global scraping_status
    import time
    scraping_status = {
        'active': True, 'progress': 0,
        'message': 'Starting Featured Products scraper...',
        'start_time': time.time(), 'expected_duration': 120
    }
    run_scraper_in_background('featured')
    return jsonify({'success': True, 'message': 'Featured products scraping started'})

@app.route('/api/scrape_custom', methods=['POST'])
@login_required
def scrape_custom():
    global scraping_status
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    import time
    scraping_status = {
        'active': True, 'progress': 0,
        'message': f'Starting custom URL scraper for: {url}',
        'start_time': time.time(), 'expected_duration': 30
    }
    run_scraper_in_background('custom', url=url)
    return jsonify({'success': True, 'message': f'Custom URL scraping started: {url}'})

@app.route('/api/generate_instagram', methods=['POST'])
@login_required
def generate_instagram():
    try:
        if not web_app.instagram_generator:
            return jsonify({'error': 'Instagram generator not available'}), 500
            
        data = request.get_json()
        product_index = data.get('product_index', 0)
        
        if product_index >= len(web_app.current_products):
            return jsonify({'error': 'Invalid product index'}), 400
        
        post_data = web_app.instagram_generator.generate_instagram_post(
            product_index, web_app.current_products
        )
        
        if post_data:
            try:
                files = web_app.instagram_generator.save_post_data(post_data)
            except Exception as save_error:
                print(f"❌ Save error: {save_error}")
                files = []
            
            return jsonify({
                'success': True,
                'post_data': post_data,
                'files': files
            })
        else:
            return jsonify({'error': 'Failed to generate Instagram post'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_facebook', methods=['POST'])
@login_required
def generate_facebook():
    """Generate Facebook post - NEW ROUTE"""
    try:
        if not web_app.facebook_generator:
            return jsonify({'error': 'Facebook generator not available'}), 500
            
        data = request.get_json()
        product_index = data.get('product_index', 0)
        
        if product_index >= len(web_app.current_products):
            return jsonify({'error': 'Invalid product index'}), 400
        
        post_data = web_app.facebook_generator.generate_facebook_post(
            product_index, web_app.current_products
        )
        
        if post_data:
            try:
                files = web_app.facebook_generator.save_post_data(post_data)
            except Exception as save_error:
                print(f"❌ Save error: {save_error}")
                files = []
            
            return jsonify({
                'success': True,
                'post_data': post_data,
                'files': files
            })
        else:
            return jsonify({'error': 'Failed to generate Facebook post'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_product', methods=['POST'])
@login_required
def delete_product():
    try:
        data = request.get_json()
        product_index = data.get('product_index', 0)
        
        if 0 <= product_index < len(web_app.current_products):
            deleted_product = web_app.current_products[product_index]
            
            import shutil
            files_deleted = []
            
            # Delete product folder and contents
            if 'product_folder' in deleted_product and deleted_product['product_folder']:
                product_folder = deleted_product['product_folder']
                if os.path.exists(product_folder):
                    shutil.rmtree(product_folder)
                    files_deleted.append(f"Folder: {product_folder}")
            
            # Remove from products list
            web_app.current_products.pop(product_index)
            
            # Reset selection if needed
            if web_app.selected_product_index == product_index:
                web_app.selected_product_index = None
            elif web_app.selected_product_index and web_app.selected_product_index > product_index:
                web_app.selected_product_index -= 1
            
            web_app.save_products_data()
            
            return jsonify({
                'success': True,
                'deleted_product': deleted_product.get('title', 'Unknown'),
                'remaining_products': len(web_app.current_products),
                'files_deleted': files_deleted
            })
        else:
            return jsonify({'error': 'Invalid product index'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear_temp')
@login_required
def clear_temp():
    try:
        import shutil
        temp_path = '/var/www/tools/temp_ads'
        
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
            os.makedirs(temp_path)
            os.makedirs(os.path.join(temp_path, 'instagram'))
            os.makedirs(os.path.join(temp_path, 'facebook'))
        else:
            os.makedirs(temp_path, exist_ok=True)
            os.makedirs(os.path.join(temp_path, 'instagram'), exist_ok=True)
            os.makedirs(os.path.join(temp_path, 'facebook'), exist_ok=True)
            
        return jsonify({'success': True, 'message': 'Temp folder cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/select_product', methods=['POST'])
@login_required
def select_product():
    try:
        data = request.get_json()
        product_index = data.get('product_index', 0)
        
        if 0 <= product_index < len(web_app.current_products):
            web_app.selected_product_index = product_index
            return jsonify({'success': True, 'selected_index': product_index})
        else:
            return jsonify({'error': 'Invalid product index'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/open_folder', methods=['POST'])
@login_required
def open_folder():
    try:
        data = request.get_json()
        product_index = data.get('product_index', 0)
        
        if product_index >= len(web_app.current_products):
            return jsonify({'error': 'Invalid product index'}), 400
        
        product = web_app.current_products[product_index]
        product_folder = product.get('product_folder', '')
        
        if not product_folder or not os.path.exists(product_folder):
            return jsonify({'error': 'Product folder not found'}), 404
        
        folder_contents = []
        for item in os.listdir(product_folder):
            item_path = os.path.join(product_folder, item)
            if os.path.isfile(item_path):
                file_size = os.path.getsize(item_path)
                folder_contents.append({
                    'name': item, 'type': 'file',
                    'size': file_size, 'path': item_path
                })
            elif os.path.isdir(item_path):
                folder_contents.append({
                    'name': item, 'type': 'folder', 'path': item_path
                })
        
        return jsonify({
            'success': True,
            'folder_path': product_folder,
            'contents': folder_contents,
            'product_title': product.get('title', 'Unknown Product')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_file')
@login_required
def download_file():
    file_path = request.args.get('path')
    if not file_path or not os.path.exists(file_path):
        return "File not found", 404
    
    if not file_path.startswith('/var/www/tools/data/'):
        return "Access denied", 403
    
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/temp_ads/<path:filename>')
@login_required
def serve_temp_file(filename):
    """Serve files from VPS temp folder - supports both Instagram and Facebook"""
    import glob
    try:
        base_temp = '/var/www/tools/temp_ads'
        
        direct_path = os.path.join(base_temp, filename)
        if os.path.exists(direct_path):
            return send_from_directory(base_temp, filename)
        
        search_patterns = [
            f"{base_temp}/instagram/*/{filename}",
            f"{base_temp}/facebook/*/{filename}",
            f"{base_temp}/*/{filename}",
            f"{base_temp}/**/{filename}"
        ]
        
        for pattern in search_patterns:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                actual_path = matches[0]
                folder = os.path.dirname(actual_path)
                actual_filename = os.path.basename(actual_path)
                return send_from_directory(folder, actual_filename)
        
        return "File not found", 404
        
    except Exception as e:
        return "File serve error", 500

@app.route('/data/products/<path:filename>')
@login_required
def serve_product_image(filename):
    try:
        base_products = '/var/www/tools/data/products'
        
        if filename.startswith('/Users/matthewmacosko/'):
            filename = os.path.basename(filename)
        
        filename = filename.lstrip('/')
        return send_from_directory(base_products, filename)
    except Exception as e:
        return "File not found", 404

if __name__ == '__main__':
    print("🚀 Starting Divine Tribe Marketing Hub - Web Version")
    print("📸 Instagram support: Active")
    print("📘 Facebook support: Active")
    print("🌐 Access at: http://tools.marijuanaunion.com")
    print(f"📊 Current products loaded: {len(web_app.current_products)}")
    print("✅ Instagram and Facebook generators ready")
    
    app.run(debug=True, host='0.0.0.0', port=8080)