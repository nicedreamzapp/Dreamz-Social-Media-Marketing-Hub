#!/usr/bin/env python3
"""
CGI entry point for Divine Tribe Marketing Hub
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# CGI setup
print("Content-Type: text/html\n")

try:
    # Import your existing Flask app
    from flask_wrapper import app
    
    # Test if app loads
    with app.test_client() as client:
        response = client.get('/')
        print(response.get_data(as_text=True))
        
except Exception as e:
    print(f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")