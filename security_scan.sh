#!/bin/bash

# Security Vulnerability Scan for The Product Mindset
# This script scans for common security vulnerabilities in the codebase

echo "🔍 Starting Security Vulnerability Scan"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "INFO")
            echo -e "${BLUE}ℹ️  INFO:${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  WARNING:${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}❌ ERROR:${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅ SUCCESS:${NC} $message"
            ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo ""
print_status "INFO" "Scanning frontend dependencies..."

# Frontend dependency scan
if [ -f "package.json" ]; then
    print_status "INFO" "Checking frontend package.json for known vulnerabilities..."
    
    # Check for common vulnerable packages
    VULNERABLE_PACKAGES=(
        "lodash"
        "moment"
        "jquery"
        "bootstrap"
        "angular"
        "vue"
        "express"
    )
    
    for package in "${VULNERABLE_PACKAGES[@]}"; do
        if grep -q "\"$package\"" package.json; then
            print_status "WARNING" "Potentially vulnerable package found: $package"
        fi
    done
    
    # Check for outdated packages (if npm audit is available)
    if command_exists npm; then
        print_status "INFO" "Running npm audit..."
        npm audit --audit-level=moderate 2>/dev/null || print_status "WARNING" "npm audit not available or failed"
    fi
    
    # Check for security-related scripts
    if grep -q "eval\|Function\|setTimeout\|setInterval" src/**/*.{js,ts,jsx,tsx} 2>/dev/null; then
        print_status "WARNING" "Potential code injection vulnerabilities found (eval, Function, etc.)"
    fi
    
else
    print_status "ERROR" "package.json not found"
fi

echo ""
print_status "INFO" "Scanning backend dependencies..."

# Backend dependency scan
if [ -f "backend/pyproject.toml" ]; then
    print_status "INFO" "Checking backend Python dependencies..."
    
    # Check for known vulnerable Python packages
    VULNERABLE_PYTHON_PACKAGES=(
        "django"
        "flask"
        "requests"
        "urllib3"
        "pyyaml"
        "pillow"
        "cryptography"
    )
    
    for package in "${VULNERABLE_PYTHON_PACKAGES[@]}"; do
        if grep -q "$package" backend/pyproject.toml; then
            print_status "WARNING" "Potentially vulnerable Python package found: $package"
        fi
    done
    
    # Check for security-related imports
    if find backend/src -name "*.py" -exec grep -l "eval\|exec\|pickle\|subprocess\|os.system" {} \; 2>/dev/null | head -5; then
        print_status "WARNING" "Potential code execution vulnerabilities found in Python code"
    fi
    
    # Check for hardcoded secrets
    if find backend/src -name "*.py" -exec grep -l "password\|secret\|key\|token" {} \; 2>/dev/null | head -5; then
        print_status "WARNING" "Potential hardcoded secrets found in Python code"
    fi
    
else
    print_status "ERROR" "backend/pyproject.toml not found"
fi

echo ""
print_status "INFO" "Scanning configuration files..."

# Configuration file security scan
CONFIG_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "nginx.conf"
    "backend/env.example"
    ".env"
    ".gitignore"
)

for config_file in "${CONFIG_FILES[@]}"; do
    if [ -f "$config_file" ]; then
        print_status "INFO" "Checking $config_file..."
        
        # Check for common security issues
        if grep -q "RUN.*curl.*http" "$config_file"; then
            print_status "WARNING" "Insecure HTTP downloads in $config_file"
        fi
        
        if grep -q "ADD.*http" "$config_file"; then
            print_status "WARNING" "Insecure HTTP downloads in $config_file"
        fi
        
        if grep -q "USER root" "$config_file"; then
            print_status "WARNING" "Running as root in $config_file"
        fi
        
        if grep -q "password\|secret\|key" "$config_file"; then
            print_status "WARNING" "Potential secrets in $config_file"
        fi
    fi
done

echo ""
print_status "INFO" "Scanning for hardcoded secrets..."

# Check for hardcoded secrets
SECRET_PATTERNS=(
    "password.*=.*['\"][^'\"]{8,}"
    "secret.*=.*['\"][^'\"]{8,}"
    "key.*=.*['\"][^'\"]{8,}"
    "token.*=.*['\"][^'\"]{8,}"
    "api_key.*=.*['\"][^'\"]{8,}"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | xargs grep -l "$pattern" 2>/dev/null | head -3; then
        print_status "WARNING" "Potential hardcoded secrets found with pattern: $pattern"
    fi
done

echo ""
print_status "INFO" "Scanning for SQL injection vulnerabilities..."

# Check for SQL injection vulnerabilities
if find backend/src -name "*.py" -exec grep -l "execute.*%" {} \; 2>/dev/null | head -3; then
    print_status "WARNING" "Potential SQL injection vulnerabilities found"
fi

if find src -name "*.ts" -o -name "*.js" -o -name "*.tsx" -o -name "*.jsx" | xargs grep -l "innerHTML\|dangerouslySetInnerHTML" 2>/dev/null | head -3; then
    print_status "WARNING" "Potential XSS vulnerabilities found (innerHTML usage)"
fi

echo ""
print_status "INFO" "Scanning for CORS misconfigurations..."

# Check CORS configuration
if grep -q "Access-Control-Allow-Origin.*\*" backend/src/**/*.py 2>/dev/null; then
    print_status "WARNING" "Overly permissive CORS configuration found"
fi

echo ""
print_status "INFO" "Scanning for authentication issues..."

# Check for authentication bypass
if find backend/src -name "*.py" -exec grep -l "skip.*auth\|bypass.*auth" {} \; 2>/dev/null; then
    print_status "WARNING" "Potential authentication bypass found"
fi

echo ""
print_status "INFO" "Scanning for file upload vulnerabilities..."

# Check for file upload vulnerabilities
if find backend/src -name "*.py" -exec grep -l "upload.*file\|multipart" {} \; 2>/dev/null; then
    print_status "WARNING" "File upload functionality found - ensure proper validation"
fi

echo ""
print_status "INFO" "Scanning for rate limiting..."

# Check for rate limiting
if ! grep -q "rate.*limit\|throttle" backend/src/**/*.py 2>/dev/null; then
    print_status "WARNING" "No rate limiting found - consider implementing rate limiting"
fi

echo ""
print_status "INFO" "Scanning for HTTPS enforcement..."

# Check for HTTPS enforcement
if ! grep -q "https\|ssl\|tls" backend/src/**/*.py 2>/dev/null; then
    print_status "WARNING" "No HTTPS enforcement found - ensure HTTPS is enforced in production"
fi

echo ""
print_status "INFO" "Scanning for logging and monitoring..."

# Check for security logging
if ! find backend/src -name "*.py" -exec grep -l "log.*auth\|log.*security" {} \; 2>/dev/null; then
    print_status "WARNING" "No security logging found - consider implementing security event logging"
fi

echo ""
print_status "INFO" "Scanning for input validation..."

# Check for input validation
if find backend/src -name "*.py" -exec grep -l "validate\|sanitize" {} \; 2>/dev/null | head -3; then
    print_status "SUCCESS" "Input validation found"
else
    print_status "WARNING" "No input validation found - ensure all inputs are validated"
fi

echo ""
print_status "INFO" "Scanning for error handling..."

# Check for error handling
if find backend/src -name "*.py" -exec grep -l "try.*except\|error.*handling" {} \; 2>/dev/null | head -3; then
    print_status "SUCCESS" "Error handling found"
else
    print_status "WARNING" "Limited error handling found - ensure proper error handling"
fi

echo ""
print_status "INFO" "Scanning for dependency vulnerabilities..."

# Check for known vulnerable dependencies
if command_exists npm; then
    print_status "INFO" "Running npm audit for frontend..."
    npm audit --audit-level=high 2>/dev/null || print_status "WARNING" "npm audit failed"
fi

if command_exists pip; then
    print_status "INFO" "Checking Python dependencies for known vulnerabilities..."
    # This would require safety or bandit tools
    print_status "INFO" "Consider running: pip install safety && safety check"
fi

echo ""
print_status "INFO" "Scanning for environment variable exposure..."

# Check for environment variable exposure
if grep -q "process\.env\|os\.environ" src/**/*.{js,ts,jsx,tsx} 2>/dev/null; then
    print_status "WARNING" "Environment variables used in frontend - ensure no secrets are exposed"
fi

echo ""
print_status "INFO" "Scanning for dependency confusion..."

# Check for dependency confusion
if [ -f "package.json" ]; then
    if grep -q "@.*/" package.json; then
        print_status "WARNING" "Scoped packages found - ensure they're from trusted sources"
    fi
fi

echo ""
print_status "INFO" "Scanning for supply chain attacks..."

# Check for supply chain attack indicators
if find . -name "*.js" -o -name "*.py" | xargs grep -l "eval\|Function\|setTimeout.*string" 2>/dev/null | head -3; then
    print_status "WARNING" "Potential supply chain attack vectors found"
fi

echo ""
print_status "INFO" "Security scan completed!"

echo ""
echo "📋 Security Recommendations:"
echo "============================="
echo "1. 🔐 Implement proper authentication and authorization"
echo "2. 🛡️  Add input validation and sanitization"
echo "3. 🚦 Implement rate limiting"
echo "4. 📝 Add security logging and monitoring"
echo "5. 🔒 Enforce HTTPS in production"
echo "6. 📦 Keep dependencies updated"
echo "7. 🔍 Regular security audits"
echo "8. 🚫 Remove hardcoded secrets"
echo "9. 🔐 Use environment variables for configuration"
echo "10. 🛡️  Implement proper error handling"

echo ""
print_status "INFO" "Consider running additional security tools:"
echo "   • OWASP ZAP for web application security testing"
echo "   • Bandit for Python security analysis"
echo "   • ESLint security plugin for JavaScript/TypeScript"
echo "   • Snyk for dependency vulnerability scanning"
echo "   • SonarQube for code quality and security analysis"
