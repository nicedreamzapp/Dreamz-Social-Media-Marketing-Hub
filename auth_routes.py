"""
Authentication Routes - Handle login/logout functionality
Separated authentication logic from main Flask app
"""
from flask import render_template_string, request, session, redirect, url_for, flash

def setup_auth_routes(app, users_dict):
    """Setup authentication routes for the Flask app"""
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username in users_dict and users_dict[username] == password:
                session['logged_in'] = True
                return redirect(url_for('home'))
            flash('Invalid credentials')
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Divine Tribe Marketing Hub - Login</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0; 
                    padding: 0; 
                    min-height: 100vh; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                }
                .login-container { 
                    background: white; 
                    padding: 40px; 
                    border-radius: 15px; 
                    box-shadow: 0 15px 35px rgba(0,0,0,0.1); 
                    max-width: 400px; 
                    width: 100%; 
                    text-align: center; 
                }
                .login-container h2 { 
                    color: #333; 
                    margin-bottom: 30px; 
                    font-size: 24px; 
                }
                .form-group { 
                    margin-bottom: 20px; 
                    text-align: left; 
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
                    border-radius: 8px; 
                    font-size: 16px; 
                    box-sizing: border-box; 
                }
                input[type="text"]:focus, input[type="password"]:focus { 
                    border-color: #667eea; 
                    outline: none; 
                }
                .login-btn { 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 12px 30px; 
                    border: none; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    font-size: 16px; 
                    width: 100%; 
                    margin-top: 10px; 
                }
                .login-btn:hover { 
                    opacity: 0.9; 
                }
                .error { 
                    color: #e74c3c; 
                    margin-top: 10px; 
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>Divine Tribe Marketing Hub</h2>
                <form method="post">
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input type="text" name="username" id="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password:</label>
                        <input type="password" name="password" id="password" required>
                    </div>
                    <button type="submit" class="login-btn">Login</button>
                    {% with messages = get_flashed_messages() %}
                        {% if messages %}
                            <div class="error">{{ messages[0] }}</div>
                        {% endif %}
                    {% endwith %}
                </form>
            </div>
        </body>
        </html>
        ''')

    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        return redirect(url_for('login'))

