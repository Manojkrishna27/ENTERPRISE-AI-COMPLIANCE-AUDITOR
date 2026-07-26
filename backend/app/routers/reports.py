import io
import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.contract import Contract, ContractVersion
from app.models.audit import AIFinding, Report
from app.models.user import User
from app.services.s3_service import storage_service
from app.utils.security import log_audit

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("", summary="List audit reports", description="Fetch list of audit reports filtered by contract ID")
def list_reports(
    contract_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Report)
    if contract_id:
        query = query.filter(Report.contract_id == contract_id)
    reports = query.order_by(Report.created_at.desc()).all()
    return [r.to_dict() for r in reports]


@router.post("/contracts/{contract_id}/version/{ver_id}/generate", status_code=status.HTTP_201_CREATED, summary="Generate compliance PDF report", description="Generate executive PDF compliance audit report for contract version")
def generate_report(
    contract_id: str,
    ver_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    version = db.query(ContractVersion).filter(ContractVersion.id == ver_id, ContractVersion.contract_id == contract_id).first()

    if not contract or not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract or version not found")

    findings = db.query(AIFinding).filter(AIFinding.version_id == ver_id).all()

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=15,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []
    story.append(Paragraph("Enterprise Contract Compliance Audit Report", title_style))
    story.append(Paragraph(f"<b>Contract Name:</b> {contract.name}", body_style))
    story.append(Paragraph(f"<b>Version Reviewed:</b> Version {version.version_number}", body_style))
    story.append(Paragraph(f"<b>Date Generated:</b> {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph(f"<b>Audited By:</b> {current_user.full_name} ({current_user.role})", body_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Executive Summary", section_style))
    high_count = sum(1 for f in findings if f.risk_level == 'High')
    med_count = sum(1 for f in findings if f.risk_level == 'Medium')
    low_count = sum(1 for f in findings if f.risk_level == 'Low')

    compliance_score = 100 - (high_count * 15 + med_count * 5 + low_count * 1)
    compliance_score = max(0, min(100, compliance_score))

    summary_text = (
        f"A thorough Retrieval-Augmented Generation (RAG) audit was conducted on this contract version "
        f"against all active compliance guidelines. A total of <b>{len(findings)}</b> risks were identified. "
        f"The contract has been assigned a compliance integrity rating of <b>{compliance_score}%</b>."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    table_data = [
        [Paragraph("<b>Risk Metric</b>", bold_body_style), Paragraph("<b>Count</b>", bold_body_style), Paragraph("<b>System Severity</b>", bold_body_style)],
        [Paragraph("High Risk Violations", body_style), str(high_count), "Requires Immediate Amendment"],
        [Paragraph("Medium Risk Violations", body_style), str(med_count), "Recommended Remediation"],
        [Paragraph("Low Risk Anomalies", body_style), str(low_count), "Minor Adjustment"],
    ]
    t = Table(table_data, colWidths=[150, 80, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TEXTCOLOR', (1,1), (1,-1), colors.HexColor('#DC2626')),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Detailed Compliance Findings & Citations", section_style))

    if not findings:
        story.append(Paragraph("No compliance breaches or policy deviations detected in this version.", body_style))
    else:
        for idx, f in enumerate(findings):
            story.append(Paragraph(f"<b>Finding #{idx+1}: {f.title}</b>", ParagraphStyle('Sub', parent=body_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'))))
            story.append(Paragraph(f"<b>Category:</b> {f.category}  |  <b>Risk Level:</b> {f.risk_level}  |  <b>Confidence Score:</b> {int(f.confidence_score*100)}%", body_style))
            story.append(Paragraph(f"<b>Explanation:</b> {f.explanation}", body_style))
            if f.business_impact:
                story.append(Paragraph(f"<b>Business Impact:</b> {f.business_impact}", body_style))
            if f.recommendation:
                story.append(Paragraph(f"<b>Remediation Action:</b> {f.recommendation}", body_style))

            citation_text = f"<b>Citations:</b> Contract Page {f.contract_page_number or 'N/A'}, Paragraph {f.contract_paragraph_number or 'N/A'}"
            if f.policy:
                citation_text += f" | Policy '{f.policy.name}' Page {f.policy_page_number or 'N/A'}, Paragraph {f.policy_paragraph_number or 'N/A'}"
            story.append(Paragraph(citation_text, body_style))

            story.append(Spacer(1, 5))
            divider = Table([[""]], colWidths=[530], rowHeights=[1])
            divider.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
            story.append(divider)
            story.append(Spacer(1, 10))

    doc.build(story)
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.getvalue()

    report_id = str(uuid.uuid4())
    s3_key = f"reports/{report_id}.pdf"

    try:
        storage_service.upload_file(pdf_bytes, s3_key)

        report = Report(
            id=report_id,
            name=f"Compliance Audit - {contract.name} (V{version.version_number})",
            report_type="Compliance Report",
            s3_key=s3_key,
            created_by=current_user.id,
            contract_id=contract.id
        )
        db.add(report)
        db.commit()

        client_ip = request.client.host if request.client else "System"
        log_audit(current_user.id, "REPORT_GENERATE", f"Generated compliance report for contract: {contract.name}", ip_address=client_ip)

        return {
            "msg": "Report generated successfully",
            "report": report.to_dict()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report: {str(e)}")


@router.get("/{id}/download", summary="Download report PDF", description="Download generated compliance PDF report binary file")
def download_report(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    try:
        local_path = storage_service.get_file_path(report.s3_key)
        download_name = f"{report.name.replace(' ', '_')}.pdf"
        return FileResponse(
            path=local_path,
            media_type='application/pdf',
            filename=download_name
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve report binary file: {str(e)}")
