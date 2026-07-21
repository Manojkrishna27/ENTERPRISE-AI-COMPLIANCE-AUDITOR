import sys
import json
import uuid
import requests
import time

BASE_URL = "http://localhost:5000/api"

print("==================================================")
print("PHASE 5: LIVE SYSTEM VALIDATION SCRIPT")
print("==================================================")

# Generate unique credentials for the test run
test_email = f"auditor_{uuid.uuid4().hex[:6]}@example.com"
test_password = "SecurePassword123!"
token = None
contract_id = None
version_id = None
department_id = None

def print_result(step, success, msg):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {step}: {msg}")
    if not success:
        sys.exit(1)

try:
    # 1. Health Check
    res = requests.get(f"{BASE_URL}/health")
    print_result("System Health", res.status_code == 200, "Backend API is responsive.")

    # 2. Registration & Authentication
    payload = {
        "email": test_email,
        "password": test_password,
        "full_name": "Test Auditor",
        "role": "Auditor"
    }
    res = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print_result("User Registration", res.status_code == 201, "Test user registered.")
    
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": test_email, "password": test_password})
    print_result("User Login", res.status_code == 200, "JWT retrieved.")
    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Security Validation (Negative Test - Revoked Token)
    # Skip actual logout here so we can continue testing, but we'll test unauthorized access
    bad_headers = {"Authorization": "Bearer invalid.token.string"}
    res = requests.get(f"{BASE_URL}/auth/me", headers=bad_headers)
    print_result("Security (Invalid JWT)", res.status_code == 401, "Rejected invalid token.")

    print("\n--------------------------------------------------")
    print("WARNING: Upload & RAG testing requires valid API keys in .env")
    print("If OPENAI_API_KEY or GEMINI_API_KEY is missing, ingestion will fail.")
    print("--------------------------------------------------\n")

    print("Next Steps for manual validation:")
    print("1. Log in to the frontend UI.")
    print("2. Upload a Contract PDF.")
    print("3. Monitor 'docker compose logs backend' for structured 'rag_logger' metrics.")
    print("4. Execute the 'Summarize this contract' prompt.")
    print("5. Ask 'What is the CEO salary?' to verify hallucination resistance.")

except Exception as e:
    print_result("Execution", False, str(e))
