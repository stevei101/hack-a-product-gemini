# Quick Security Fixes - The Product Mindset

## 🚨 Immediate Security Fixes Required

### 1. **Fix Hardcoded Secrets** (5 minutes)

**File**: `backend/src/agentic_app/core/config.py`

```python
# BEFORE (INSECURE)
NIM_API_KEY: str = "nvapi-your-api-key-here"

# AFTER (SECURE)
NIM_API_KEY: str = os.getenv("NIM_API_KEY", "")
if not NIM_API_KEY:
    raise ValueError("NIM_API_KEY environment variable is required")
```

### 2. **Add Basic Authentication** (15 minutes)

**File**: `backend/src/agentic_app/core/auth.py` (NEW FILE)

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    if credentials.credentials != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return credentials.credentials
```

**Update endpoints**:
```python
# Add to all API endpoints
from agentic_app.core.auth import verify_api_key

@router.get("/agents")
async def list_agents(api_key: str = Depends(verify_api_key)):
    # Your existing code
```

### 3. **Add Rate Limiting** (10 minutes)

**Install dependency**:
```bash
cd backend && source .venv/bin/activate
pip install slowapi
```

**Add to main.py**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to endpoints
@router.get("/agents")
@limiter.limit("10/minute")
async def list_agents(request: Request):
    # Your existing code
```

### 4. **Add Security Headers** (5 minutes)

**Add to main.py**:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "*.yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)  # Only in production
```

### 5. **Secure Environment Variables** (5 minutes)

**Create `.env` file**:
```bash
# backend/.env
NIM_API_KEY=your_actual_nvidia_api_key_here
API_KEY=your_secure_api_key_here
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=your_jwt_secret_key_here
```

**Update .gitignore**:
```bash
# Add to .gitignore
.env
*.env
.env.local
.env.production
```

### 6. **Add Input Validation** (10 minutes)

**Update Pydantic models**:
```python
from pydantic import validator, Field
import re

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    
    @validator('message')
    def validate_message(cls, v):
        # Remove potential XSS
        v = re.sub(r'<script.*?</script>', '', v, flags=re.IGNORECASE)
        v = re.sub(r'javascript:', '', v, flags=re.IGNORECASE)
        return v.strip()
```

## 🔧 Advanced Security Fixes

### 7. **Add JWT Authentication** (30 minutes)

**Install dependencies**:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

**Create auth service**:
```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

### 8. **Add Security Logging** (10 minutes)

**Add to main.py**:
```python
import logging
import json

# Configure security logging
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

def log_security_event(event_type: str, details: dict):
    security_logger.info(json.dumps({
        "event": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }))
```

### 9. **Add CORS Security** (5 minutes)

**Update CORS configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specific methods only
    allow_headers=["*"],
)
```

### 10. **Add Request Validation** (10 minutes)

**Create request validator**:
```python
from fastapi import Request
import time

request_counts = {}

def validate_request(request: Request):
    client_ip = request.client.host
    current_time = time.time()
    
    # Simple rate limiting per IP
    if client_ip in request_counts:
        if current_time - request_counts[client_ip] < 1:  # 1 request per second
            raise HTTPException(status_code=429, detail="Too many requests")
    
    request_counts[client_ip] = current_time
```

## 🚀 Quick Implementation Script

**Create `fix_security.sh`**:
```bash
#!/bin/bash
echo "🔧 Applying security fixes..."

# 1. Create secure environment file
cp backend/env.example backend/.env
echo "✅ Created .env file"

# 2. Update .gitignore
echo ".env" >> .gitignore
echo "✅ Updated .gitignore"

# 3. Install security dependencies
cd backend && source .venv/bin/activate
pip install slowapi python-jose[cryptography] passlib[bcrypt]
echo "✅ Installed security packages"

echo "🎉 Security fixes applied! Remember to:"
echo "   1. Set secure values in backend/.env"
echo "   2. Update API endpoints with authentication"
echo "   3. Test all endpoints"
```

## ⚠️ Critical Reminders

1. **Never commit secrets to git**
2. **Use HTTPS in production**
3. **Regularly update dependencies**
4. **Monitor security logs**
5. **Test authentication thoroughly**

## 📞 Next Steps

1. Apply immediate fixes (Priority 1)
2. Test all endpoints
3. Deploy to staging environment
4. Run security tests
5. Deploy to production with monitoring

---

**Time to implement**: ~2 hours for basic security  
**Priority**: CRITICAL - Do before production deployment
