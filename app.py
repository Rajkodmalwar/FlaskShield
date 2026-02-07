# Secure Backend Demo
# Intel Security Mini Lab

from flask import Flask, request, jsonify, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import logging
from datetime import datetime, timedelta
import os
import re
from collections import defaultdict, deque
import time

app = Flask(__name__)

# Security: Secret key for session management
# In production, use environment variable or secure configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Security: Session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session timeout

# Configure logging for security events
os.makedirs('logs', exist_ok=True)

# Security event logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)
security_handler = logging.FileHandler('logs/security.log')
security_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
security_logger.addHandler(security_handler)

# Access logger
access_logger = logging.getLogger('access')
access_logger.setLevel(logging.INFO)
access_handler = logging.FileHandler('logs/access.log')
access_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
access_logger.addHandler(access_handler)

# Security: In-memory tracking for rate limiting and anomaly detection
login_attempts = defaultdict(lambda: deque(maxlen=10))  # Track last 10 attempts per IP
security_metrics = {
    'total_requests': 0,
    'failed_logins': 0,
    'blocked_requests': 0,
    'suspicious_activities': []
}

# In-memory user store with hashed passwords
# Security: Passwords are hashed using werkzeug's pbkdf2:sha256
USERS = {
    'user1': {
        'password': generate_password_hash('password123'),
        'role': 'USER'
    },
    'admin1': {
        'password': generate_password_hash('admin123'),
        'role': 'ADMIN'
    }
}

# Security: Apply security headers to all responses
@app.after_request
def set_security_headers(response):
    """
    Security: Apply security headers to prevent common attacks
    - X-Content-Type-Options: Prevent MIME-sniffing attacks
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable browser XSS protection
    - Content-Security-Policy: Restrict resource loading
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Security: Rate limiting decorator
def rate_limit(max_attempts=5, window_seconds=60):
    """
    Security: Implement rate limiting to prevent brute force attacks
    Tracks attempts per IP address within a time window
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip_address = request.remote_addr
            current_time = time.time()
            
            # Get attempt history for this IP
            attempts = login_attempts[ip_address]
            
            # Remove attempts outside the time window
            while attempts and current_time - attempts[0] > window_seconds:
                attempts.popleft()
            
            # Check if rate limit exceeded
            if len(attempts) >= max_attempts:
                security_logger.warning(
                    f"Rate limit exceeded - IP: {ip_address} - Endpoint: {request.endpoint}"
                )
                security_metrics['blocked_requests'] += 1
                return jsonify({
                    'error': 'Too many requests. Please try again later.',
                    'retry_after': window_seconds
                }), 429
            
            # Record this attempt
            attempts.append(current_time)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Security: Decorator to enforce authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            security_logger.warning(f"Unauthorized access attempt to {request.endpoint} from {request.remote_addr}")
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Security: Decorator to enforce role-based access control
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            username = session['username']
            user_role = USERS.get(username, {}).get('role')
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Security: Input validation helper
def validate_input(data, field, pattern=None, min_length=None, max_length=None):
    """
    Security: Validate user input to prevent injection attacks
    Returns (is_valid, error_message)
    """
    if field not in data:
        return False, f'{field} is required'
    
    value = data[field]
    
    if not isinstance(value, str):
        return False, f'{field} must be a string'
    
    if min_length and len(value) < min_length:
        return False, f'{field} must be at least {min_length} characters'
    
    if max_length and len(value) > max_length:
        return False, f'{field} must be at most {max_length} characters'
    
    if pattern and not re.match(pattern, value):
        return False, f'{field} format is invalid'
    
    return True, None

@app.route('/login', methods=['POST'])
@rate_limit(max_attempts=5, window_seconds=60)
def login():
    """
    Authenticate user and create session.
    Security: Rate limited, logs failed attempts, uses constant-time password comparison,
    validates input, implements security headers
    """
    security_metrics['total_requests'] += 1
    
    data = request.get_json()
    
    # Security: Input validation
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    # Validate username
    valid, error = validate_input(data, 'username', min_length=1, max_length=50)
    if not valid:
        return jsonify({'error': error}), 400
    
    # Validate password
    valid, error = validate_input(data, 'password', min_length=1, max_length=100)
    if not valid:
        return jsonify({'error': error}), 400
    
    username = data['username']
    password = data['password']
    
    user = USERS.get(username)
    
    # Security: Use check_password_hash for constant-time comparison
    # to prevent timing attacks
    if user and check_password_hash(user['password'], password):
        # Create session
        session['username'] = username
        session['role'] = user['role']
        return jsonify({
            'message': 'Login successful',
            'username': username,
            'role': user['role']
        }), 200
    else:
        # Security: Log failed login attempt with timestamp and IP
        ip_address = request.remote_addr
        security_logger.warning(
            f"Failed login attempt - Username: {username} - IP: {ip_address} - Timestamp: {datetime.now().isoformat()}"
        )
        security_metrics['failed_logins'] += 1
        
        # Security: Anomaly detection - detect brute force patterns
        recent_failures = len([a for a in login_attempts[ip_address] if time.time() - a < 300])
        if recent_failures >= 3:
            security_metrics['suspicious_activities'].append({
                'type': 'brute_force_attempt',
                'ip': ip_address,
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'attempts': recent_failures
            })
            # Keep only last 50 suspicious activities
            if len(security_metrics['suspicious_activities']) > 50:
                security_metrics['suspicious_activities'] = security_metrics['suspicious_activities'][-50:]
        
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/user/data', methods=['GET'])
@role_required('USER', 'ADMIN')
def user_data():
    """
    Endpoint accessible to both USER and ADMIN roles.
    Security: RBAC enforced via role_required decorator
    """
    return jsonify({
        'message': 'User data',
        'data': {
            'info': 'This is accessible to USER and ADMIN roles',
            'username': session['username'],
            'role': session['role']
        }
    }), 200

@app.route('/admin/data', methods=['GET'])
@role_required('ADMIN')
def admin_data():
    """
    Endpoint accessible only to ADMIN role.
    Security: RBAC enforced via role_required decorator
    """
    return jsonify({
        'message': 'Admin data',
        'data': {
            'info': 'This is accessible only to ADMIN role',
            'sensitive_info': 'Confidential administrative data',
            'username': session['username'],
            'role': session['role']
        }
    }), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Clear session on logout."""
    username = session.get('username')
    security_logger.info(f"User logged out - Username: {username} - IP: {request.remote_addr}")
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/security/dashboard', methods=['GET'])
@role_required('ADMIN')
def security_dashboard():
    """
    Security monitoring dashboard accessible only to ADMIN.
    Displays real-time security metrics and threat intelligence.
    """
    # Read recent security logs
    recent_failures = []
    try:
        with open('logs/security.log', 'r') as f:
            lines = f.readlines()[-20:]  # Last 20 log entries
            recent_failures = [line.strip() for line in lines if 'Failed login' in line]
    except FileNotFoundError:
        pass
    
    # Calculate statistics
    total_suspicious = len(security_metrics['suspicious_activities'])
    recent_suspicious = [s for s in security_metrics['suspicious_activities'][-10:]]  # Last 10
    
    dashboard_data = {
        'summary': {
            'total_requests': security_metrics['total_requests'],
            'failed_logins': security_metrics['failed_logins'],
            'blocked_requests': security_metrics['blocked_requests'],
            'suspicious_activities': total_suspicious,
            'success_rate': round(
                ((security_metrics['total_requests'] - security_metrics['failed_logins']) / 
                 max(security_metrics['total_requests'], 1)) * 100, 2
            )
        },
        'recent_failures': recent_failures[-5:],  # Last 5 failures
        'suspicious_activities': recent_suspicious,
        'security_status': 'healthy' if security_metrics['blocked_requests'] < 10 else 'warning'
    }
    
    return jsonify(dashboard_data), 200

@app.route('/security/metrics', methods=['GET'])
@role_required('ADMIN')
def security_metrics_endpoint():
    """
    Detailed security metrics for monitoring and analysis.
    """
    return jsonify(security_metrics), 200

@app.route('/demo/vulnerable', methods=['GET'])
def vulnerable_endpoint():
    """
    EDUCATIONAL DEMO: Shows a vulnerable endpoint (for learning purposes)
    This endpoint demonstrates why input validation is critical.
    In production, this would be a security risk.
    """
    # Intentionally vulnerable to demonstrate security concepts
    user_input = request.args.get('input', '')
    
    return jsonify({
        'warning': 'This is a DEMO endpoint showing vulnerability',
        'note': 'In production, never trust user input directly',
        'user_input_reflected': user_input,  # XSS risk if rendered in HTML
        'vulnerability': 'Reflected input without sanitization',
        'mitigation': 'Always validate and sanitize user input'
    }), 200

@app.route('/demo/secure', methods=['GET'])
def secure_endpoint():
    """
    EDUCATIONAL DEMO: Shows proper input handling
    This endpoint demonstrates secure coding practices.
    """
    user_input = request.args.get('input', '')
    
    # Security: Input validation and sanitization
    if len(user_input) > 100:
        return jsonify({'error': 'Input too long'}), 400
    
    # Security: Sanitize input (remove potentially dangerous characters)
    sanitized_input = re.sub(r'[<>"\']', '', user_input)
    
    return jsonify({
        'message': 'Secure input handling',
        'original_length': len(user_input),
        'sanitized_length': len(sanitized_input),
        'security_applied': 'Input validation and sanitization',
        'note': 'Input has been validated and sanitized'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'security_features': [
            'Rate Limiting',
            'Security Headers',
            'Input Validation',
            'RBAC',
            'Security Logging',
            'Anomaly Detection'
        ]
    }), 200

if __name__ == '__main__':
    # Security: Debug mode should be disabled in production
    app.run(debug=True, host='127.0.0.1', port=5000)
