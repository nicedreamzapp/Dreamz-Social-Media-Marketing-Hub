"""
Facebook Post Generator - Based on Instagram Generator
Keeps original image aspect ratios and uses Facebook-optimized prompts
"""

import json
import os
from datetime import datetime
from PIL import Image
from pathlib import Path
from path_utils import slugify

class FacebookImageProcessor:
    """Handles image processing for Facebook - keeps original aspect ratios"""
    
    def __init__(self):
        # Facebook allows various sizes, so we'll use a reasonable max
        self.max_width = 1200
        self.max_height = 1200
        self.quality = 95
        
    def process_single_image(self, input_path, output_path):
        """Process image for Facebook - maintain aspect ratio, resize if too large"""
        if not os.path.exists(input_path):
            print(f"    Image not found: {input_path}")
            return None
        
        if os.path.exists(output_path):
            print(f"    Skipping existing: {os.path.basename(output_path)}")
            return output_path
        
        try:
            image = Image.open(input_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get original dimensions
            original_width, original_height = image.size
            
            # Only resize if image is too large
            if original_width > self.max_width or original_height > self.max_height:
                # Calculate scale to fit within max dimensions while maintaining aspect ratio
                scale = min(self.max_width / original_width, self.max_height / original_height)
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"    Resized: {original_width}x{original_height} -> {new_width}x{new_height}")
            else:
                print(f"    No resize needed: {original_width}x{original_height}")
            
            image.save(output_path, 'JPEG', quality=self.quality)
            print(f"    Processed: {os.path.basename(output_path)}")
            return output_path
            
        except Exception as e:
            print(f"    Error processing image {input_path}: {e}")
            return None
    
    def fix_path_for_current_system(self, path_str):
        """Convert Mac/Windows paths to VPS paths"""
        if not path_str:
            return None
            
        # Convert to string if Path object
        path_str = str(path_str)
        
        # Handle Mac paths: /Users/matthewmacosko/Desktop/ad-generator/data/products/...
        if '/Users/matthewmacosko/Desktop/ad-generator/' in path_str:
            relative_part = path_str.split('/ad-generator/', 1)[1]
            vps_path = os.path.join('/var/www/tools', relative_part)
            print(f"    Converted Mac path: {path_str} -> {vps_path}")
            return vps_path
        
        # Handle other Mac variations
        if '/Users/matthewmacosko/' in path_str and 'data/' in path_str:
            parts = path_str.split('data/', 1)
            if len(parts) > 1:
                vps_path = f'/var/www/tools/data/{parts[1]}'
                print(f"    Converted Mac path variation: {path_str} -> {vps_path}")
                return vps_path
        
        # Handle Windows paths: C:\Users\...\data\products\...
        if ':\\' in path_str and 'data' in path_str:
            parts = path_str.replace('\\', '/').split('/')
            if 'data' in parts:
                data_index = parts.index('data')
                relative_parts = parts[data_index:]
                vps_path = '/var/www/tools/' + '/'.join(relative_parts)
                print(f"    Converted Windows path: {path_str} -> {vps_path}")
                return vps_path
        
        # If already a VPS path, use as-is
        if path_str.startswith('/var/www/tools/'):
            return path_str
        
        # If it's a relative path, make it absolute to VPS
        if not os.path.isabs(path_str):
            vps_path = os.path.join('/var/www/tools', path_str)
            return vps_path
        
        # If it's already a valid absolute path for VPS, use it
        if os.path.exists(path_str):
            return path_str
        
        # Last resort: try to extract filename and look in VPS data/products
        filename = os.path.basename(path_str)
        if filename:
            # Try to find the file in VPS data/products structure
            for root, dirs, files in os.walk('/var/www/tools/data/products'):
                if filename in files:
                    found_path = os.path.join(root, filename)
                    print(f"    Found image by search: {found_path}")
                    return found_path
        
        print(f"    Could not convert path: {path_str}")
        return None
    
    def process_all_product_images(self, product):
        """Process ALL images for a product with VPS path handling"""
        
        # Build stable slug and discover images
        product_title = product.get('title', 'Unknown Product')
        slug = slugify(product_title)
        safe_title = slug if slug != 'unknown' else 'unknown_product'
        
        print(f"[FB IMG] Processing images for: {product_title}")
        print(f"[FB IMG] Slug: {slug}")
        
        # Get original images from product data
        original_images = product.get('local_images', [])
        if not original_images:
            single_image = product.get('local_image')
            if single_image:
                original_images = [single_image]
        
        print(f"[FB IMG] Found {len(original_images)} original image paths")
        
        # Convert paths to work with VPS system
        valid_images = []
        for i, image_path in enumerate(original_images):
            fixed_path = self.fix_path_for_current_system(image_path)
            if fixed_path and os.path.exists(fixed_path):
                valid_images.append(fixed_path)
                print(f"[FB IMG] Valid image {i+1}: {os.path.basename(fixed_path)}")
            else:
                print(f"[FB IMG] Invalid image {i+1}: {image_path}")
        
        if not valid_images:
            print("[FB IMG] No valid images found after path conversion")
            return None
        
        # Create Facebook folder in VPS temp structure
        product_fb_folder = Path('/var/www/tools/temp_ads') / 'facebook' / slug
        product_fb_folder.mkdir(parents=True, exist_ok=True)
        
        existing_processed = self.get_existing_processed_images(str(product_fb_folder))
        processed_images = []
        
        print(f"[FB IMG] Processing {len(valid_images)} images for Facebook format...")
        
        for i, image_path in enumerate(valid_images):
            if i == 0:
                fb_filename = f"{slug}_main_facebook.jpg"
            else:
                fb_filename = f"{slug}_{i+1}_facebook.jpg"
            
            fb_output_path = product_fb_folder / fb_filename
            
            if fb_filename in existing_processed:
                print(f"    Using existing: {fb_filename}")
                processed_images.append(str(fb_output_path))
                continue
            
            processed_path = self.process_single_image(image_path, str(fb_output_path))
            if processed_path:
                processed_images.append(processed_path)
        
        result_data = {
            'product_folder': str(product_fb_folder),
            'processed_images': processed_images,
            'main_image': processed_images[0] if processed_images else None,
            'total_processed': len(processed_images),
            'safe_product_name': safe_title
        }
        
        print(f"[FB IMG] Completed processing: {len(processed_images)} Facebook images")
        return result_data
    
    def get_existing_processed_images(self, folder):
        """Check for existing processed images"""
        existing = set()
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.lower().endswith('_facebook.jpg'):
                    existing.add(filename)
        return existing

class FacebookGenerator:
    """Facebook post generator with interactive ChatGPT prompts"""
    
    def __init__(self):
        self.image_processor = FacebookImageProcessor()
        # Use VPS paths
        os.makedirs('/var/www/tools/temp_ads/facebook', exist_ok=True)
        
    def extract_product_text_for_chatgpt(self, product):
        """Extract all product text for ChatGPT to work with"""
        title = product.get('title', '')
        description = product.get('description', '')
        short_description = product.get('short_description', '')
        price = product.get('price', '')
        category = product.get('category', '')
        
        # Combine all product information for ChatGPT
        product_text_parts = []
        
        if title:
            product_text_parts.append(f"TITLE: {title}")
        
        if price and price not in ["Contact for pricing", "$0.00", "Free"]:
            product_text_parts.append(f"PRICE: {price}")
        
        if category and category != "Uncategorized":
            product_text_parts.append(f"CATEGORY: {category}")
        
        if description:
            product_text_parts.append(f"DESCRIPTION: {description}")
        elif short_description:
            product_text_parts.append(f"DESCRIPTION: {short_description}")
        
        # Join all parts with line breaks
        full_product_text = '\n\n'.join(product_text_parts)
        
        print(f"Extracted product text for ChatGPT ({len(full_product_text)} characters)")
        return full_product_text
    
    def generate_facebook_post(self, product_index, products):
        """Process images and extract text for Facebook post"""
        if product_index >= len(products):
            print("Invalid product index")
            return None
        
        product = products[product_index]
        
        print(f"Preparing Facebook post for: {product.get('title', 'Unknown')[:50]}...")
        
        # Process images with VPS path handling (keeps aspect ratios)
        image_data = self.image_processor.process_all_product_images(product)
        
        if not image_data or not image_data.get('processed_images'):
            print("Warning: No images processed for Facebook")
            # Continue anyway - we can still extract text
        
        # Extract the product text for ChatGPT
        product_text = self.extract_product_text_for_chatgpt(product)
        
        # Create post data with RAW PRODUCT TEXT
        image_count = image_data.get('total_processed', 0) if image_data else 0
        
        post_data = {
            'product_title': product.get('title', 'Unknown Product'),
            'product_url': product.get('url', ''),
            'caption': product_text,  # RAW PRODUCT TEXT - ChatGPT will work with this
            'main_image_path': image_data.get('main_image') if image_data else None,
            'all_facebook_images': image_data.get('processed_images', []) if image_data else [],
            'product_facebook_folder': image_data.get('product_folder') if image_data else None,
            'original_images': product.get('local_images', []),
            'generated_at': datetime.now().isoformat(),
            'platform': 'facebook',
            'character_count': len(product_text),
            'hashtag_count': 0,  # No hashtags generated - ChatGPT will add them
            'total_images_processed': image_count,
            'safe_product_name': image_data.get('safe_product_name') if image_data else 'unknown',
            'image_format': 'original_aspect_ratio'
        }
        
        print(f"Facebook post prepared (text extraction only):")
        print(f"  - Raw product text: {post_data['character_count']} characters")
        print(f"  - Images processed: {image_count}")
        print(f"  - Ready for ChatGPT processing")
        
        return post_data
    
    def save_post_data(self, post_data):
        """Save post data to VPS folder"""
        if not post_data:
            print("No post data to save")
            return None
        
        product_folder = post_data.get('product_facebook_folder')
        if not product_folder:
            # Create a basic folder if images weren't processed
            safe_name = post_data.get('safe_product_name', 'unknown')
            product_folder = os.path.join('/var/www/tools/temp_ads', 'facebook', safe_name)
            os.makedirs(product_folder, exist_ok=True)
            post_data['product_facebook_folder'] = product_folder
        
        product_json = os.path.join(product_folder, 'post_data.json')
        product_txt = os.path.join(product_folder, 'raw_product_text.txt')
        
        try:
            with open(product_json, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)
            
            with open(product_txt, 'w', encoding='utf-8') as f:
                f.write(post_data['caption'])  # This is the raw product text
            
            print(f"Facebook post data saved:")
            print(f"  - JSON: {product_json}")
            print(f"  - Raw text: {product_txt}")
            
            return {
                'json_file': product_json,
                'text_file': product_txt,
                'images_folder': post_data.get('product_facebook_folder'),
                'main_image': post_data.get('main_image_path'),
                'all_images': post_data.get('all_facebook_images', [])
            }
            
        except Exception as e:
            print(f"Error saving Facebook post data: {e}")
            return None

def load_products():
    """Load products from VPS data path"""
    try:
        # Use VPS path
        products_file = '/var/www/tools/data/products_master.json'
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        if not isinstance(products, list):
            print("Invalid product data format")
            return []
        
        valid_products = [p for p in products if isinstance(p, dict) and p.get('title')]
        print(f"Loaded {len(valid_products)} valid products for Facebook generation")
        
        return valid_products
        
    except FileNotFoundError:
        print("No products found. Please run the scraper first.")
        return []
    except json.JSONDecodeError:
        print("Invalid JSON in products file")
        return []
    except Exception as e:
        print(f"Error loading products: {e}")
        return []

if __name__ == "__main__":
    # Test the Facebook generator
    generator = FacebookGenerator()
    products = load_products()
    
    if products:
        # Test with first product
        post_data = generator.generate_facebook_post(0, products)
        if post_data:
            generator.save_post_data(post_data)
            print("\nRaw Product Text for ChatGPT:")
            print("-" * 40)
            print(post_data['caption'])
            print("-" * 40)
            print("This text will be sent to ChatGPT to create the Facebook post.")

