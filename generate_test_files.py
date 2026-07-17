import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

def create_pdf(filename, title, content_paragraphs):
    os.makedirs('test_documents', exist_ok=True)
    filepath = os.path.join('test_documents', filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=HexColor('#1E293B'),
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=HexColor('#4F46E5'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=HexColor('#334155'),
        spaceAfter=8
    )
    
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    for section_title, paragraphs in content_paragraphs:
        if section_title:
            story.append(Paragraph(section_title, section_style))
        for p_text in paragraphs:
            story.append(Paragraph(p_text, body_style))
        story.append(Spacer(1, 8))
        
    doc.build(story)
    print(f"Created test PDF: {filepath}")

def generate_test_data():
    # 1. GDPR Compliance Policy Document
    policy_paragraphs = [
        ("Section 1: Data Protection & Access Control Guidelines", [
            "Paragraph 1: All customer personally identifiable information (PII) must be encrypted both in transit using TLS 1.3 and at rest using AES-256 bits keys. Access keys must be rotated every 90 days without exception.",
            "Paragraph 2: Authentication controls must require multi-factor verification (MFA) for all administrative and auditor privileges. Passwords must consist of a minimum of 14 characters, combining alphanumeric and special marks."
        ]),
        ("Section 2: Security Breach Notification Timelines", [
            "Paragraph 1: In the event of a confirmed security incident or unauthorized access to corporate database tables containing PII, compliance operations must trigger notification alerts to regulatory authorities.",
            "Paragraph 2: All vendor service agreements must mandate security breach notification reporting to the compliance board within seventy-two (72) hours of incident identification. Failure to notify within this timeframe constitutes a material breach."
        ]),
        ("Section 3: PII Data Retention and Erasure Rules", [
            "Paragraph 1: Personally identifiable information must only be retained for as long as necessary to fulfill business transactions. The maximum retention limit for inactive user profiles is set at two (2) years.",
            "Paragraph 2: Upon service termination, all customer data must be purged or anonymized within thirty (30) days from all primary drives and backup systems. Proof of erasure certification must be delivered."
        ])
    ]
    
    # 2. Vendor Service Agreement (Contract with violations)
    contract_paragraphs = [
        ("ARTICLE I: Scope of Services and Performance", [
            "Paragraph 1: This Master Services Agreement is entered into by Acme Services Corp (Vendor) and Global Corp. Vendor agrees to provide cloud-based infrastructure optimization and technical maintenance operations.",
            "Paragraph 2: Vendor agrees to maintain server uptime SLAs of 99.9% measured on a monthly basis, excluding planned maintenance windows communicated in writing at least forty-eight hours prior."
        ]),
        ("ARTICLE II: Privacy and Data Protection Controls", [
            "Paragraph 1: Vendor shall have access to customer database tables for system diagnostics. Vendor will ensure standard password protection guidelines are followed to secure access credentials.",
            "Paragraph 2: In the event of a security breach or system compromise, Vendor agrees to conduct an internal review and notify the customer within fifteen (15) business days after resolving the incident."
        ]),
        ("ARTICLE III: Data Storage and Term Policies", [
            "Paragraph 1: The term of this agreement shall run for five years. Vendor reserves the right to retain transaction records, database indexes, and logs indefinitely to optimize operational machine learning models.",
            "Paragraph 2: Following termination, Customer may request data retrieval. Vendor will remove customer configurations from active directories within ninety (90) calendar days."
        ])
    ]
    
    create_pdf("GDPR_Compliance_Policy.pdf", "Corporate GDPR & Security Compliance Standard", policy_paragraphs)
    create_pdf("Vendor_Service_Agreement.pdf", "Vendor Master Services Agreement", contract_paragraphs)

if __name__ == '__main__':
    generate_test_data()
