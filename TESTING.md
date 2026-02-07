# 🧪 Security Features Testing Guide

This document provides step-by-step instructions to test and demonstrate all security features.

## Prerequisites

Server must be running:
```bash
python app.py
```

## Test Suite

### Test 1: Successful Authentication ✅

**Test USER login:**
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"user1","password":"password123"}' `
  -SessionVariable session `
  -UseBasicParsing

$response.Content
```

**Expected Result:**
```json
{
  "message": "Login successful",
  "role": "USER",
  "username": "user1"
}
```

---

### Test 2: Failed Login & Security Logging 🔐

**Test with wrong password:**
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"user1","password":"wrongpassword"}' `
  -UseBasicParsing
```

**Expected Result:**
- HTTP 401 Unauthorized
- Error: "Invalid credentials"

**Verify Security Logging:**
```powershell
Get-Content logs\security.log -Tail 5
```

**Expected Log Entry:**
```
2026-02-07 XX:XX:XX - WARNING - Failed login attempt - Username: user1 - IP: 127.0.0.1 - Timestamp: 2026-02-07TXX:XX:XX
```

---

### Test 3: Rate Limiting (Brute Force Protection) 🛡️

**Run 6 failed login attempts rapidly:**
```powershell
# PowerShell script to test rate limiting
1..6 | ForEach-Object {
    try {
        Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
          -Method POST `
          -Headers @{"Content-Type"="application/json"} `
          -Body '{"username":"user1","password":"wrong"}' `
          -UseBasicParsing
    } catch {
        Write-Host "Attempt $_: $($_.Exception.Response.StatusCode)"
    }
}
```

**Expected Result:**
- First 5 attempts: HTTP 401 (Invalid credentials)
- 6th attempt: **HTTP 429 (Too Many Requests)**
- Message: "Too many requests. Please try again later."

**Verify Rate Limit Logging:**
```powershell
Get-Content logs\security.log | Select-String "Rate limit"
```

---

### Test 4: RBAC - USER Accessing USER Endpoint ✅

**Login as USER and access allowed endpoint:**
```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Login
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"user1","password":"password123"}' `
  -WebSession $session `
  -UseBasicParsing | Out-Null

# Access user endpoint
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/user/data" `
  -Method GET `
  -WebSession $session `
  -UseBasicParsing

$response.Content
```

**Expected Result:** ✅ Success
```json
{
  "data": {
    "info": "This is accessible to USER and ADMIN roles",
    "role": "USER",
    "username": "user1"
  },
  "message": "User data"
}
```

---

### Test 5: RBAC - USER Denied ADMIN Access 🚫

**USER attempting to access ADMIN endpoint:**
```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Login as USER
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"user1","password":"password123"}' `
  -WebSession $session `
  -UseBasicParsing | Out-Null

# Try to access admin endpoint (should fail)
try {
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/admin/data" `
      -Method GET `
      -WebSession $session `
      -UseBasicParsing
} catch {
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.Value__)"
    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $reader.ReadToEnd()
}
```

**Expected Result:** ❌ Denied
```
Status Code: 403
{
  "error": "Insufficient permissions"
}
```

---

### Test 6: ADMIN Full Access ⭐

**ADMIN accessing all endpoints:**
```powershell
$adminSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Login as ADMIN
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"admin1","password":"admin123"}' `
  -WebSession $adminSession `
  -UseBasicParsing | Out-Null

# Access admin endpoint
Write-Host "`n--- Admin Data Endpoint ---"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/admin/data" `
  -Method GET `
  -WebSession $adminSession `
  -UseBasicParsing
$response.Content

# Access user endpoint (admin can access user-level too)
Write-Host "`n--- User Data Endpoint (as Admin) ---"
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/user/data" `
  -Method GET `
  -WebSession $adminSession `
  -UseBasicParsing
$response.Content
```

**Expected Result:** ✅ Both succeed

---

### Test 7: Security Dashboard (Admin-only) 📊

**View security monitoring dashboard:**
```powershell
$adminSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Login as ADMIN
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"admin1","password":"admin123"}' `
  -WebSession $adminSession `
  -UseBasicParsing | Out-Null

# Access security dashboard
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/security/dashboard" `
  -Method GET `
  -WebSession $adminSession `
  -UseBasicParsing

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

**Expected Result:**
```json
{
  "summary": {
    "total_requests": 50,
    "failed_logins": 12,
    "blocked_requests": 2,
    "suspicious_activities": 1,
    "success_rate": 76.0
  },
  "recent_failures": [...],
  "suspicious_activities": [...],
  "security_status": "healthy"
}
```

---

### Test 8: Security Headers 🔒

**Verify security headers are applied:**
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" `
  -Method GET `
  -UseBasicParsing

Write-Host "`n--- Security Headers ---"
Write-Host "X-Content-Type-Options: $($response.Headers['X-Content-Type-Options'])"
Write-Host "X-Frame-Options: $($response.Headers['X-Frame-Options'])"
Write-Host "X-XSS-Protection: $($response.Headers['X-XSS-Protection'])"
Write-Host "Content-Security-Policy: $($response.Headers['Content-Security-Policy'])"
Write-Host "Strict-Transport-Security: $($response.Headers['Strict-Transport-Security'])"
```

**Expected Output:**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

### Test 9: Input Validation ✔️

**Test input validation:**
```powershell
# Missing username
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"password":"test"}' `
  -UseBasicParsing

# Empty username (fails validation)
Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"","password":"test"}' `
  -UseBasicParsing
```

**Expected Results:**
- HTTP 400 (Bad Request)
- Error messages about validation failures

---

### Test 10: Vulnerable vs Secure Endpoints 🎓

**Educational Demo - Vulnerable endpoint:**
```powershell
$maliciousInput = "<script>alert('XSS')</script>"
$encodedInput = [System.Web.HttpUtility]::UrlEncode($maliciousInput)

$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/demo/vulnerable?input=$encodedInput" `
  -Method GET `
  -UseBasicParsing

$response.Content
```

**Secure endpoint:**
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/demo/secure?input=$encodedInput" `
  -Method GET `
  -UseBasicParsing

$response.Content
```

**Compare**: Vulnerable reflects input as-is; Secure sanitizes it.

---

### Test 11: Anomaly Detection 🚨

**Trigger brute force detection:**
```powershell
# Create 4 failed attempts to trigger anomaly detection
1..4 | ForEach-Object {
    try {
        Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
          -Method POST `
          -Headers @{"Content-Type"="application/json"} `
          -Body '{"username":"user1","password":"wrong"}' `
          -UseBasicParsing
    } catch {}
    Start-Sleep -Milliseconds 500
}

# Check security metrics as ADMIN
$adminSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"admin1","password":"admin123"}' `
  -WebSession $adminSession `
  -UseBasicParsing | Out-Null

$metrics = Invoke-WebRequest -Uri "http://127.0.0.1:5000/security/metrics" `
  -Method GET `
  -WebSession $adminSession `
  -UseBasicParsing

$metrics.Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

**Expected**: `suspicious_activities` array contains brute force attempts.

---

### Test 12: Health Check 🏥

**Verify all security features are active:**
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" `
  -Method GET `
  -UseBasicParsing

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

**Expected Result:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-07T...",
  "security_features": [
    "Rate Limiting",
    "Security Headers",
    "Input Validation",
    "RBAC",
    "Security Logging",
    "Anomaly Detection"
  ]
}
```

---

## Complete Test Script

**Run all tests automatically:**

Save this as `test_security.ps1`:

```powershell
# Complete Security Test Suite
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Security Features Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Successful Login
Write-Host "[TEST 1] Successful Login..." -ForegroundColor Yellow
try {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
      -Method POST `
      -Headers @{"Content-Type"="application/json"} `
      -Body '{"username":"user1","password":"password123"}' `
      -WebSession $session `
      -UseBasicParsing
    Write-Host "✅ PASSED - Login successful" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
}

# Test 2: Failed Login
Write-Host "`n[TEST 2] Failed Login Detection..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
      -Method POST `
      -Headers @{"Content-Type"="application/json"} `
      -Body '{"username":"user1","password":"wrong"}' `
      -UseBasicParsing
    Write-Host "❌ FAILED - Should have been rejected" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode.Value__ -eq 401) {
        Write-Host "✅ PASSED - Login correctly rejected" -ForegroundColor Green
    }
}

# Test 3: Rate Limiting
Write-Host "`n[TEST 3] Rate Limiting..." -ForegroundColor Yellow
$rateLimitHit = $false
1..6 | ForEach-Object {
    try {
        Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
          -Method POST `
          -Headers @{"Content-Type"="application/json"} `
          -Body '{"username":"test","password":"test"}' `
          -UseBasicParsing | Out-Null
    } catch {
        if ($_.Exception.Response.StatusCode.Value__ -eq 429) {
            $rateLimitHit = $true
        }
    }
}
if ($rateLimitHit) {
    Write-Host "✅ PASSED - Rate limiting active" -ForegroundColor Green
} else {
    Write-Host "❌ FAILED - Rate limit not triggered" -ForegroundColor Red
}

# Test 4: RBAC - USER accessing USER endpoint
Write-Host "`n[TEST 4] RBAC - USER Access..." -ForegroundColor Yellow
try {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
      -Method POST `
      -Headers @{"Content-Type"="application/json"} `
      -Body '{"username":"user1","password":"password123"}' `
      -WebSession $session `
      -UseBasicParsing | Out-Null
    
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/user/data" `
      -Method GET `
      -WebSession $session `
      -UseBasicParsing
    Write-Host "✅ PASSED - USER can access user endpoint" -ForegroundColor Green
} catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
}

# Test 5: RBAC - USER denied ADMIN access
Write-Host "`n[TEST 5] RBAC - USER Denied ADMIN..." -ForegroundColor Yellow
try {
    $session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" `
      -Method POST `
      -Headers @{"Content-Type"="application/json"} `
      -Body '{"username":"user1","password":"password123"}' `
      -WebSession $session `
      -UseBasicParsing | Out-Null
    
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/admin/data" `
      -Method GET `
      -WebSession $session `
      -UseBasicParsing
    Write-Host "❌ FAILED - USER should not access admin endpoint" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode.Value__ -eq 403) {
        Write-Host "✅ PASSED - USER correctly denied ADMIN access" -ForegroundColor Green
    }
}

# Test 6: Security Headers
Write-Host "`n[TEST 6] Security Headers..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" `
  -Method GET `
  -UseBasicParsing

$headersPresent = $response.Headers.ContainsKey('X-Frame-Options') -and 
                  $response.Headers.ContainsKey('X-Content-Type-Options')
if ($headersPresent) {
    Write-Host "✅ PASSED - Security headers applied" -ForegroundColor Green
} else {
    Write-Host "❌ FAILED - Missing security headers" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Suite Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nCheck logs/security.log for detailed security events" -ForegroundColor Yellow
```

**Run:**
```powershell
.\test_security.ps1
```

---

## 📸 Demo Screenshots Checklist

For your resume/GitHub, capture:

1. ✅ Successful login response
2. ✅ Rate limiting in action (429 response)
3. ✅ RBAC denial (403 Forbidden)
4. ✅ Security dashboard with metrics
5. ✅ Security logs showing failed attempts
6. ✅ Security headers in browser dev tools
7. ✅ Anomaly detection in metrics

---

## 💡 For Interviews

**Demo Flow (5 minutes):**
1. Show health endpoint → "Here are all security features"
2. Successful login → "Secure authentication"
3. Trigger rate limit → "Brute force protection"
4. USER → ADMIN deny → "RBAC in action"
5. Show security dashboard → "Real-time monitoring"
6. Show security.log → "Comprehensive logging"

**Key Message**: "This isn't just authentication - it's enterprise security monitoring and threat detection."
