# 🔒 Security Documentation

## Table of Contents
1. [Security Architecture Overview](#security-architecture-overview)
2. [Authentication Security](#authentication-security)
3. [Authorization & RBAC](#authorization--rbac)
4. [Rate Limiting](#rate-limiting)
5. [Security Headers](#security-headers)
6. [Input Validation](#input-validation)
7. [Security Monitoring](#security-monitoring)
8. [Threat Detection](#threat-detection)
9. [Interview Preparation](#interview-preparation)

---

## Security Architecture Overview

This application implements a **defense-in-depth** security model with multiple layers:

```
┌─────────────────────────────────────────┐
│     Layer 1: Network Security           │
│     (Security Headers, HTTPS)           │
├─────────────────────────────────────────┤
│     Layer 2: Application Security       │
│     (Rate Limiting, Input Validation)   │
├─────────────────────────────────────────┤
│     Layer 3: Authentication             │
│     (Password Hashing, Session Mgmt)    │
├─────────────────────────────────────────┤
│     Layer 4: Authorization              │
│     (RBAC, Permission Checks)           │
├─────────────────────────────────────────┤
│     Layer 5: Monitoring & Detection     │
│     (Logging, Anomaly Detection)        │
└─────────────────────────────────────────┘
```

**Philosophy**: No single security control is perfect. Multiple layers ensure that if one control fails, others provide protection.

---

## Authentication Security

### Password Hashing

**Implementation:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Storing password
hashed = generate_password_hash('password123')

# Verifying password
is_valid = check_password_hash(hashed, 'user_input')
```

**Why This Matters:**
- **Never store plain-text passwords** - If database is compromised, passwords are safe
- **PBKDF2-SHA256** algorithm - Industry-standard, resistant to brute force
- **Automatic salting** - Each password has unique salt, prevents rainbow table attacks
- **Constant-time comparison** - Prevents timing attacks

### Session Security

**Configuration:**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True  # JavaScript can't access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection  
app.config['SESSION_COOKIE_SECURE'] = True     # HTTPS only (production)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Auto-logout
```

**Security Benefits:**
1. **HTTPOnly** - Prevents XSS attacks from stealing session cookies
2. **SameSite** - Prevents Cross-Site Request Forgery (CSRF)
3. **Secure flag** - Ensures cookies only sent over HTTPS
4. **Session timeout** - Limits damage from stolen sessions

**Interview Question Prep:**
> Q: "Why use HTTPOnly cookies?"
> 
> A: "HTTPOnly prevents JavaScript from accessing the session cookie. Even if an attacker injects malicious JavaScript (XSS), they can't steal the session token. This is defense-in-depth - input validation prevents XSS, but HTTPOnly provides backup protection."

---

## Authorization & RBAC

### Role-Based Access Control

**Implementation:**
```python
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = USERS.get(session['username'], {}).get('role')
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**Key Security Principles:**

1. **Principle of Least Privilege**
   - Users get minimum permissions needed
   - ADMIN can access everything
   - USER can only access user-level data

2. **Fail-Secure Design**
   - If role is missing/invalid → Access denied (403)
   - If not authenticated → Authentication required (401)
   - Default behavior is secure

3. **Separation of Duties**
   - Security monitoring (admin-only)
   - Regular operations (user+admin)

**Interview Question Prep:**
> Q: "What's the difference between 401 and 403?"
> 
> A: "401 Unauthorized means you're not authenticated - you need to log in. 403 Forbidden means you're authenticated but don't have permission for this resource. In our RBAC system, a USER trying to access /admin/data gets 403 because they're logged in but lack the ADMIN role."

---

## Rate Limiting

### Brute Force Protection

**Implementation:**
```python
def rate_limit(max_attempts=5, window_seconds=60):
    # Tracks attempts per IP using a deque (efficient sliding window)
    attempts = login_attempts[ip_address]
    
    # Remove old attempts outside time window
    while attempts and current_time - attempts[0] > window_seconds:
        attempts.popleft()
    
    # Check if limit exceeded
    if len(attempts) >= max_attempts:
        return 429  # Too Many Requests
```

**Why This Works:**
1. **Sliding Window Algorithm** - More accurate than fixed windows
2. **IP-based tracking** - Attackers can't bypass with multiple sessions
3. **Graceful degradation** - 429 response tells client when to retry
4. **Deque efficiency** - O(1) for add/remove operations

**Attack Scenarios Prevented:**
- **Credential stuffing** - Attacker trying leaked passwords
- **Brute force** - Systematic password guessing
- **API abuse** - Automated scanning/scraping

**Interview Question Prep:**
> Q: "Why use a sliding window instead of fixed time windows?"
> 
> A: "Fixed windows have an edge case: if an attacker makes 5 requests at 59 seconds, then 5 more at 1 second of next window, they get 10 requests in 2 seconds. Sliding window counts only attempts in the most recent 60 seconds at any moment, closing this loophole."

---

## Security Headers

### HTTP Response Headers

**Implementation:**
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

### Header-by-Header Breakdown

| Header | Attack Prevented | How It Works |
|--------|------------------|--------------|
| **X-Content-Type-Options: nosniff** | MIME-sniffing attacks | Browser won't guess file type, prevents execution of disguised scripts |
| **X-Frame-Options: DENY** | Clickjacking | Prevents page from being embedded in iframe, stops UI redressing attacks |
| **X-XSS-Protection: 1; mode=block** | Reflected XSS | Browser's built-in XSS filter blocks page rendering if attack detected |
| **Content-Security-Policy** | XSS, data injection | Whitelist-based resource loading, prevents inline scripts & external resources |
| **Strict-Transport-Security** | MITM, downgrade attacks | Forces HTTPS for 1 year, prevents protocol downgrade attacks |

**Real-World Example:**
```
Clickjacking Attack Without X-Frame-Options:
1. Attacker embeds your site in invisible iframe
2. Overlays fake UI on top
3. User thinks they're clicking attacker's button
4. Actually clicking your "Delete Account" button

With X-Frame-Options: DENY:
→ Browser refuses to render page in iframe
→ Attack fails before it starts
```

**Interview Question Prep:**
> Q: "Explain Content-Security-Policy"
> 
> A: "CSP is a whitelist-based defense against XSS. With 'default-src self', the browser only loads resources (scripts, images, styles) from our own domain. Even if an attacker injects `<script src='evil.com/steal.js'>`, the browser blocks it. It's an extra layer beyond input sanitization."

---

## Input Validation

### Validation Strategy

**Implementation:**
```python
def validate_input(data, field, pattern=None, min_length=None, max_length=None):
    # 1. Presence check
    if field not in data:
        return False, f'{field} is required'
    
    # 2. Type checking
    if not isinstance(value, str):
        return False, f'{field} must be a string'
    
    # 3. Length validation
    if min_length and len(value) < min_length:
        return False, f'{field} too short'
    
    # 4. Format validation
    if pattern and not re.match(pattern, value):
        return False, f'{field} format invalid'
    
    return True, None
```

**Defense Against Common Attacks:**

1. **SQL Injection** (if database used)
   ```python
   # Vulnerable:
   query = f"SELECT * FROM users WHERE username='{input}'"  # DON'T DO THIS
   
   # Secure:
   query = "SELECT * FROM users WHERE username=?"
   cursor.execute(query, (validated_input,))  # Parameterized query
   ```

2. **XSS (Cross-Site Scripting)**
   ```python
   # Vulnerable endpoint (demo only):
   return f"<p>Hello {user_input}</p>"  # If input is <script>alert()</script>
   
   # Secure approach:
   sanitized = re.sub(r'[<>"\']]', '', user_input)  # Remove dangerous chars
   # Or use proper HTML escaping
   ```

3. **Command Injection**
   ```python
   # Vulnerable:
   os.system(f"ping {user_input}")  # DON'T DO THIS
   
   # Secure:
   # Validate input matches expected format (e.g., IP address)
   if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', user_input):
       # Still use subprocess with list, not string
   ```

**Interview Question Prep:**
> Q: "What's the difference between validation and sanitization?"
> 
> A: "Validation checks if input meets requirements and rejects it if not. Sanitization modifies input to make it safe. I prefer validation - reject bad input entirely. It's more secure than trying to 'clean' potentially malicious data. Our `/demo/vulnerable` and `/demo/secure` endpoints show both approaches."

---

## Security Monitoring

### Dual Logging System

**Architecture:**
```
Application Events
        │
        ├──────> security.log  (Critical events)
        │        - Failed logins
        │        - Unauthorized access
        │        - Rate limit violations
        │        - Anomalies
        │
        └──────> access.log    (General access)
                 - All requests
                 - User actions
                 - API usage patterns
```

**Log Levels Strategy:**
```python
security_logger.info()     # Successful security events
security_logger.warning()  # Failed attempts, suspicious behavior  
security_logger.error()    # Security control failures
security_logger.critical() # Active attacks, breaches (if implemented)
```

**What Gets Logged:**

1. **Authentication Events**
   ```
   2026-02-07 19:25:01 - WARNING - Failed login attempt - Username: user1 - IP: 192.168.1.100
   ```
   - Username (for pattern analysis, not sensitive)
   - IP address (identify attack sources)
   - Timestamp (correlate events)

2. **Authorization Failures**
   ```
   2026-02-07 19:26:15 - WARNING - Unauthorized access attempt to admin_data from 192.168.1.100
   ```
   - Which resource was targeted
   - Who attempted access
   - When it occurred

3. **Rate Limit Events**
   ```
   2026-02-07 19:27:30 - WARNING - Rate limit exceeded - IP: 192.168.1.100 - Endpoint: login
   ```
   - Identifies potential automated attacks
   - Sources of abuse

**Interview Question Prep:**
> Q: "Why separate security logs from application logs?"
> 
> A: "Separation helps with analysis and alerting. Security logs are reviewed by security teams and SIEM systems, while application logs go to developers. Different audiences, different purposes. In production, security logs would go to a SIEM like Splunk for real-time analysis and alerting."

---

## Threat Detection

### Anomaly Detection

**Algorithm:**
```python
# Detect brute force patterns
recent_failures = [attempt for attempt in login_attempts[ip] 
                   if time.time() - attempt < 300]  # Last 5 minutes

if recent_failures >= 3:
    # Flag as suspicious - potential brute force attack
    security_metrics['suspicious_activities'].append({
        'type': 'brute_force_attempt',
        'ip': ip_address,
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'attempts': recent_failures
    })
```

**Detection Patterns:**

1. **Brute Force Attack**
   - **Pattern**: 3+ failed logins from same IP in 5 minutes
   - **Action**: Log as suspicious, could trigger IP ban in production
   - **Why 3 attempts**: Balance between catching attackers and allowing users who forgot password

2. **Credential Stuffing**
   - **Pattern**: Multiple usernames tried from same IP
   - **Action**: Could implement username enumeration protection
   - **Mitigation**: Generic "invalid credentials" message

3. **Account Enumeration**
   - **Pattern**: Many login attempts with different usernames
   - **Mitigation**: Same response time/message for valid and invalid usernames
   - **Why it matters**: Attackers shouldn't learn which usernames exist

**Dashboard Metrics:**
```json
{
  "summary": {
    "total_requests": 1523,
    "failed_logins": 45,
    "blocked_requests": 12,
    "suspicious_activities": 3,
    "success_rate": 97.04
  }
}
```

**Interview Question Prep:**
> Q: "How do you balance security logging with privacy?"
> 
> A: "We log security-relevant data (usernames, IPs, timestamps) but never passwords, even in logs. We log failed attempts because it's security monitoring, but in production, we'd need privacy policies and data retention limits. For example, delete logs older than 90 days unless needed for investigation."

---

## Interview Preparation

### Key Talking Points

#### 1. **"Walk me through your security project"**

**Answer Structure:**
```
"I built a Flask security application demonstrating enterprise security fundamentals:

1. Authentication - werkzeug password hashing, secure session management
2. Authorization - RBAC with USER and ADMIN roles
3. Rate Limiting - Prevents brute force attacks, 5 attempts per 60 seconds
4. Security Headers - Protects against XSS, clickjacking, MIME-sniffing
5. Monitoring - Dual logging system with anomaly detection
6. Input Validation - Prevents injection attacks

The key is defense-in-depth - multiple layers so if one fails, others protect.
I can demo the brute force protection if you'd like."
```

#### 2. **"What OWASP Top 10 vulnerabilities did you address?"**

**Your Answer:**
```
"I addressed 7 of the OWASP Top 10:

1. Broken Access Control - RBAC with role checks on every protected endpoint
2. Cryptographic Failures - Password hashing, secure session cookies
3. Injection - Input validation with regex, length checks, type validation
4. Security Misconfiguration - Security headers, secure cookie flags
5. Vulnerable Components - Minimal dependencies, only Flask and werkzeug
6. Authentication Failures - Rate limiting, secure password storage
7. Security Logging Failures - Comprehensive logging of all security events

I have demo endpoints showing vulnerable vs. secure input handling for learning."
```

#### 3. **"How would you test this application for vulnerabilities?"**

**Your Answer:**
```
"I'd use a multi-layered approach:

1. Automated Scanning - Run tools like Burp Suite or OWASP ZAP
   - Test for common vulns (XSS, injection, etc.)
   - Generate security report

2. Manual Testing:
   - Try bypassing rate limiting (fresh IPs, timing)
   - Test RBAC (USER accessing admin endpoints)
   - Attempt session hijacking
   - Input validation edge cases

3. Code Review:
   - Check all user inputs are validated
   - Verify RBAC consistently applied
   - Ensure no credentials in code

4. Logging Analysis:
   - Verify all security events logged
   - Check for sensitive data in logs

I'm learning Burp Suite for automated testing and want to gain more hands-on experience in penetration testing."
```

#### 4. **"What would you add for production?"**

**Your Answer:**
```
"Critical additions for production:

1. Database - Replace in-memory storage with PostgreSQL
   - Use parameterized queries (SQL injection prevention)
   - Encrypt sensitive data at rest

2. HTTPS - TLS/SSL certificates
   - Enable SESSION_COOKIE_SECURE flag
   - HSTS to force HTTPS

3. Advanced Auth:
   - Multi-factor authentication (MFA)
   - JWT tokens for stateless auth
   - Password complexity/history requirements

4. Enhanced Monitoring:
   - Send logs to SIEM (Splunk, ELK stack)
   - Real-time alerting for suspicious activity
   - Automated incident response

5. Testing:
   - Penetration testing
   - Security audit
   - Compliance checks (SOC 2, ISO 27001)

6. Rate Limiting:
   - Use Redis for distributed rate limiting
   - IP reputation checking
   - CAPTCHA after repeated failures
```

### Questions to Ask Interviewer

**Show your security mindset:**

1. "What security frameworks does Intel follow? (NIST, ISO 27001?)"
2. "What tools does your security team use for vulnerability assessment?"
3. "How does Intel handle security incident response?"
4. "What's Intel's approach to secure SDLC?"
5. "Are there opportunities to work with penetration testing or threat intelligence?"

---

## Security Best Practices Demonstrated

✅ **Never trust user input** - Validate everything  
✅ **Fail securely** - Default to deny access  
✅ **Defense-in-depth** - Multiple layers of security  
✅ **Least privilege** - Minimum necessary permissions  
✅ **Secure by default** - Security built in, not bolted on  
✅ **Logging & monitoring** - Detect and respond to threats  
✅ **Separation of concerns** - Security logic separated from business logic  

---

## Quick Reference: Security Controls

| Control | Purpose | OWASP Coverage |
|---------|---------|----------------|
| Password Hashing | Protect credentials | A02: Cryptographic Failures |
| **RBAC** | Prevent unauthorized access | A01: Broken Access Control |
| Rate Limiting | Prevent brute force | A07: Authentication Failures |
| Security Headers | Multiple attack prevention | A05: Security Misconfiguration |
| Input Validation | Prevent injection | A03: Injection |
| Session Security | Protect user sessions | A07: Authentication Failures |
| Security Logging | Detect attacks | A09: Security Logging Failures |

---

**Remember**: You can explain EVERY security decision in this project because you built it. Be honest about what you know and what you're learning. Saying "I implemented rate limiting to prevent brute force, and I'm studying more advanced techniques like CAPTCHA and IP reputation" shows both competence and growth mindset.
