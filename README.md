# 🔐 FlaskShield

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Security](https://img.shields.io/badge/Security-OWASP-red.svg)

Enterprise-grade Flask security platform demonstrating authentication, RBAC, rate limiting, threat detection, and comprehensive security monitoring based on OWASP principles.

## ✨ Key Features

- **🔒 Secure Authentication** - PBKDF2-SHA256 password hashing, session management, HTTP-only cookies
- **👥 Role-Based Access Control** - USER/ADMIN roles with permission enforcement
- **🛡️ Brute Force Protection** - Rate limiting with IP tracking and automatic blocking
- **📊 Security Dashboard** - Real-time monitoring, metrics, and anomaly detection
- **🔍 Threat Detection** - Automated logging of suspicious activity patterns
- **⚡ Security Headers** - XSS, clickjacking, MIME-sniffing protection
- **✅ Input Validation** - Regex-based sanitization preventing injection attacks

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Rajkodmalwar/FlaskShield.git
cd FlaskShield
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run
python app.py
```

Server runs at `http://127.0.0.1:5000`

## 🔑 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| user1 | password123 | USER |
| admin1 | admin123 | ADMIN |

## 📡 Key Endpoints

- `POST /login` - Authenticate user
- `GET /user/data` - User dashboard (requires auth)
- `GET /admin/data` - Admin resources (admin only)
- `GET /security/dashboard` - Security monitoring (admin only)
- `GET /health` - System health check

## 🧪 Test Security Features

```bash
# Test rate limiting (run 6+ times quickly)
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"wrong"}'

# Login as admin
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"admin123"}' \
  -c cookies.txt

# View security dashboard
curl http://127.0.0.1:5000/security/dashboard -b cookies.txt

# Check security logs
cat logs/security.log
```

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

## 📚 Documentation

- **[SECURITY.md](docs/SECURITY.md)** - Security architecture deep dive
- **[TESTING.md](docs/TESTING.md)** - Complete test suite
- **[security_assessment.md](docs/security_assessment.md)** - Threat modeling analysis

## 🎓 What You'll Learn

- Secure authentication implementation
- Rate limiting for brute force prevention
- Role-based access control patterns
- Security headers configuration
- Threat detection and logging
- Input validation techniques
- OWASP Top 10 defense strategies

## 🛠️ Tech Stack

Flask • Python • werkzeug.security • Logging • Collections

## 📄 License

MIT License - Educational purposes

---

Built by [Raj Kodmalwar](https://github.com/Rajkodmalwar) | **⚠️ Educational project** - Demonstrates security concepts
