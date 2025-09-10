"""
Authentication Routes - User login and session management
Handles secure user authentication for the marketing hub
"""
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
import hashlib
import time

def setup_auth_routes(app, users_dict):
    """Setup authentication routes for the Flask app"""
    
    # Store users dictionary for route access
    app.config['AUTH_USERS'] = users_dict
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page and authentication handler"""
        if request.method == 'GET':
            # Show login form - FIXED: removed .name attribute
            return render_template('login.html') if 'login.html' in app.jinja_env.list_templates() else simple_login_form()
        
        # Handle login attempt
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return handle_login_error('Username and password required')
        
        # Check credentials
        if username in app.config['AUTH_USERS'] and app.config['AUTH_USERS'][username] == password:
            session['logged_in'] = True
            session['username'] = username
            session['login_time'] = time.time()
            
            print(f"✓ User '{username}' logged in successfully")
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
        else:
            print(f"❌ Failed login attempt for username: '{username}'")
            return handle_login_error('Invalid username or password')
    
    @app.route('/logout')
    def logout():
        """Logout handler"""
        username = session.get('username', 'Unknown')
        session.clear()
        print(f"✓ User '{username}' logged out")
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/api/auth_status')
    def auth_status():
        """Check authentication status"""
        if 'logged_in' in session:
            return jsonify({
                'authenticated': True,
                'username': session.get('username'),
                'login_time': session.get('login_time')
            })
        else:
            return jsonify({'authenticated': False})
    
    def handle_login_error(message):
        """Handle login errors consistently"""
        if request.is_json:
            return jsonify({'success': False, 'error': message}), 401
        else:
            flash(message, 'error')
            # FIXED: removed .name attribute
            return render_template('login.html') if 'login.html' in app.jinja_env.list_templates() else simple_login_form()
    
    def simple_login_form():
        """Fallback login form if template is missing"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dreamz Marketing Hub - Login</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    margin: 0;
                }
                .login-container { 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                    width: 300px;
                }
                .login-header {
                    text-align: center;
                    margin-bottom: 30px;
                    color: #333;
                }
                .form-group { 
                    margin-bottom: 20px; 
                }
                label { 
                    display: block; 
                    margin-bottom: 5px;
                    color: #555;
                    font-weight: bold;
                }
                input[type="text"], input[type="password"] { 
                    width: 100%; 
                    padding: 12px; 
                    border: 2px solid #ddd; 
                    border-radius: 5px;
                    box-sizing: border-box;
                    font-size: 16px;
                }
                input[type="text"]:focus, input[type="password"]:focus {
                    border-color: #667eea;
                    outline: none;
                }
                button { 
                    width: 100%; 
                    padding: 12px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    border: none; 
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    font-weight: bold;
                }
                button:hover {
                    opacity: 0.9;
                }
                .flash-message {
                    padding: 10px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                    text-align: center;
                }
                .flash-error {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                .flash-success {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="login-header">
                    <h2>🚀 Dreamz Marketing Hub</h2>
                    <p>Universal WooCommerce Tools</p>
                </div>
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message flash-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <form method="POST">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        '''

def create_login_required_decorator():
    """Create a login required decorator"""
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return login_required

def check_session_validity(session_timeout_hours=24):
    """Check if the current session is still valid"""
    if 'logged_in' not in session:
        return False
    
    login_time = session.get('login_time', 0)
    current_time = time.time()
    session_duration = current_time - login_time
    timeout_seconds = session_timeout_hours * 3600
    
    if session_duration > timeout_seconds:
        # Session expired
        session.clear()
        return False
    
    return True

def get_current_user():
    """Get current authenticated user info"""
    if 'logged_in' in session and check_session_validity():
        return {
            'username': session.get('username'),
            'login_time': session.get('login_time'),
            'authenticated': True
        }
    return {'authenticated': False}

def hash_password(password):
    """Simple password hashing (for future use)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify hashed password (for future use)"""
    return hash_password(password) == hashed

# Session management utilities
def extend_session():
    """Extend the current session"""
    if 'logged_in' in session:
        session['login_time'] = time.time()
        return True
    return False

def get_session_info():
    """Get detailed session information"""
    if 'logged_in' not in session:
        return None
    
    login_time = session.get('login_time', 0)
    current_time = time.time()
    session_duration = current_time - login_time
    
    return {
        'username': session.get('username'),
        'login_time': login_time,
        'session_duration_minutes': session_duration / 60,
        'is_valid': check_session_validity()
    }

# Test authentication system
if __name__ == '__main__':
    print("Authentication System Test")
    print("=" * 30)
    
    # Test password hashing
    test_password = "TestPassword123!"
    hashed = hash_password(test_password)
    print(f"Password: {test_password}")
    print(f"Hashed: {hashed[:20]}...")
    print(f"Verification: {verify_password(test_password, hashed)}")
    
    # Test users
    test_users = {
        'admin': 'DreamzHub2025!',
        'matthew': 'MatthewDreamz2025!'
    }
    
    print(f"\nConfigured Users: {len(test_users)}")
    for username in test_users:
        print(f"  - {username}")