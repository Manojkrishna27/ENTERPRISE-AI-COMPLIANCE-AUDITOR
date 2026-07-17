import io
import os
import uuid
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.database import db
from app.models.contract import Contract, ContractVersion
from app.models.audit import AIFinding, Report
from app.models.user import User
from app.services.s3_service import storage_service
from app.utils.security import log_audit

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['GET'])
@jwt_required()
def list_reports():
    contract_id = request.args.get('contract_id')
    query = Report.query
    if contract_id:
        query = query.filter_by(contract_id=contract_id)
    reports = query.order_by(Report.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reports]), 200


@reports_bp.route('/contracts/<contract_id>/version/<ver_id>/generate', methods=['POST'])
@jwt_required()
def generate_report(contract_id, ver_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    contract = Contract.query.get(contract_id)
    version = ContractVersion.query.filter_by(id=ver_id, contract_id=contract_id).first()
    
    if not contract or not version:
        return jsonify({"msg": "Contract or version not found"}), 404
        
    findings = AIFinding.query.filter_by(version_id=ver_id).all()
    
    # Create PDF in-memory buffer
    pdf_buffer = io.BytesIO()
    
    # Setup document template
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#0F172A'), # Charcoal / Navy slate
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
    
    # Document story elements
    story = []
    
    # Header Section
    story.append(Paragraph("Enterprise Contract Compliance Audit Report", title_style))
    story.append(Paragraph(f"<b>Contract Name:</b> {contract.name}", body_style))
    story.append(Paragraph(f"<b>Version Reviewed:</b> Version {version.version_number}", body_style))
    story.append(Paragraph(f"<b>Date Generated:</b> {version.created_at.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph(f"<b>Audited By:</b> {user.full_name} ({user.role})", body_style))
    story.append(Spacer(1, 15))
    
    # Executive Summary Card
    story.append(Paragraph("Executive Summary", section_style))
    high_count = sum(1 for f in findings if f.risk_level == 'High')
    med_count = sum(1 for f in findings if f.risk_level == 'Medium')
    low_count = sum(1 for f in findings if f.risk_level == 'Low')
    
    compliance_score = 100 - (high_count * 15 + med_count * 5 + low_count * 1)
    compliance_score = max(0, min(100, compliance_score)) # Keep bounds [0, 100]
    
    summary_text = (
        f"A thorough Retrieval-Augmented Generation (RAG) audit was conducted on this contract version "
        f"against all active compliance guidelines. A total of <b>{len(findings)}</b> risks were identified. "
        f"The contract has been assigned a compliance integrity rating of <b>{compliance_score}%</b>."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))
    
    # Summary Table
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
        ('TEXTCOLOR', (1,1), (1,-1), colors.HexColor('#DC2626')), # highlight counts
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Detailed Clause Audits
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
            
            # Citations
            citation_text = f"<b>Citations:</b> Contract Page {f.contract_page_number or 'N/A'}, Paragraph {f.contract_paragraph_number or 'N/A'}"
            if f.policy:
                citation_text += f" | Policy '{f.policy.name}' Page {f.policy_page_number or 'N/A'}, Paragraph {f.policy_paragraph_number or 'N/A'}"
            story.append(Paragraph(citation_text, body_style))
            
            # Divider line
            story.append(Spacer(1, 5))
            divider = Table([[""]], colWidths=[530], rowHeights=[1])
            divider.setStyle(TableStyle([('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
            story.append(divider)
            story.append(Spacer(1, 10))
            
    # Build Document
    doc.build(story)
    
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.getvalue()
    
    # Save Report record and file
    report_id = str(uuid.uuid4())
    s3_key = f"reports/{report_id}.pdf"
    
    try:
        storage_service.upload_file(pdf_bytes, s3_key)
        
        report = Report(
            id=report_id,
            name=f"Compliance Audit - {contract.name} (V{version.version_number})",
            report_type="Compliance Report",
            s3_key=s3_key,
            created_by=user_id,
            contract_id=contract.id
        )
        db.session.add(report)
        db.session.commit()
        
        log_audit(user_id, "REPORT_GENERATE", f"Generated compliance report for contract: {contract.name}")
        
        return jsonify({
            "msg": "Report generated successfully",
            "report": report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating PDF report: {e}")
        return jsonify({"msg": "Failed to generate report", "error": str(e)}), 500


@reports_bp.route('/<id>/download', methods=['GET'])
@jwt_required()
def download_report(id):
    report = Report.query.get(id)
    if not report:
        return jsonify({"msg": "Report not found"}), 404
        
    try:
        local_path = storage_service.get_file_path(report.s3_key)
        return send_file(
            local_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{report.name.replace(' ', '_')}.pdf"
        )
    except Exception as e:
        print(f"Error fetching report for download: {e}")
        return jsonify({"msg": "Failed to retrieve report binary file", "error": str(e)}), 500
