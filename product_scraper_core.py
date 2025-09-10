"""
Product Scraper Core - Universal WooCommerce scraping logic
Handles URL fetching, HTML parsing, and product data extraction for any WooCommerce site
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

class ProductScraperCore:
    def __init__(self, headers=None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Supported domains - your WooCommerce sites
        self.supported_domains = [
            'ineedhemp.com',
            'nicedreamzwholesale.com', 
            'tribeseedbank.com'
        ]
    
    def get_domain_from_url(self, url):
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return None
    
    def is_supported_domain(self, url):
        """Check if URL is from a supported domain"""
        domain = self.get_domain_from_url(url)
        return domain in self.supported_domains
    
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
            'scraper_version': '3.0-universal',
            'domain': self.get_domain_from_url(url)
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
        """Extract FULL product description"""
        
        full_description_selectors = [
            '#tab-description',
            '.woocommerce-Tabs-panel--description',
            '.panel.entry-content',
            '.wc-tab#tab-description',
            'div[id*="description"] .panel',
            '.product-description .entry-content',
            '.woocommerce-product-details__description',
            '.product-details-description',
            '.product-content .entry-content',
            '.single-product-summary .entry-content',
            '.product-tabs .description .panel',
            '.tab-content .description',
            '[role="tabpanel"][id*="description"]',
            '.product-description-content',
            '.woocommerce-product-details .entry-content'
        ]
        
        for selector in full_description_selectors:
            element = soup.select_one(selector)
            if element:
                desc_text = element.get_text(separator=' ', strip=True)
                
                if desc_text and len(desc_text) > 50:
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
        
        return "Premium quality product"
    
    def clean_description_text(self, description):
        """Clean and normalize description text"""
        if not description:
            return "Premium quality product"
        
        clean_text = ' '.join(description.split())
        
        import html
        clean_text = html.unescape(clean_text)
        
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
        domain = self.get_domain_from_url(base_url)
        
        selectors = [
            'img[data-large_image]',
            'img.wp-post-image',
            '.woocommerce-product-gallery img',
            '.product-images img',
            'img[data-src]',
            'img[src*="product"]',
            '.product-image img',
            '.single-product-main-image img',
            'figure.woocommerce-product-gallery__wrapper img'
        ]
        
        for selector in selectors:
            for img in soup.select(selector):
                for attr in ['data-large_image', 'data-src', 'src']:
                    src = img.get(attr)
                    if src:
                        src = self.clean_image_url(src, base_url, domain)
                        if src and src not in seen and self.is_valid_image_url(src, domain):
                            images.append(src)
                            seen.add(src)
                        break
        
        print(f"  Found {len(images)} valid images")
        return images
    
    def clean_image_url(self, url, base_url, domain):
        """Clean and normalize image URL - now domain-agnostic"""
        if not url:
            return None
        
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            url = f'https://{domain}' + url
        elif not url.startswith('http'):
            url = urljoin(base_url, url)
        
        if '?' in url:
            url = url.split('?')[0]
        
        return url
    
    def is_valid_image_url(self, url, domain):
        """Validate image URL - now supports all your domains"""
        if not url:
            return False
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(ext in url.lower() for ext in valid_extensions):
            return False
        
        exclude_terms = ['logo', 'favicon', 'placeholder', 'loading', 'spinner']
        if any(term in url.lower() for term in exclude_terms):
            return False
        
        # Check if it's from the expected domain
        if domain not in url:
            return False
        
        return True
    
    def get_product_urls_from_page(self, page_url, limit=None):
        """Extract product URLs from a category or listing page"""
        try:
            response = requests.get(page_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            domain = self.get_domain_from_url(page_url)
            
            product_selectors = [
                'ul.products li.product a',
                '.wc-block-grid__product a',
                'article.product a',
                '.product-item a',
                'li.type-product a',
                '.woocommerce-loop-product__link',
                'a[href*="/product/"]'
            ]
            
            for selector in product_selectors:
                page_links = soup.select(selector)
                
                if page_links:
                    print(f"Found {len(page_links)} product links with selector: {selector}")
                    
                    for link in page_links:
                        href = link.get('href')
                        if href:
                            href = self.clean_product_url(href, domain)
                            
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
    
    def clean_product_url(self, url, domain):
        """Clean and normalize product URL - now domain-agnostic"""
        if not url:
            return None
        
        if url.startswith('/'):
            url = f'https://{domain}' + url
        elif not url.startswith('http'):
            url = f'https://{domain}/' + url
        
        url = url.split('?')[0].split('#')[0]
        
        return url
    
    def is_valid_product_url(self, url):
        """Validate product URL - now supports all your domains"""
        if not url:
            return False
        
        # Check if it's from a supported domain
        if not self.is_supported_domain(url):
            return False
        
        return ('/product/' in url and 
                not url.endswith('/product/') and
                not any(term in url.lower() for term in ['cart', 'checkout', 'account']))