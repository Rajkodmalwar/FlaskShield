# 🔐 FlaskShield - Security Assessment Platform

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Security](https://img.shields.io/badge/Security-OWASP-red.svg)

A Flask-based security assessment platform demonstrating enterprise-grade security fundamentals including authentication, authorization, rate limiting, security monitoring, and threat detection. Built to showcase secure development practices and OWASP security principles.

## 🎯 Project Overview

This project implements a **security-focused backend application** that demonstrates:
- Secure authentication and session management
- Role-Based Access Control (RBAC)
- Rate limiting and brute force protection
- Security headers implementation
- Comprehensive security logging and monitoring
- Real-time threat detection and anomaly identification
- Input validation and sanitization

**Purpose**: Educational platform showcasing enterprise security best practices and vulnerability awareness.

## � Table of Contents
- [Security Features](#-security-features-implemented)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing-the-security-features)
- [Security Concepts](#-security-concepts-demonstrated)
- [Production Deployment](#-production-deployment-checklist)

## �🛡️ Security Features Implemented

### 1. **Authentication & Session Security**
- Password hashing using werkzeug's PBKDF2-SHA256
- Constant-time password comparison (timing attack prevention)
- Secure session configuration with HTTPOnly and SameSite cookies
- Session timeout (1-hour lifetime)
- Environment-based secret key management

### 2. **Role-Based Access Control (RBAC)**
- Two-tier role system: `USER` and `ADMIN`
- Role-specific endpoints with permission enforcement
- Principle of least privilege applied
- Unauthorized access attempt logging

### 3. **Rate Limiting & Brute Force Protection**
- Configurable rate limiting per endpoint
- IP-based request tracking
- Automatic blocking of excessive requests
- 429 (Too Many Requests) responses with retry guidance
- Prevents brute force authentication attacks

### 4. **Security Headers**
Applied to all responses to prevent common web attacks:
- `X-Content-Type-Options: nosniff` - MIME-sniffing prevention
- `X-Frame-Options: DENY` - Clickjacking protection
- `X-XSS-Protection: 1; mode=block` - XSS attack mitigation
- `Content-Security-Policy` - Resource loading restrictions
- `Strict-Transport-Security` - Enforce HTTPS in production

### 5. **Security Monitoring & Logging**
- **Dual logging system**:
  - `security.log` - Authentication failures, unauthorized access, rate limit violations
  - `access.log` - General access patterns
- **Real-time metrics tracking**:
  - Total requests
  - Failed login attempts  
  - Blocked requests
  - Suspicious activity patterns
- **Anomaly detection**: Identifies brute force patterns (3+ failures in 5 minutes)

### 6. **Input Validation & Sanitization**
- Regex-based validation for all user inputs
- Length restriction enforcement
- Type checking
- Pattern matching for format validation
- XSS prevention through sanitization

### 7. **Security Dashboard** (Admin-only)
Real-time security monitoring interface providing:
- Request statistics and success rates
- Recent failed login attempts
- Suspicious activity alerts
- System health status
- Threat intelligence

## 📁 Project Structure

```
FlaskShield/
├── app.py                  # Main application with security features
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── docs/                  # Documentation
│   ├── SECURITY.md            # Detailed security documentation
│   ├── security_assessment.md # Security analysis report
│   ├── TESTING.md             # Testing guide
│   ├── PROJECT_SUMMARY.md     # Project overview
│   └── GITHUB_SETUP.md        # GitHub setup guide
└── logs/
    ├── security.log       # Security events log
    └── access.log         # Access pattern log
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Rajkodmalwar/FlaskShield.git
cd FlaskShield
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

The server starts on `http://127.0.0.1:5000`

## 🔑 Default Users

| Username | Password | Role |
|----------|----------|------|
| user1 | password123 | USER |
| admin1 | admin123 | ADMIN |

**⚠️ Note**: Change these in production!

## 📡 API Endpoints

### Authentication
- **POST** `/login` - User authentication
- **POST** `/logout` - End user session (requires auth)

### Protected Resources
- **GET** `/user/data` - Accessible to USER and ADMIN roles
- **GET** `/admin/data` - Accessible to ADMIN role only

### Security Monitoring (Admin-only)
- **GET** `/security/dashboard` - Real-time security dashboard
- **GET** `/security/metrics` - Detailed security metrics

### Educational Demos
- **GET** `/demo/vulnerable` - Shows vulnerable input handling (for learning)
- **GET** `/demo/secure` - Shows secure input handling

### Health Check
- **GET** `/health` - System health and feature list

## 🧪 Testing the Security Features

### 1. Test Successful Login
```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}' \
  -c cookies.txt
```

### 2. Test Rate Limiting (Brute Force Protection)
Run this 6 times quickly to trigger rate limiting:
```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"wrong"}'
```

### 3. Test RBAC (USER trying to access ADMIN endpoint)
```bash
# Login as USER
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}' \
  -c cookies.txt

# Try to access admin endpoint (should fail with 403)
curl -X GET http://127.0.0.1:5000/admin/data -b cookies.txt
```

### 4. View Security Dashboard
```bash
# Login as ADMIN
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"admin123"}' \
  -c admin-cookies.txt

# Access security dashboard
curl -X GET http://127.0.0.1:5000/security/dashboard -b admin-cookies.txt
```

### 5. Check Security Logs
```bash
cat logs/security.log
```

## 🎓 Security Concepts Demonstrated

### OWASP Top 10 Coverage
1. **Broken Access Control** - RBAC implementation prevents unauthorized access
2. **Cryptographic Failures** - Password hashing, secure session management
3. **Injection** - Input validation and sanitization
4. **Security Misconfiguration** - Security headers, secure session config
5. **Vulnerable Components** - Minimal dependencies, known secure libraries
6. **Identification/Authentication Failures** - Rate limiting, secure password storage
7. **Security Logging Failures** - Comprehensive logging system

### Defense-in-Depth Layers
1. **Application Layer**: Input validation, RBAC, rate limiting
2. **Session Layer**: Secure cookie configuration, timeouts
3. **Network Layer**: Security headers, HTTPS enforcement
4. **Monitoring Layer**: Real-time logging, anomaly detection

## 📊 Security Metrics

The application tracks:
- **Availability**: Rate limiting prevents DoS
- **Confidentiality**: Session security, RBAC
- **Integrity**: Input validation, secure password storage
- **Accountability**: Comprehensive logging

## 🔍 What Makes This Security-Focused?

Unlike typical CRUD applications, this project:
- ✅ **Implements threat detection** - Real-time anomaly identification
- ✅ **Demonstrates vulnerability awareness** - Educational vulnerable/secure endpoint pairs
- ✅ **Provides security monitoring** - Admin dashboard for threat intelligence
- ✅ **Applies defense-in-depth** - Multiple security layers
- ✅ **Focuses on observability** - Comprehensive logging and metrics
- ✅ **Shows production readiness** - Environment-based configs, error handling

## 🛠️ Technologies Used

- **Flask** - Web framework
- **werkzeug.security** - Password hashing
- **Python logging** - Security event tracking
- **Collections (deque)** - Efficient rate limiting
- **Regular expressions** - Input validation

## 📚 Learning Outcomes

After building/studying this project, you understand:
- How to implement secure authentication systems
- Why rate limiting is critical for API security
- How RBAC prevents unauthorized access
- The importance of security headers in web applications
- How to detect and log security threats
- Input validation techniques to prevent injection attacks
- Security monitoring and incident detection approaches

## 🔐 Production Deployment Checklist

- [ ] Change default secret key (use environment variable)
- [ ] Enable HTTPS and set `SESSION_COOKIE_SECURE = True`
- [ ] Use environment variables for all credentials
- [ ] Set up proper database (replace in-memory storage)
- [ ] Configure production logging (e.g., to SIEM)
- [ ] Implement JWT or OAuth for token-based auth
- [ ] Add database query parameterization
- [ ] Set up monitoring and alerting (e.g., Splunk, ELK)
- [ ] Conduct penetration testing
- [ ] Implement CSRF tokens for state-changing operations

## 📚 Documentation

For detailed information, see:

- **[SECURITY.md](docs/SECURITY.md)** - Deep dive into security architecture, implementation details, and interview preparation guide
- **[TESTING.md](docs/TESTING.md)** - Complete test suite with PowerShell commands for all security features
- **[security_assessment.md](docs/security_assessment.md)** - Comprehensive security analysis and threat modeling
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Quick project overview and key features
- **[GITHUB_SETUP.md](docs/GITHUB_SETUP.md)** - Step-by-step guide for setting up GitHub repository

## 🤝 Contributing

This is an educational project. Suggestions for additional security features welcome!

## 📄 License

MIT License - Educational purposes

## ✉️ Contact

Built as part of security engineering portfolio by Raj Kodmalwar

---

**⚠️ Disclaimer**: This is an educational project demonstrating security concepts. The vulnerable endpoints are intentionally insecure for learning purposes. Never deploy intentionally vulnerable code to production.

## License
MIT
