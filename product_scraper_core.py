"""
Product Scraper Core - Main scraping logic and data extraction
Handles URL fetching, HTML parsing, and product data extraction
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import time
from datetime import datetime
from urllib.parse import urljoin

class ProductScraperCore:
    def __init__(self, headers=None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def scrape_product_page(self, url):
        """Scrape single product page with enhanced error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error scraping {url}: {e}")
            return None
    
    def extract_product_data(self, soup, url):
        """Extract comprehensive product data"""
        if not soup:
            return None
        
        title = self.extract_title(soup)
        if not title or len(title) < 3:
            return None
        
        return {
            'url': url,
            'title': title,
            'description': self.extract_description(soup),
            'short_description': self.extract_short_description(soup),
            'price': self.extract_price(soup),
            'category': self.extract_category(soup),
            'sku': self.extract_sku(soup),
            'scraped_at': datetime.now().isoformat(),
            'scraper_version': '2.2'
        }
    
    def extract_title(self, soup):
        """Extract product title with multiple selectors"""
        selectors = [
            'h1.product_title',
            'h1.entry-title', 
            'h1.product-title',
            '.product_title',
            'h1',
            '.page-title h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if (title and len(title) > 2 and 
                    not any(word in title.lower() for word in ['error', '404', 'not found', 'page not found'])):
                    return title
        return None
    
    def extract_description(self, soup):
        """FIXED: Extract FULL product description (not just short description)"""
        
        # Priority 1: Full description selectors (usually in tabs or separate sections)
        full_description_selectors = [
            '#tab-description',  # WooCommerce description tab content
            '.woocommerce-Tabs-panel--description',  # WooCommerce description panel
            '.panel.entry-content',  # Description panel content
            '.wc-tab#tab-description',  # Alternative tab format
            'div[id*="description"] .panel',  # Description panel variations
            '.product-description .entry-content',  # Full description in content area
            '.woocommerce-product-details__description',  # Full description wrapper
            '.product-details-description',  # Custom theme descriptions
            '.product-content .entry-content',  # Entry content in product area
            '.single-product-summary .entry-content',  # Single product content
            '.product-tabs .description .panel',  # Tabbed description content
            '.tab-content .description',  # Tab content description
            '[role="tabpanel"][id*="description"]',  # ARIA description panels
            '.product-description-content',  # Generic description content
            '.woocommerce-product-details .entry-content'  # WooCommerce entry content
        ]
        
        # Try full description selectors first
        for selector in full_description_selectors:
            element = soup.select_one(selector)
            if element:
                # Get all text content, preserving structure
                desc_text = element.get_text(separator=' ', strip=True)
                
                # Clean and validate
                if desc_text and len(desc_text) > 50:  # Must be substantial content
                    # Remove common junk text
                    if not any(junk in desc_text.lower() for junk in ['lorem ipsum', 'placeholder', 'test content']):
                        print(f"  Found FULL description: {len(desc_text)} chars using {selector}")
                        return self.clean_description_text(desc_text)
        
        print("  WARNING: Could not find full description, falling back to short description")
        return self.extract_short_description(soup)
    
    def extract_short_description(self, soup):
        """Extract short description as fallback"""
        selectors = [
            'div.woocommerce-product-details__short-description',
            '.product-description',
            '.entry-summary .woocommerce-product-details__short-description',
            '.product-short-description',
            '.summary .woocommerce-product-details__short-description p'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if len(desc) > 20:
                    return self.clean_description_text(desc)
        
        return "Premium quality product from Divine Tribe"
    
    def clean_description_text(self, description):
        """Clean and normalize description text"""
        if not description:
            return "Premium quality product"
        
        # Remove extra whitespace and normalize
        clean_text = ' '.join(description.split())
        
        # Remove HTML entities
        import html
        clean_text = html.unescape(clean_text)
        
        # Don't truncate - keep full description
        return clean_text
    
    def extract_price(self, soup):
        """Extract price with enhanced selectors"""
        selectors = [
            '.price .woocommerce-Price-amount',
            '.price .amount',
            '.price',
            '.product-price',
            '.woocommerce-Price-amount bdi',
            'span.woocommerce-Price-amount'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = element.get_text(strip=True)
                if '$' in price or '€' in price or '£' in price:
                    return price
        
        return "Contact for pricing"
    
    def extract_category(self, soup):
        """Extract product category"""
        selectors = [
            '.woocommerce-breadcrumb a',
            '.breadcrumb a',
            '.product_meta .posted_in a'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and text.lower() not in ['home', 'shop', 'products']:
                    return text
        
        return "Uncategorized"
    
    def extract_sku(self, soup):
        """Extract product SKU"""
        selectors = [
            '.sku',
            '.product_meta .sku',
            '[data-sku]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                sku = element.get_text(strip=True)
                if sku and sku.lower() != 'n/a':
                    return sku
        
        return None
    
    def extract_image_urls(self, soup, base_url):
        """Extract image URLs with enhanced selectors"""
        images = []
        seen = set()
        
        # Enhanced image selectors for WooCommerce
        selectors = [
            'img[data-large_image]',  # WooCommerce large images
            'img.wp-post-image',  # WordPress post images
            '.woocommerce-product-gallery img',  # Gallery images
            '.product-images img',  # Product image containers
            'img[data-src]',  # Lazy loaded images
            'img[src*="product"]',  # Any product images
            '.product-image img',  # Product image wrappers
            '.single-product-main-image img',  # Main product images
            'figure.woocommerce-product-gallery__wrapper img'  # Gallery wrapper images
        ]
        
        for selector in selectors:
            for img in soup.select(selector):
                # Try multiple attributes for image source
                for attr in ['data-large_image', 'data-src', 'src']:
                    src = img.get(attr)
                    if src:
                        src = self.clean_image_url(src, base_url)
                        if src and src not in seen and self.is_valid_image_url(src):
                            images.append(src)
                            seen.add(src)
                        break
        
        print(f"  Found {len(images)} valid images")
        return images
    
    def clean_image_url(self, url, base_url):
        """Clean and normalize image URL"""
        if not url:
            return None
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        # Handle relative URLs
        elif url.startswith('/'):
            url = 'https://ineedhemp.com' + url
        elif not url.startswith('http'):
            url = urljoin(base_url, url)
        
        # Remove query parameters for cleaner URLs
        if '?' in url:
            url = url.split('?')[0]
        
        return url
    
    def is_valid_image_url(self, url):
        """Validate image URL"""
        if not url:
            return False
        
        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(ext in url.lower() for ext in valid_extensions):
            return False
        
        # Exclude unwanted images
        exclude_terms = ['logo', 'favicon', 'placeholder', 'loading', 'spinner']
        if any(term in url.lower() for term in exclude_terms):
            return False
        
        # Must be from the main domain
        if 'ineedhemp.com' not in url:
            return False
        
        return True
    
    def get_product_urls_from_page(self, page_url, limit=None):
        """Extract product URLs from a category or listing page"""
        try:
            response = requests.get(page_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            
            # Multiple selectors for different page layouts
            product_selectors = [
                'ul.products li.product a',           # WooCommerce product grid
                '.wc-block-grid__product a',          # Block editor products
                'article.product a',                  # Article-based products
                '.product-item a',                    # Custom theme products
                'li.type-product a',                  # WordPress product post type
                '.woocommerce-loop-product__link',    # WooCommerce loop links
                'a[href*="/product/"]'                # Any link containing /product/
            ]
            
            for selector in product_selectors:
                page_links = soup.select(selector)
                
                if page_links:
                    print(f"Found {len(page_links)} product links with selector: {selector}")
                    
                    for link in page_links:
                        href = link.get('href')
                        if href:
                            href = self.clean_product_url(href)
                            
                            if (href and self.is_valid_product_url(href) and 
                                href not in links):
                                links.append(href)
                                
                                if limit and len(links) >= limit:
                                    break
                    
                    if links:
                        break
            
            return links[:limit] if limit else links
            
        except Exception as e:
            print(f"Error extracting URLs from {page_url}: {e}")
            return []
    
    def clean_product_url(self, url):
        """Clean and normalize product URL"""
        if not url:
            return None
        
        # Make absolute URL
        if url.startswith('/'):
            url = 'https://ineedhemp.com' + url
        elif not url.startswith('http'):
            url = 'https://ineedhemp.com/' + url
        
        # Remove parameters and fragments
        url = url.split('?')[0].split('#')[0]
        
        return url
    
    def is_valid_product_url(self, url):
        """Validate product URL"""
        if not url:
            return False
        
        return ('/product/' in url and 
                'ineedhemp.com' in url and 
                not url.endswith('/product/') and
                not any(term in url.lower() for term in ['cart', 'checkout', 'account']))