from instagram_generator import InstagramGenerator
from database_manager import ProductDatabase

# Load fresh data
db = ProductDatabase()
products = db.load_products()

if products:
    generator = InstagramGenerator()
    
    # Test first 3 products
    for i in range(min(3, len(products))):
        print(f"\n=== PRODUCT {i} ===")
        print(f"Title: {products[i].get('title', 'No title')[:50]}...")
        
        post_data = generator.generate_instagram_post(i, products)
        if post_data:
            caption = post_data.get('caption', '')
            print(f"Caption length: {len(caption)}")
            print(f"Caption preview: {caption[:100]}...")
            print(f"Product in caption: {'TITLE:' in caption}")
        else:
            print("No post data generated")
