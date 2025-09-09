"""
Unified Scraper - REDUCED VERSION
Main scraper class with utilities moved to separate modules
"""
import os
import json
import time
from datetime import datetime
import requests
from product_scraper_core import ProductScraperCore
from path_utils import create_product_folders, normalize_image_path
from database_manager import ProductDatabase

# Import enhanced image processor if available
try:
    from enhanced_image_processor import EnhancedImageProcessor
    ENHANCED_IMAGES = True
    print("✓ Enhanced image processor loaded")
except ImportError:
    print("⚠ Enhanced image processor not found - using basic image handling")
    ENHANCED_IMAGES = False

class CleanProductScraper:
    """Main scraper class - REDUCED VERSION with utilities extracted"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Initialize core scraper
        self.scraper_core = ProductScraperCore(self.headers)
        
        # Initialize database manager
        self.database = ProductDatabase()
        
        # VPS paths
        self.base_dir = '/var/www/tools'
        self.products_dir = '/var/www/tools/data/products'
        
        # Initialize enhanced image processor
        if ENHANCED_IMAGES:
            self.image_processor = EnhancedImageProcessor(self.headers)
        else:
            self.image_processor = None
        
        print(f"✓ Clean scraper ready - VPS paths configured")
    
    def get_existing_products(self, scrape_source=None):
        """Get existing products with optional source filtering"""
        return self.database.get_existing_products(scrape_source)
    
    def download_images(self, image_urls, images_folder):
        """Download images using enhanced processor or basic method"""
        if ENHANCED_IMAGES and self.image_processor:
            downloaded = self.image_processor.download_images(image_urls, images_folder)
            return self.image_processor.validate_downloaded_images(downloaded)
        else:
            return self.basic_download_images(image_urls, images_folder)
    
    def basic_download_images(self, image_urls, images_folder):
        """Fallback: Basic image downloading"""
        downloaded = []
        
        # Check existing images
        existing_images = set()
        if os.path.exists(images_folder):
            existing_images = set(f for f in os.listdir(images_folder) 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')))
        
        for i, url in enumerate(image_urls):
            try:
                # Generate filename
                ext = 'jpg'
                if url.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                    ext = url.split('.')[-1].lower().split('?')[0]
                
                filename = f"image_{i+1}.{ext}"
                filepath = os.path.join(images_folder, filename)
                
                # Skip if exists
                if filename in existing_images:
                    print(f"    Skipped existing: {filename}")
                    downloaded.append(filepath)
                    continue
                
                # Download
                response = requests.get(url, timeout=15, headers=self.headers)
                response.raise_for_status()
                
                if len(response.content) < 1000:
                    print(f"    Skipped tiny image: {filename}")
                    continue
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                downloaded.append(filepath)
                print(f"    Downloaded: {filename} ({len(response.content)} bytes)")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Failed image {i+1}: {e}")
                continue
        
        return downloaded
    
    def save_product_data(self, product_data, product_folder):
        """Save comprehensive product data with VPS paths"""
        data_file = os.path.join(product_folder, 'product_data.json')
        
        # Ensure all paths are VPS paths
        if 'product_folder' in product_data:
            product_data['product_folder'] = product_folder
        if 'images_folder' in product_data:
            product_data['images_folder'] = os.path.join(product_folder, 'images')
        
        # Save JSON
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)
        
        # Save text files
        text_files = {
            'description.txt': product_data.get('description', ''),
            'short_description.txt': product_data.get('short_description', ''),
            'title.txt': product_data.get('title', ''),
            'price.txt': product_data.get('price', '')
        }
        
        for filename, content in text_files.items():
            file_path = os.path.join(product_folder, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"  ✓ Saved product data and text files")
        return data_file
    
    def process_single_product(self, url, scrape_source="unknown"):
        """Process one product with source-aware duplicate checking"""
        # Source-specific duplicate checking
        if scrape_source == "custom":
            existing_products = self.get_existing_products("custom")
        else:
            existing_products = self.get_existing_products()
        
        if url in existing_products:
            print(f"  Skipping (already scraped): {url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]}")
            return None
        
        print(f"Processing: {url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]}")
        
        soup = self.scraper_core.scrape_product_page(url)
        product_data = self.scraper_core.extract_product_data(soup, url)
        
        if not product_data:
            print("  Failed to extract product data")
            return None
        
        print(f"  Product: {product_data['title'][:50]}...")
        
        # Create folders using utility function
        product_folder, images_folder, safe_name = create_product_folders(
            product_data['title'], self.products_dir
        )
        
        # Check existing images
        existing_images = []
        if os.path.exists(images_folder):
            existing_images = [f for f in os.listdir(images_folder) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))]
        
        if existing_images:
            print(f"  Found {len(existing_images)} existing images")
            local_images = [os.path.join(images_folder, img) for img in existing_images]
            image_urls = []
        else:
            image_urls = self.scraper_core.extract_image_urls(soup, url)
            local_images = self.download_images(image_urls, images_folder)
        
        # Update product data with VPS paths and source tracking
        product_data.update({
            'product_folder': product_folder,
            'images_folder': images_folder,
            'safe_name': safe_name,
            'image_urls': image_urls,
            'local_images': local_images,
            'image_count': len(local_images),
            'scrape_source': scrape_source
        })
        
        self.save_product_data(product_data, product_folder)
        
        print(f"  Total images: {len(local_images)}")
        return product_data
    
    def get_product_urls(self, category, limit=None):
        """Get product URLs with source-aware duplicate prevention"""
        existing_products = self.get_existing_products(category)
        
        if category == 'best_sellers':
            url = "https://ineedhemp.com/product-category/best-sellers/"
            links = self.scraper_core.get_product_urls_from_page(url, limit)
            
            new_links = [url for url in links if url not in existing_products]
            skipped = len(links) - len(new_links)
            
            print(f"Found {len(new_links)} new best sellers (skipped {skipped} existing)")
            return new_links
            
        elif category == 'featured':
            url = "https://ineedhemp.com/featured-products/"
            links = self.scraper_core.get_product_urls_from_page(url, limit or 20)
            
            new_links = [url for url in links if url not in existing_products]
            skipped = len(links) - len(new_links)
            
            print(f"Found {len(new_links)} new featured products (skipped {skipped} existing)")
            return new_links
        
        return []
    
    def scrape_custom_url(self, url):
        """Custom URL scraper that allows re-scraping products from other sources"""
        print(f"Custom URL Scraper")
        print("=" * 40)
        
        # Validate and clean URL
        if not url.startswith('http'):
            if url.startswith('/'):
                url = 'https://ineedhemp.com' + url
            else:
                url = 'https://' + url
        
        # Validate product URL
        if not self.scraper_core.is_valid_product_url(url):
            print(f"Warning: This doesn't appear to be a valid product URL")
        
        # Only check if this URL was already scraped as a custom URL
        existing_custom_products = self.get_existing_products("custom")
        if url in existing_custom_products:
            print(f"Product already scraped as custom URL - will re-scrape anyway")
        
        return [url]
    
    def scrape_products(self, urls, mode_name):
        """Scrape multiple products with source tracking"""
        if not urls:
            print("No URLs to scrape!")
            return []
        
        print(f"{mode_name}: {len(urls)} products")
        print("=" * 50)
        
        all_products = []
        successful = 0
        failed = 0
        
        # Determine scrape source
        if "Best Sellers" in mode_name:
            scrape_source = "best_sellers"
        elif "Featured" in mode_name:
            scrape_source = "featured"
        elif "Custom" in mode_name:
            scrape_source = "custom"
        else:
            scrape_source = "unknown"
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}]", end=" ")
            
            product = self.process_single_product(url, scrape_source)
            if product:
                all_products.append(product)
                successful += 1
            else:
                failed += 1
            
            # Progress update
            if i % 5 == 0 or i == len(urls):
                print(f"  Progress: {successful} successful, {failed} failed")
            
            time.sleep(1)
        
        # Add to master database
        if all_products:
            self.database.add_products(all_products)
        
        print(f"Complete! {successful} products scraped successfully")
        print(f"Failed: {failed}")
        
        return all_products
    
    def show_database_stats(self):
        """Display database statistics"""
        self.database.show_database_stats()
    
    def delete_product_completely(self, product_index):
        """Completely delete a product including files"""
        try:
            products = self.database.load_products()
            
            if product_index < 0 or product_index >= len(products):
                print("Invalid product index")
                return False
            
            product = products[product_index]
            
            # Delete product folder and contents
            if 'product_folder' in product and product['product_folder']:
                product_folder = product['product_folder']
                if os.path.exists(product_folder):
                    import shutil
                    shutil.rmtree(product_folder)
                    print(f"✓ Deleted product folder: {product_folder}")
            
            # Remove from database
            success, deleted_product = self.database.delete_product(product_index)
            
            if success:
                print(f"✓ Completely deleted product '{deleted_product.get('title', 'Unknown')}'")
                return True
            else:
                print(f"❌ Failed to delete from database")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting product: {e}")
            return False

def main():
    """Main function for command line usage"""
    scraper = CleanProductScraper()
    
    print("UNIFIED SCRAPER v3.0 - REDUCED VERSION")
    print("=" * 50)
    print("✓ Utilities moved to separate modules")
    print("✓ All paths work with Flask web app")
    print("✓ Source-aware duplicate checking")
    if ENHANCED_IMAGES:
        print("✓ Enhanced image processing active")
    else:
        print("⚠ Basic image processing")
    print()
    print("1. Scrape Top 15 Best Sellers")
    print("2. Scrape Featured Products (Max 20)")
    print("3. Custom URL Scraper")
    print("4. Show Database Stats") 
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            urls = scraper.get_product_urls('best_sellers', 15)
            if urls:
                scraper.scrape_products(urls, "Best Sellers (Top 15)")
            else:
                print("No new best sellers found!")
            break
            
        elif choice == '2':
            urls = scraper.get_product_urls('featured', 20)
            if urls:
                scraper.scrape_products(urls, "Featured Products (Max 20)")
            else:
                print("No new featured products found!")
            break
            
        elif choice == '3':
            url = input("Enter product URL: ").strip()
            if url:
                urls = scraper.scrape_custom_url(url)
                if urls:
                    scraper.scrape_products(urls, "Custom URL")
            break
            
        elif choice == '4':
            scraper.show_database_stats()
                
        elif choice == '5':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()