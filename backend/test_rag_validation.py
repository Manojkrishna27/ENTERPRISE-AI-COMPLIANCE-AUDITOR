import os
import sys
import time

import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

BASE_URL = "http://localhost:5000/api"

print("==================================================")
print("PHASE 5: RAG & UPLOAD VALIDATION SCRIPT")
print("==================================================")


def print_result(step, success, msg):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {step}: {msg}")
    if not success:
        sys.exit(1)


def create_dummy_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "EMPLOYMENT CONTRACT")
    c.drawString(100, 730, "This contract is between The Company and John Doe.")
    c.drawString(
        100,
        710,
        "1. Salary: The employee shall be paid a base salary of $100,000 per year.",
    )
    c.drawString(
        100,
        690,
        "2. Risk Clause: The employee is liable for any data breaches up to $1,000,000.",
    )
    c.drawString(
        100, 670, "3. Termination: Either party may terminate with 30 days notice."
    )
    c.showPage()

    # Page 2
    c.drawString(
        100, 750, "4. Confidentiality: The employee must not disclose company secrets."
    )
    c.drawString(100, 730, "This agreement is governed by the laws of California.")
    c.save()


try:
    # 0. Wait for backend to be ready
    print("Waiting for backend API to be ready...")
    for _ in range(30):
        try:
            requests.get(f"{BASE_URL}/health")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        print_result("Startup", False, "Backend failed to start in time.")

    # 1. Login to get token
    res = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@company.com", "password": "admin123"},
    )
    if res.status_code != 200:
        print_result("Login", False, f"Failed to login: {res.text}")
    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Dummy PDF
    pdf_path = "dummy_contract.pdf"
    create_dummy_pdf(pdf_path)

    # 3. Upload PDF
    print(
        "\nUploading document (this will trigger PyMuPDF parsing, LlamaIndex Chunking, and Embedding generation...)"
    )
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path, f, "application/pdf")}
        data = {"name": "Test Employment Contract"}
        res = requests.post(
            f"{BASE_URL}/contracts", headers=headers, files=files, data=data
        )

    print_result(
        "Upload & Parsing",
        res.status_code == 201,
        f"Status: {res.status_code} - {res.text}",
    )

    contract_data = res.json()
    contract_id = contract_data["contract"]["id"]
    version_id = contract_data["version"]["id"]
    chunks_count = contract_data.get("chunks_count", 0)
    print_result(
        "Chunking Validation",
        chunks_count > 0,
        f"Generated {chunks_count} chunks successfully.",
    )

    # 4. RAG Valid Query
    print("\nExecuting Valid RAG Query: 'What are the highest-risk clauses?'")
    rag_payload = {"question": "What are the highest-risk clauses?"}
    res = requests.post(
        f"{BASE_URL}/analysis/contracts/{contract_id}/version/{version_id}/copilot",
        headers=headers,
        json=rag_payload,
    )

    print_result(
        "RAG API Call",
        res.status_code == 200,
        f"Status: {res.status_code} - {res.text}",
    )
    rag_data = res.json()
    answer = rag_data.get("answer", "")
    metrics = rag_data.get("metrics", {})

    print("\n--- Valid AI Response ---")
    print(answer)
    print("-------------------------\n")
    print_result(
        "RAG Quality",
        "1,000,000" in answer or "data breach" in answer.lower(),
        "Retrieved and identified the risk clause.",
    )
    print_result(
        "RAG Telemetry",
        metrics.get("model_used") is not None,
        f"Metrics returned: {metrics}",
    )

    # 5. RAG Negative Query (Hallucination Test)
    print("\nExecuting Negative RAG Query: 'What is the CEO salary?'")
    neg_payload = {"question": "What is the CEO salary?"}
    res = requests.post(
        f"{BASE_URL}/analysis/contracts/{contract_id}/version/{version_id}/copilot",
        headers=headers,
        json=neg_payload,
    )

    print_result(
        "Negative RAG API Call", res.status_code == 200, f"Status: {res.status_code}"
    )
    neg_data = res.json()
    neg_answer = neg_data.get("answer", "")

    print("\n--- Negative AI Response ---")
    print(neg_answer)
    print("----------------------------\n")
    print_result(
        "Hallucination Resistance",
        "insufficient evidence" in neg_answer.lower()
        or "not mention" in neg_answer.lower()
        or "could not find" in neg_answer.lower(),
        "AI correctly identified missing context.",
    )

    # Cleanup
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    print("\n==================================================")
    print("ALL LIVE RAG TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

except Exception as e:
    import traceback

    traceback.print_exc()
    print_result("Execution", False, str(e))
