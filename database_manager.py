"""
Database Manager - Universal WooCommerce Product Database
Handles product data storage, retrieval, and management across multiple sites
"""
import json
import os
from datetime import datetime
from pathlib import Path

class ProductDatabase:
    """Enhanced product database with multi-site support and better organization"""
    
    def __init__(self, database_file='/var/www/tools/data/products_master.json'):
        self.database_file = database_file
        self.backup_dir = Path('/var/www/tools/data/backups')
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(database_file), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Initialize database if it doesn't exist
        if not os.path.exists(self.database_file):
            self.initialize_database()
        
        print(f"✅ Database manager initialized: {self.database_file}")
    
    def initialize_database(self):
        """Initialize empty database with metadata"""
        initial_data = {
            'metadata': {
                'version': '3.0-universal',
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'total_products': 0,
                'supported_sites': [
                    'ineedhemp.com',
                    'nicedreamzwholesale.com', 
                    'tribeseedbank.com'
                ]
            },
            'products': []
        }
        
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Initialized new database: {self.database_file}")
    
    def create_backup(self):
        """Create a timestamped backup of the current database"""
        try:
            if not os.path.exists(self.database_file):
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"products_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Copy current database to backup
            import shutil
            shutil.copy2(self.database_file, backup_path)
            
            # Keep only the last 10 backups
            self.cleanup_old_backups()
            
            print(f"✅ Database backup created: {backup_filename}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return None
    
    def cleanup_old_backups(self, keep_count=10):
        """Remove old backups, keeping only the most recent ones"""
        try:
            backup_files = list(self.backup_dir.glob("products_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                print(f"🗑️ Removed old backup: {old_backup.name}")
                
        except Exception as e:
            print(f"❌ Backup cleanup failed: {e}")
    
    def load_database(self):
        """Load complete database with error handling - supports both old and new formats"""
        try:
            if not os.path.exists(self.database_file):
                self.initialize_database()
            
            with open(self.database_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle old format (simple array) vs new format (metadata wrapper)
            if isinstance(data, list):
                # Old format - convert to new format
                print(f"✅ Converting old database format with {len(data)} products")
                converted_data = {
                    'metadata': {
                        'version': '3.0-universal',
                        'created': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat(),
                        'total_products': len(data)
                    },
                    'products': data
                }
                # Save in new format
                self.save_database(converted_data)
                return converted_data
            else:
                # New format - validate structure
                if 'products' not in data:
                    data['products'] = []
                if 'metadata' not in data:
                    data['metadata'] = {
                        'version': '3.0-universal',
                        'created': datetime.now().isoformat(),
                        'last_updated': datetime.now().isoformat(),
                        'total_products': len(data['products'])
                    }
                return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Database JSON error: {e}")
            self.create_backup()
            self.initialize_database()
            return self.load_database()
        except Exception as e:
            print(f"❌ Database load error: {e}")
            return {'metadata': {}, 'products': []}
    
    def save_database(self, data):
        """Save complete database with backup"""
        try:
            # Create backup before saving (but only if file exists and has content)
            if os.path.exists(self.database_file) and os.path.getsize(self.database_file) > 0:
                self.create_backup()
            
            # Update metadata
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['last_updated'] = datetime.now().isoformat()
            data['metadata']['total_products'] = len(data.get('products', []))
            
            # Save to file
            with open(self.database_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Database save error: {e}")
            return False
    
    def load_products(self):
        """Load only the products array"""
        database = self.load_database()
        products = database.get('products', [])
        print(f"✅ Loaded {len(products)} products from database")
        return products
    
    def save_products(self, products):
        """Save products array to database"""
        database = self.load_database()
        database['products'] = products
        return self.save_database(database)
    
    def add_products(self, new_products):
        """Add new products to database"""
        if not new_products:
            return False
        
        database = self.load_database()
        existing_urls = {product.get('url', '') for product in database['products']}
        
        added_count = 0
        for product in new_products:
            product_url = product.get('url', '')
            if product_url and product_url not in existing_urls:
                # Add metadata for new product
                product['added_to_database'] = datetime.now().isoformat()
                product['database_version'] = '3.0-universal'
                
                database['products'].append(product)
                existing_urls.add(product_url)
                added_count += 1
        
        if added_count > 0:
            success = self.save_database(database)
            if success:
                print(f"✅ Added {added_count} new products to database")
            return success
        else:
            print("ℹ️ No new products to add (all duplicates)")
            return True
    
    def get_existing_products(self, scrape_source=None):
        """Get existing product URLs, optionally filtered by source"""
        products = self.load_products()
        
        if scrape_source:
            # Filter by specific scrape source
            filtered_products = [p for p in products if p.get('scrape_source') == scrape_source]
            urls = {product.get('url', '') for product in filtered_products if product.get('url')}
        else:
            # All products
            urls = {product.get('url', '') for product in products if product.get('url')}
        
        return urls
    
    def delete_product(self, product_index):
        """Delete a product by index"""
        try:
            database = self.load_database()
            products = database['products']
            
            if 0 <= product_index < len(products):
                deleted_product = products.pop(product_index)
                success = self.save_database(database)
                
                if success:
                    return True, deleted_product
                else:
                    return False, None
            else:
                return False, None
                
        except Exception as e:
            print(f"❌ Delete product error: {e}")
            return False, None
    
    def get_products_by_site(self, domain):
        """Get products from a specific site domain"""
        products = self.load_products()
        site_products = []
        
        for product in products:
            product_domain = product.get('domain', '')
            if product_domain == domain:
                site_products.append(product)
            elif not product_domain and domain in product.get('url', ''):
                # Fallback for older products without domain field
                site_products.append(product)
        
        return site_products
    
    def show_database_stats(self):
        """Display comprehensive database statistics"""
        database = self.load_database()
        products = database['products']
        metadata = database.get('metadata', {})
        
        print("\n📊 DATABASE STATISTICS")
        print("=" * 50)
        print(f"Database Version: {metadata.get('version', 'Unknown')}")
        print(f"Last Updated: {metadata.get('last_updated', 'Unknown')}")
        print(f"Total Products: {len(products)}")
        
        # Site breakdown
        site_stats = {}
        source_stats = {}
        
        for product in products:
            # Count by site domain
            domain = product.get('domain', 'Unknown')
            site_stats[domain] = site_stats.get(domain, 0) + 1
            
            # Count by scrape source
            source = product.get('scrape_source', 'Unknown')
            source_stats[source] = source_stats.get(source, 0) + 1
        
        print("\n🌐 Products by Site:")
        for domain, count in sorted(site_stats.items()):
            print(f"  {domain}: {count} products")
        
        print("\n📥 Products by Source:")
        for source, count in sorted(source_stats.items()):
            print(f"  {source}: {count} products")
        
        # Image statistics
        total_images = sum(len(p.get('local_images', [])) for p in products)
        products_with_images = sum(1 for p in products if p.get('local_images'))
        
        print(f"\n📸 Image Statistics:")
        print(f"  Total Images: {total_images}")
        print(f"  Products with Images: {products_with_images}/{len(products)}")
        if products_with_images > 0:
            avg_images = total_images / products_with_images
            print(f"  Average Images per Product: {avg_images:.1f}")
        
        # Recent activity
        recent_products = [p for p in products if 'added_to_database' in p]
        if recent_products:
            recent_products.sort(key=lambda x: x['added_to_database'], reverse=True)
            print(f"\n🆕 Recent Additions (last 5):")
            for product in recent_products[:5]:
                title = product.get('title', 'Unknown')[:40]
                added_date = product.get('added_to_database', '')[:10]  # Just the date part
                domain = product.get('domain', 'Unknown')
                print(f"  {added_date} - {title}... ({domain})")
        
        print("=" * 50)
    
    def search_products(self, query, field='title'):
        """Search products by a specific field"""
        products = self.load_products()
        query_lower = query.lower()
        
        results = []
        for i, product in enumerate(products):
            field_value = product.get(field, '')
            if isinstance(field_value, str) and query_lower in field_value.lower():
                results.append((i, product))
        
        return results
    
    def get_database_health(self):
        """Check database health and integrity"""
        health_report = {
            'status': 'healthy',
            'issues': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            database = self.load_database()
            products = database['products']
            
            # Check for missing required fields
            missing_titles = sum(1 for p in products if not p.get('title'))
            missing_urls = sum(1 for p in products if not p.get('url'))
            
            if missing_titles > 0:
                health_report['issues'].append(f"{missing_titles} products missing titles")
            if missing_urls > 0:
                health_report['issues'].append(f"{missing_urls} products missing URLs")
            
            # Check for duplicate URLs
            urls = [p.get('url', '') for p in products if p.get('url')]
            duplicate_urls = len(urls) - len(set(urls))
            if duplicate_urls > 0:
                health_report['warnings'].append(f"{duplicate_urls} duplicate URLs found")
            
            # Check file paths
            missing_folders = 0
            for product in products:
                folder_path = product.get('product_folder', '')
                if folder_path and not os.path.exists(folder_path):
                    missing_folders += 1
            
            if missing_folders > 0:
                health_report['warnings'].append(f"{missing_folders} products have missing folders")
            
            # Update status
            if health_report['issues']:
                health_report['status'] = 'issues_found'
            elif health_report['warnings']:
                health_report['status'] = 'warnings_found'
            
            # Statistics
            health_report['statistics'] = {
                'total_products': len(products),
                'duplicate_urls': duplicate_urls,
                'missing_folders': missing_folders,
                'database_size_mb': os.path.getsize(self.database_file) / (1024*1024)
            }
            
        except Exception as e:
            health_report['status'] = 'error'
            health_report['issues'].append(f"Database health check failed: {e}")
        
        return health_report

# Test functionality
if __name__ == '__main__':
    print("Database Manager Test")
    print("=" * 30)
    
    # Initialize database
    db = ProductDatabase()
    
    # Show current stats
    db.show_database_stats()
    
    # Show health report
    health = db.get_database_health()
    print(f"\n🏥 Database Health: {health['status']}")
    if health['issues']:
        print("Issues:")
        for issue in health['issues']:
            print(f"  ❌ {issue}")
    if health['warnings']:
        print("Warnings:")
        for warning in health['warnings']:
            print(f"  ⚠️ {warning}")