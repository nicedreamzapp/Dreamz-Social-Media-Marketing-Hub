"""
Database Manager - Handle product database operations
Manages loading, saving, and querying the products database
"""
import json
import os
from path_utils import fix_mac_to_vps_paths, normalize_image_path

class ProductDatabase:
    """Manages the products master database"""
    
    def __init__(self, db_path='/var/www/tools/data/products_master.json'):
        self.db_path = db_path
        self.data_dir = '/var/www/tools/data'
        self.products_dir = '/var/www/tools/data/products'
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.products_dir, exist_ok=True)
    
    def load_products(self):
        """Load products from database with path normalization"""
        try:
            # Try multiple possible locations
            possible_locations = [
                '/var/www/tools/data/products_master.json',
                '/var/www/tools/products/products_master.json',
                '/var/www/tools/products_master.json',
                '/var/www/tools/products.json',
                'data/products_master.json',  # relative fallback
                'products_master.json'
            ]
            
            for master_file in possible_locations:
                if os.path.exists(master_file):
                    with open(master_file, 'r', encoding='utf-8') as f:
                        products = json.load(f)
                    
                    # Fix Mac/Windows paths to VPS paths
                    products = fix_mac_to_vps_paths(products)
                    
                    print(f"✅ Loaded {len(products)} products from {master_file}")
                    print(f"✅ All paths normalized to VPS format")
                    return products
                    
            # If no file found, return empty list
            print("❌ No products file found - starting with empty list")
            return []
            
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            return []
    
    def save_products(self, products):
        """Save products to database"""
        try:
            # Ensure all paths are normalized before saving
            normalized_products = fix_mac_to_vps_paths(products)
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(normalized_products, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(normalized_products)} products to {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving products: {e}")
            return False
    
    def get_existing_products(self, scrape_source=None):
        """Get list of already scraped products with optional source filtering"""
        existing_products = set()
        
        # Check master database
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                    for product in products:
                        if 'url' in product:
                            # If scrape_source filter specified, only check that source
                            if scrape_source:
                                product_source = product.get('scrape_source', 'unknown')
                                if product_source == scrape_source:
                                    existing_products.add(product['url'])
                            else:
                                # No filter - check all (default behavior)
                                existing_products.add(product['url'])
            except:
                pass
        
        # Check individual product folders
        if os.path.exists(self.products_dir):
            for folder_name in os.listdir(self.products_dir):
                folder_path = os.path.join(self.products_dir, folder_name)
                if os.path.isdir(folder_path):
                    data_file = os.path.join(folder_path, 'product_data.json')
                    if os.path.exists(data_file):
                        try:
                            with open(data_file, 'r', encoding='utf-8') as f:
                                product_data = json.load(f)
                                if 'url' in product_data:
                                    if scrape_source:
                                        product_source = product_data.get('scrape_source', 'unknown')
                                        if product_source == scrape_source:
                                            existing_products.add(product_data['url'])
                                    else:
                                        existing_products.add(product_data['url'])
                        except:
                            pass
        
        return existing_products
    
    def add_products(self, new_products):
        """Add new products to the database"""
        try:
            # Load existing products
            existing_products = self.load_products()
            existing_urls = {p.get('url') for p in existing_products}
            
            # Add only new products (avoid duplicates)
            added_count = 0
            for product in new_products:
                if product.get('url') not in existing_urls:
                    existing_products.append(product)
                    added_count += 1
            
            # Save updated database
            success = self.save_products(existing_products)
            
            if success:
                print(f"✅ Added {added_count} new products to database")
                return True
            else:
                print(f"❌ Failed to save updated database")
                return False
                
        except Exception as e:
            print(f"❌ Error adding products: {e}")
            return False
    
    def delete_product(self, product_index):
        """Delete a product from the database"""
        try:
            products = self.load_products()
            
            if 0 <= product_index < len(products):
                deleted_product = products.pop(product_index)
                success = self.save_products(products)
                
                if success:
                    print(f"✅ Deleted product: {deleted_product.get('title', 'Unknown')}")
                    return True, deleted_product
                else:
                    print(f"❌ Failed to save after deletion")
                    return False, None
            else:
                print(f"❌ Invalid product index: {product_index}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error deleting product: {e}")
            return False, None
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
            products = self.load_products()
            
            if not products:
                return {
                    'total_products': 0,
                    'products_with_images': 0,
                    'database_location': self.db_path,
                    'vps_paths': 0,
                    'mac_paths': 0
                }
            
            products_with_images = len([p for p in products if p.get('image_count', 0) > 0])
            
            # Path analysis
            vps_paths = 0
            mac_paths = 0
            for p in products:
                if 'local_images' in p and p['local_images']:
                    if '/var/www/tools/' in p['local_images'][0]:
                        vps_paths += 1
                    elif '/Users/matthewmacosko/' in p['local_images'][0]:
                        mac_paths += 1
            
            # Description analysis
            full_desc_count = len([p for p in products if len(p.get('description', '')) > 100])
            short_desc_count = len([p for p in products if len(p.get('description', '')) <= 100])
            
            # Category breakdown
            categories = {}
            for p in products:
                cat = p.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            # Source breakdown
            sources = {}
            for p in products:
                source = p.get('scrape_source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            # Image statistics
            image_counts = [p.get('image_count', 0) for p in products]
            
            return {
                'total_products': len(products),
                'products_with_images': products_with_images,
                'database_location': self.db_path,
                'vps_paths': vps_paths,
                'mac_paths': mac_paths,
                'full_descriptions': full_desc_count,
                'short_descriptions': short_desc_count,
                'categories': categories,
                'sources': sources,
                'avg_images_per_product': sum(image_counts) / len(image_counts) if image_counts else 0,
                'max_images_single_product': max(image_counts) if image_counts else 0,
                'total_images_downloaded': sum(image_counts) if image_counts else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return None
    
    def show_database_stats(self):
        """Display comprehensive database statistics"""
        stats = self.get_database_stats()
        
        if not stats:
            print("Error getting database statistics")
            return
        
        print(f"\nDatabase Stats:")
        print(f"Total Products: {stats['total_products']}")
        print(f"Products with Images: {stats['products_with_images']}")
        print(f"Database Location: {stats['database_location']}")
        
        print(f"\nPath Analysis:")
        print(f"Products with VPS paths: {stats['vps_paths']}")
        print(f"Products with Mac paths: {stats['mac_paths']}")
        
        print(f"\nDescription Analysis:")
        print(f"Full Descriptions (>100 chars): {stats['full_descriptions']}")
        print(f"Short Descriptions (≤100 chars): {stats['short_descriptions']}")
        
        if stats['avg_images_per_product'] > 0:
            print(f"\nImage Stats:")
            print(f"Average Images per Product: {stats['avg_images_per_product']:.1f}")
            print(f"Max Images in Single Product: {stats['max_images_single_product']}")
            print(f"Total Images Downloaded: {stats['total_images_downloaded']}")
        
        if stats['categories']:
            print(f"\nBy Category:")
            for cat, count in sorted(stats['categories'].items()):
                print(f"  {cat}: {count}")
        
        if stats['sources']:
            print(f"\nBy Source:")
            for source, count in sorted(stats['sources'].items()):
                print(f"  {source}: {count}")

