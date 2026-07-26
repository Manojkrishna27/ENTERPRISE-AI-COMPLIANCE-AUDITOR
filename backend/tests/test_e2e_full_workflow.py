import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import db, SessionLocal
from app.models.contract import ContractChunk, ContractVersion

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def create_sample_pdf_bytes():
    return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"

def test_e2e_system_endpoints(client):
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_ready = client.get("/api/ready")
    assert res_ready.status_code in [200, 503]

def test_e2e_complete_workflow(client):
    # --- 1. User Registration & Authentication ---
    admin_email = f"e2e_admin_{uuid.uuid4().hex[:6]}@company.com"
    reg_payload = {
        "email": admin_email,
        "password": "AdminPassword123!",
        "full_name": "E2E Admin User",
        "role": "Admin"
    }
    res_reg = client.post("/api/auth/register", json=reg_payload)
    assert res_reg.status_code == 201
    assert res_reg.json()["user"]["email"] == admin_email

    # Login
    login_payload = {
        "email": admin_email,
        "password": "AdminPassword123!"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get /me profile
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == admin_email

    # --- 2. Admin Operations & Departments ---
    res_dept = client.post("/api/admin/departments", json={
        "name": f"Legal Operations {uuid.uuid4().hex[:4]}",
        "description": "Legal & Compliance Auditing Dept"
    }, headers=headers)
    assert res_dept.status_code == 201
    dept_id = res_dept.json()["department"]["id"]

    res_depts = client.get("/api/admin/departments", headers=headers)
    assert res_depts.status_code == 200
    assert len(res_depts.json()) > 0

    res_users = client.get("/api/admin/users", headers=headers)
    assert res_users.status_code == 200
    assert any(u["email"] == admin_email for u in res_users.json())

    # --- 3. Policy Management ---
    pdf_file_bytes = create_sample_pdf_bytes()
    policy_upload_files = {
        "file": ("test_policy.pdf", pdf_file_bytes, "application/pdf")
    }
    policy_upload_data = {
        "name": "GDPR Data Processing Agreement Standard",
        "description": "Standard corporate privacy and data processing policy",
        "category": "GDPR"
    }
    res_policy = client.post("/api/policies", data=policy_upload_data, files=policy_upload_files, headers=headers)
    assert res_policy.status_code == 201
    policy_id = res_policy.json()["policy"]["id"]

    res_policies = client.get("/api/policies", headers=headers)
    assert res_policies.status_code == 200
    assert any(p["id"] == policy_id for p in res_policies.json())

    # --- 4. Contract Management ---
    contract_files = {
        "file": ("vendor_agreement.pdf", pdf_file_bytes, "application/pdf")
    }
    contract_data = {
        "name": "Master Services Agreement - Acme Corp",
        "description": "Vendor MSA agreement with indemnification & liability terms",
        "department_id": dept_id
    }
    res_contract = client.post("/api/contracts", data=contract_data, files=contract_files, headers=headers)
    assert res_contract.status_code == 201
    contract_id = res_contract.json()["contract"]["id"]
    version_id = res_contract.json()["version"]["id"]

    # Insert a parsed ContractChunk for analysis testing
    session = SessionLocal()
    chunk = ContractChunk(
        version_id=version_id,
        chunk_text="The Vendor shall limit total aggregate liability to $10,000. Privacy guidelines must adhere to standard GDPR compliance specifications.",
        page_number=1,
        paragraph_number=1,
        chunk_position=1
    )
    session.add(chunk)
    session.commit()
    session.close()

    # List Contracts
    res_contracts = client.get("/api/contracts", headers=headers)
    assert res_contracts.status_code == 200
    assert any(c["id"] == contract_id for c in res_contracts.json())

    # Get Contract Details
    res_contract_detail = client.get(f"/api/contracts/{contract_id}", headers=headers)
    assert res_contract_detail.status_code == 200
    assert res_contract_detail.json()["id"] == contract_id
    assert len(res_contract_detail.json()["versions"]) > 0

    # Get Version Details
    res_version_detail = client.get(f"/api/contracts/{contract_id}/versions/{version_id}", headers=headers)
    assert res_version_detail.status_code == 200
    assert res_version_detail.json()["id"] == version_id

    # --- 5. RAG Compliance Analysis ---
    res_analyze = client.post(f"/api/analysis/contracts/{contract_id}/version/{version_id}/analyze", headers=headers)
    assert res_analyze.status_code == 200
    assert "findings_count" in res_analyze.json()
    assert "compliance_score" in res_analyze.json()

    # Get Findings
    res_findings = client.get(f"/api/analysis/contracts/{contract_id}/version/{version_id}/findings", headers=headers)
    assert res_findings.status_code == 200
    assert isinstance(res_findings.json(), list)

    # --- 6. RAG Copilot Chat ---
    copilot_payload = {
        "question": "What are the liability limits and data privacy requirements in this contract?"
    }
    res_copilot = client.post(f"/api/analysis/contracts/{contract_id}/version/{version_id}/copilot", json=copilot_payload, headers=headers)
    assert res_copilot.status_code == 200
    assert "answer" in res_copilot.json()
    assert "metrics" in res_copilot.json()

    # --- 7. Report Generation & Download ---
    res_report_gen = client.post(f"/api/reports/contracts/{contract_id}/version/{version_id}/generate", headers=headers)
    assert res_report_gen.status_code == 201
    report_id = res_report_gen.json()["report"]["id"]

    res_reports = client.get("/api/reports", headers=headers)
    assert res_reports.status_code == 200
    assert any(r["id"] == report_id for r in res_reports.json())

    res_download = client.get(f"/api/reports/{report_id}/download", headers=headers)
    assert res_download.status_code == 200
    assert res_download.headers["content-type"] == "application/pdf"
    assert len(res_download.content) > 0

    # --- 8. Dashboard Analytics & Search ---
    res_dash = client.get("/api/dashboard", headers=headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "kpis" in dash_data
    assert dash_data["kpis"]["total_contracts"] >= 1
    assert dash_data["kpis"]["total_policies"] >= 1

    # Search API
    res_search = client.get("/api/search?q=GDPR", headers=headers)
    assert res_search.status_code == 200
    assert "contracts" in res_search.json()
    assert "policies" in res_search.json()

    # Audit Logs
    res_logs = client.get("/api/admin/audit-logs", headers=headers)
    assert res_logs.status_code == 200
    assert len(res_logs.json()) > 0

    # --- 9. Logout ---
    res_logout = client.post("/api/auth/logout", headers=headers)
    assert res_logout.status_code == 200

    # Verify Revoked Token
    res_revoked = client.get("/api/auth/me", headers=headers)
    assert res_revoked.status_code == 401
