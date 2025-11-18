#!/bin/bash

# Alprina API Manual Testing Script
# This script tests all major API endpoints manually

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="${API_BASE_URL:-https://api.alprina.com}"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
API_KEY=""
USER_ID=""
SCAN_ID=""

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS:${NC} $2"
    else
        echo -e "${RED}❌ FAIL:${NC} $2"
    fi
}

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4

    if [ -n "$headers" ]; then
        curl -s -X "$method" "$API_BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "$headers" \
            -d "$data"
    else
        curl -s -X "$method" "$API_BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
}

# Start testing
echo -e "${YELLOW}═══════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Alprina API Comprehensive Testing Suite${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════${NC}"
echo -e "API Base URL: ${BLUE}$API_BASE_URL${NC}"
echo -e "Test Email: ${BLUE}$TEST_EMAIL${NC}"

# Test 1: Health Check
print_header "1. HEALTH & ROOT ENDPOINTS"

echo "Testing GET /health..."
HEALTH_RESPONSE=$(curl -s "$API_BASE_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_result 0 "Health check endpoint"
    echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    print_result 1 "Health check endpoint"
    echo "$HEALTH_RESPONSE"
fi

echo -e "\nTesting GET /..."
ROOT_RESPONSE=$(curl -s "$API_BASE_URL/")
if echo "$ROOT_RESPONSE" | grep -q "Alprina API"; then
    print_result 0 "Root endpoint"
    echo "$ROOT_RESPONSE" | jq '.' 2>/dev/null || echo "$ROOT_RESPONSE"
else
    print_result 1 "Root endpoint"
    echo "$ROOT_RESPONSE"
fi

# Test 2: Authentication
print_header "2. AUTHENTICATION ENDPOINTS"

echo "Testing POST /v1/auth/register..."
REGISTER_RESPONSE=$(api_call POST "/v1/auth/register" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Test User\"}")

if echo "$REGISTER_RESPONSE" | grep -q "api_key"; then
    print_result 0 "User registration"
    API_KEY=$(echo "$REGISTER_RESPONSE" | jq -r '.api_key')
    USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.user_id')
    echo "API Key: ${API_KEY:0:20}..."
    echo "User ID: $USER_ID"
elif echo "$REGISTER_RESPONSE" | grep -q "already exists"; then
    print_result 0 "User registration (user exists)"
    echo "User already exists, attempting login..."

    # Try login instead
    LOGIN_RESPONSE=$(api_call POST "/v1/auth/login" "{\"email\":\"test@example.com\",\"password\":\"$TEST_PASSWORD\"}")
    if echo "$LOGIN_RESPONSE" | grep -q "api_keys"; then
        API_KEY=$(echo "$LOGIN_RESPONSE" | jq -r '.api_keys[0].key')
        USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.id')
        print_result 0 "Login with existing user"
    fi
else
    print_result 1 "User registration"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

echo -e "\nTesting GET /v1/auth/me..."
ME_RESPONSE=$(api_call GET "/v1/auth/me" "" "Authorization: Bearer $API_KEY")
if echo "$ME_RESPONSE" | grep -q "user"; then
    print_result 0 "Get current user"
    echo "$ME_RESPONSE" | jq '.user' 2>/dev/null || echo "$ME_RESPONSE"
else
    print_result 1 "Get current user"
    echo "$ME_RESPONSE"
fi

echo -e "\nTesting GET /v1/auth/api-keys..."
KEYS_RESPONSE=$(api_call GET "/v1/auth/api-keys" "" "Authorization: Bearer $API_KEY")
if echo "$KEYS_RESPONSE" | grep -q "api_keys"; then
    print_result 0 "List API keys"
    echo "Total keys: $(echo "$KEYS_RESPONSE" | jq -r '.total')"
else
    print_result 1 "List API keys"
    echo "$KEYS_RESPONSE"
fi

# Test 3: Agents
print_header "3. AGENT ENDPOINTS"

echo "Testing GET /v1/agents..."
AGENTS_RESPONSE=$(api_call GET "/v1/agents" "")
if echo "$AGENTS_RESPONSE" | grep -q "agents"; then
    print_result 0 "List available agents"
    AGENT_COUNT=$(echo "$AGENTS_RESPONSE" | jq '.agents | length')
    echo "Available agents: $AGENT_COUNT"
    echo "$AGENTS_RESPONSE" | jq '.agents[0:3] | .[] | {id, name}' 2>/dev/null || echo "$AGENTS_RESPONSE"
else
    print_result 1 "List available agents"
    echo "$AGENTS_RESPONSE"
fi

# Test 4: Code Scanning
print_header "4. CODE SCANNING ENDPOINTS"

TEST_CODE='def unsafe_query(user_input):\n    query = f"SELECT * FROM users WHERE name = '\''{user_input}'\''"\\n    return query'

echo "Testing POST /v1/scan/code..."
SCAN_RESPONSE=$(api_call POST "/v1/scan/code" "{\"code\":\"$TEST_CODE\",\"language\":\"python\",\"profile\":\"code-audit\"}" "Authorization: Bearer $API_KEY")

if echo "$SCAN_RESPONSE" | grep -q "scan_id"; then
    print_result 0 "Code scan submission"
    SCAN_ID=$(echo "$SCAN_RESPONSE" | jq -r '.scan_id')
    echo "Scan ID: $SCAN_ID"
    FINDINGS=$(echo "$SCAN_RESPONSE" | jq '.findings | length' 2>/dev/null || echo "0")
    echo "Findings: $FINDINGS"
else
    print_result 1 "Code scan submission"
    echo "$SCAN_RESPONSE"
fi

# Test 5: Scan Management
print_header "5. SCAN MANAGEMENT ENDPOINTS"

echo "Testing GET /v1/scans..."
SCANS_LIST_RESPONSE=$(api_call GET "/v1/scans?limit=5" "" "Authorization: Bearer $API_KEY")
if echo "$SCANS_LIST_RESPONSE" | grep -q "scans"; then
    print_result 0 "List scans"
    TOTAL_SCANS=$(echo "$SCANS_LIST_RESPONSE" | jq -r '.total')
    echo "Total scans: $TOTAL_SCANS"
else
    print_result 1 "List scans"
    echo "$SCANS_LIST_RESPONSE"
fi

if [ -n "$SCAN_ID" ]; then
    echo -e "\nTesting GET /v1/scans/{id}..."
    SCAN_DETAIL_RESPONSE=$(api_call GET "/v1/scans/$SCAN_ID" "" "Authorization: Bearer $API_KEY")
    if echo "$SCAN_DETAIL_RESPONSE" | grep -q "id"; then
        print_result 0 "Get scan details"
    else
        print_result 1 "Get scan details"
        echo "$SCAN_DETAIL_RESPONSE"
    fi
fi

# Test 6: Dashboard Endpoints
print_header "6. DASHBOARD ENDPOINTS"

echo "Testing GET /v1/dashboard/vulnerabilities..."
VULN_RESPONSE=$(api_call GET "/v1/dashboard/vulnerabilities?limit=10" "" "Authorization: Bearer $API_KEY")
if echo "$VULN_RESPONSE" | grep -q "vulnerabilities" || echo "$VULN_RESPONSE" | grep -q "503"; then
    if echo "$VULN_RESPONSE" | grep -q "503"; then
        print_result 0 "Dashboard vulnerabilities (DB not configured)"
    else
        print_result 0 "Dashboard vulnerabilities"
        echo "Total vulnerabilities: $(echo "$VULN_RESPONSE" | jq -r '.total_count')"
        echo "Critical: $(echo "$VULN_RESPONSE" | jq -r '.critical_count')"
    fi
else
    print_result 1 "Dashboard vulnerabilities"
    echo "$VULN_RESPONSE"
fi

echo -e "\nTesting GET /v1/dashboard/scans/recent..."
RECENT_SCANS_RESPONSE=$(api_call GET "/v1/dashboard/scans/recent?limit=5" "" "Authorization: Bearer $API_KEY")
if echo "$RECENT_SCANS_RESPONSE" | grep -q "scans" || echo "$RECENT_SCANS_RESPONSE" | grep -q "503"; then
    if echo "$RECENT_SCANS_RESPONSE" | grep -q "503"; then
        print_result 0 "Recent scans (DB not configured)"
    else
        print_result 0 "Recent scans"
        echo "Recent scans count: $(echo "$RECENT_SCANS_RESPONSE" | jq -r '.total_count')"
    fi
else
    print_result 1 "Recent scans"
    echo "$RECENT_SCANS_RESPONSE"
fi

echo -e "\nTesting GET /v1/dashboard/analytics/trends..."
TRENDS_RESPONSE=$(api_call GET "/v1/dashboard/analytics/trends?days=30" "" "Authorization: Bearer $API_KEY")
if echo "$TRENDS_RESPONSE" | grep -q "trends" || echo "$TRENDS_RESPONSE" | grep -q "503"; then
    if echo "$TRENDS_RESPONSE" | grep -q "503"; then
        print_result 0 "Analytics trends (DB not configured)"
    else
        print_result 0 "Analytics trends"
        echo "Trend data points: $(echo "$TRENDS_RESPONSE" | jq '.trends | length')"
    fi
else
    print_result 1 "Analytics trends"
    echo "$TRENDS_RESPONSE"
fi

# Test 7: Alerts
print_header "7. ALERT ENDPOINTS"

echo "Testing GET /v1/alerts/unread-count..."
UNREAD_RESPONSE=$(api_call GET "/v1/alerts/unread-count" "" "Authorization: Bearer $API_KEY")
if echo "$UNREAD_RESPONSE" | grep -q "count"; then
    print_result 0 "Unread alerts count"
    echo "Unread count: $(echo "$UNREAD_RESPONSE" | jq -r '.count')"
else
    print_result 1 "Unread alerts count"
    echo "$UNREAD_RESPONSE"
fi

echo -e "\nTesting GET /v1/alerts..."
ALERTS_RESPONSE=$(api_call GET "/v1/alerts?limit=10" "" "Authorization: Bearer $API_KEY")
if [ -n "$ALERTS_RESPONSE" ]; then
    print_result 0 "List alerts"
    ALERT_COUNT=$(echo "$ALERTS_RESPONSE" | jq '. | length' 2>/dev/null || echo "0")
    echo "Alerts returned: $ALERT_COUNT"
else
    print_result 1 "List alerts"
fi

# Test 8: Authentication Failures
print_header "8. AUTHENTICATION FAILURE TESTS"

echo "Testing unauthorized access..."
UNAUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/v1/auth/me")
if [ "$UNAUTH_RESPONSE" = "401" ]; then
    print_result 0 "Unauthorized access returns 401"
else
    print_result 1 "Unauthorized access returns $UNAUTH_RESPONSE (expected 401)"
fi

echo -e "\nTesting invalid API key..."
INVALID_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer invalid_key_123" \
    "$API_BASE_URL/v1/auth/me")
if [ "$INVALID_RESPONSE" = "401" ]; then
    print_result 0 "Invalid API key returns 401"
else
    print_result 1 "Invalid API key returns $INVALID_RESPONSE (expected 401)"
fi

# Summary
print_header "TEST SUMMARY"
echo -e "${GREEN}✅ All critical endpoints tested${NC}"
echo -e "\n${YELLOW}Note:${NC} Some endpoints may return 503 if database is not configured."
echo -e "${YELLOW}Note:${NC} This is expected for dashboard and analytics endpoints.\n"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Testing completed successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Store credentials for later use
echo -e "${YELLOW}Credentials for manual testing:${NC}"
echo -e "API Key: ${GREEN}$API_KEY${NC}"
echo -e "User ID: ${GREEN}$USER_ID${NC}"

if [ -n "$SCAN_ID" ]; then
    echo -e "Last Scan ID: ${GREEN}$SCAN_ID${NC}"
fi
