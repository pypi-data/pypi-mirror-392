# Alprina API Testing Guide

Complete guide for testing all API routes and ensuring CLI functionality.

## Table of Contents
1. [Automated Testing with Pytest](#automated-testing)
2. [Manual API Testing](#manual-testing)
3. [CLI Testing](#cli-testing)
4. [Integration Testing](#integration-testing)
5. [API Endpoint Reference](#api-reference)

---

## Automated Testing with Pytest

### Setup

```bash
cd cli

# Install test dependencies
pip install pytest pytest-cov httpx

# Or if using requirements-dev.txt
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all API route tests
pytest tests/test_api_routes.py -v

# Run with coverage report
pytest tests/test_api_routes.py -v --cov=src/alprina_cli/api

# Run specific test class
pytest tests/test_api_routes.py::TestAuthenticationRoutes -v

# Run specific test
pytest tests/test_api_routes.py::TestAuthenticationRoutes::test_register_new_user -v

# Run with detailed output
pytest tests/test_api_routes.py -v --tb=short

# Run and stop on first failure
pytest tests/test_api_routes.py -x
```

### Test Coverage

The test suite covers:
- ✅ Health and root endpoints
- ✅ Authentication (register, login, API keys)
- ✅ Code scanning
- ✅ Scan management
- ✅ Dashboard endpoints
- ✅ Alert endpoints
- ✅ Agent listings
- ✅ Authentication failures

---

## Manual API Testing

### Option 1: Using the Testing Script

```bash
# Make script executable
chmod +x cli/test_api_manual.sh

# Test against production
./cli/test_api_manual.sh

# Test against local API
API_BASE_URL=http://localhost:8000 ./cli/test_api_manual.sh

# Test against staging
API_BASE_URL=https://staging.api.alprina.com ./cli/test_api_manual.sh
```

The script will test all major endpoints and provide colorized output showing pass/fail status.

### Option 2: Using cURL Manually

#### 1. Health Check
```bash
curl https://api.alprina.com/health | jq
```

#### 2. Register User
```bash
curl -X POST https://api.alprina.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "YourPassword123!",
    "full_name": "Test User"
  }' | jq

# Save the API key from response
export API_KEY="your_api_key_here"
```

#### 3. Login
```bash
curl -X POST https://api.alprina.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "YourPassword123!"
  }' | jq
```

#### 4. Get Current User
```bash
curl https://api.alprina.com/v1/auth/me \
  -H "Authorization: Bearer $API_KEY" | jq
```

#### 5. Scan Code
```bash
curl -X POST https://api.alprina.com/v1/scan/code \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def unsafe_query(user_input):\n    query = f\"SELECT * FROM users WHERE name = '"'"'{user_input}'"'"'\"\\n    return query",
    "language": "python",
    "profile": "code-audit"
  }' | jq
```

#### 6. List Scans
```bash
curl "https://api.alprina.com/v1/scans?limit=10" \
  -H "Authorization: Bearer $API_KEY" | jq
```

#### 7. Get Dashboard Data
```bash
# Vulnerabilities
curl "https://api.alprina.com/v1/dashboard/vulnerabilities?limit=10" \
  -H "Authorization: Bearer $API_KEY" | jq

# Recent scans
curl "https://api.alprina.com/v1/dashboard/scans/recent?limit=5" \
  -H "Authorization: Bearer $API_KEY" | jq

# Trends
curl "https://api.alprina.com/v1/dashboard/analytics/trends?days=30" \
  -H "Authorization: Bearer $API_KEY" | jq
```

#### 8. Get Alerts
```bash
# Unread count
curl https://api.alprina.com/v1/alerts/unread-count \
  -H "Authorization: Bearer $API_KEY" | jq

# List alerts
curl "https://api.alprina.com/v1/alerts?limit=10" \
  -H "Authorization: Bearer $API_KEY" | jq
```

---

## CLI Testing

### Install CLI (if not installed)

```bash
# From PyPI (published version)
pip install alprina

# Or from source
cd cli
pip install -e .
```

### Test CLI Commands

```bash
# Check version
alprina --version

# Get help
alprina --help

# Scan a file
alprina scan path/to/file.py --profile code-audit

# Scan with specific agent
alprina scan path/to/contract.sol --agent solidity

# List available agents
alprina agents list

# View scan history
alprina scans list

# Get scan details
alprina scans get SCAN_ID

# Login
alprina auth login

# Check status
alprina auth status
```

### Test CLI with Sample Vulnerable Code

Create a test file:
```python
# test_vulnerable.py
def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def unsafe_eval(user_code):
    return eval(user_code)
```

Scan it:
```bash
alprina scan test_vulnerable.py --profile code-audit
```

---

## Integration Testing

### Full Workflow Test

```bash
# 1. Create test directory
mkdir -p /tmp/alprina_test
cd /tmp/alprina_test

# 2. Create vulnerable code
cat > vulnerable.py << 'EOF'
import os
import pickle

def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return query

def unsafe_pickle_load(data):
    return pickle.loads(data)

def unsafe_command(user_cmd):
    os.system(user_cmd)
EOF

# 3. Scan with CLI
alprina scan vulnerable.py

# 4. Check results
alprina scans list

# 5. Cleanup
cd -
rm -rf /tmp/alprina_test
```

### Backend Integration Test

```bash
# Start local API server
cd cli
uvicorn alprina_cli.api.main:app --reload --port 8000

# In another terminal, run tests
API_BASE_URL=http://localhost:8000 ./test_api_manual.sh
```

---

## API Endpoint Reference

### Core Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | API root info |
| `/health` | GET | No | Health check |
| `/docs` | GET | No | Swagger UI docs |

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/auth/register` | POST | No | Register new user |
| `/v1/auth/login` | POST | No | Login user |
| `/v1/auth/me` | GET | Yes | Get current user |
| `/v1/auth/api-keys` | GET | Yes | List API keys |
| `/v1/auth/api-keys` | POST | Yes | Create API key |
| `/v1/auth/api-keys/{id}` | DELETE | Yes | Revoke API key |
| `/v1/auth/sync-stack-user` | POST | No | Sync Stack Auth user |

### Scanning

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/scan/code` | POST | Yes | Scan code |
| `/v1/scans` | GET | Yes | List scans |
| `/v1/scans/{id}` | GET | Yes | Get scan details |

### Dashboard

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/dashboard/vulnerabilities` | GET | Yes | Get vulnerabilities |
| `/v1/dashboard/scans/recent` | GET | Yes | Get recent scans |
| `/v1/dashboard/analytics/trends` | GET | Yes | Get vulnerability trends |
| `/v1/dashboard/ai-fix` | POST | Yes | Generate AI fix |

### Alerts

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/alerts` | GET | Yes | List alerts |
| `/v1/alerts/unread-count` | GET | Yes | Get unread count |
| `/v1/alerts/mark-read` | POST | Yes | Mark alert as read |
| `/v1/alerts/mark-all-read` | POST | Yes | Mark all as read |

### Agents

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/agents` | GET | No | List available agents |

### Billing & Subscriptions

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/webhooks/polar` | POST | No | Polar webhook |
| `/v1/subscription/status` | GET | Yes | Get subscription status |

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd cli
        pip install -e .
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        cd cli
        pytest tests/test_api_routes.py -v --cov

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Common Issues

**1. Database not configured (503 errors)**
- Dashboard endpoints may return 503 if DATABASE_URL is not set
- This is expected for local testing without a database
- Set `DATABASE_URL` environment variable to fix

**2. Authentication failures**
- Ensure API key is properly prefixed with `Bearer `
- Check that user exists and API key is valid
- API keys expire after 90 days by default

**3. Rate limiting**
- Production API may have rate limits
- Use backoff strategy for repeated requests
- Check `X-RateLimit-Remaining` header

**4. Test user already exists**
- Use unique email for each test run
- Or login with existing credentials
- Or clean up test users periodically

---

## Best Practices

1. **Always test against staging before production**
2. **Use environment variables for API URLs and keys**
3. **Run full test suite before deploying**
4. **Monitor API response times**
5. **Check for security vulnerabilities regularly**
6. **Keep test data separate from production**
7. **Clean up test users and scans**

---

## Quick Reference

```bash
# Run all tests
pytest cli/tests/test_api_routes.py -v

# Manual API test
./cli/test_api_manual.sh

# Test CLI
alprina scan test.py

# Test specific endpoint
curl https://api.alprina.com/health | jq

# Run with coverage
pytest cli/tests/test_api_routes.py --cov -v
```

---

## Support

- Documentation: https://docs.alprina.com
- Issues: https://github.com/0xShortx/Alprina/issues
- API Docs: https://api.alprina.com/docs
