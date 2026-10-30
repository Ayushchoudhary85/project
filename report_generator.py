"""
PDF Scan Report Generator for PhishGuard using ReportLab.
Produces clean, structured security audit reports in memory.
"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_file_scan_pdf(scan_data: dict) -> bytes:
    """Generate a downloadable PDF audit report for a file scan."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b")
    )
    h2_style = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    mono_style = ParagraphStyle(
        "ReportMono",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    elements = []

    # Title & Metadata
    elements.append(Paragraph("PHISHGUARD &bull; CYBER INTELLIGENCE REPORT", title_style))
    elements.append(Paragraph(f"Forensic File Security Assessment &bull; ID #{scan_data.get('id', 'N/A')}", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#00e599"), spaceAfter=14))

    # Verdict Badge color
    status = scan_data.get("status", "Limited Analysis")
    if status == "Clean":
        status_color = colors.HexColor("#10b981")
    elif status == "Suspicious":
        status_color = colors.HexColor("#f59e0b")
    elif status == "Malicious":
        status_color = colors.HexColor("#ef4444")
    else:
        status_color = colors.HexColor("#64748b")

    # Overview Table
    risk_score = scan_data.get("risk_score")
    risk_label = f" (Risk: {risk_score}/100)" if risk_score is not None else ""
    entropy_val = scan_data.get("entropy")
    entropy_txt = f"{entropy_val} bits ({scan_data.get('entropy_assessment', 'Normal')})" if entropy_val not in (None, "", "N/A") else "N/A"

    overview_data = [
        [Paragraph("<b>Target Filename:</b>", body_style), Paragraph(str(scan_data.get("filename", "-")), body_style)],
        [Paragraph("<b>Scan Verdict:</b>", body_style), Paragraph(f"<b>{status}</b>{risk_label}", ParagraphStyle("S", parent=body_style, textColor=status_color, fontSize=11))],
        [Paragraph("<b>Threat Identification:</b>", body_style), Paragraph(str(scan_data.get("threat_name") or "None Detected"), body_style)],
        [Paragraph("<b>Inspection Engine:</b>", body_style), Paragraph(str(scan_data.get("engine_used", "Static Inspector")), body_style)],
        [Paragraph("<b>Timestamp (UTC):</b>", body_style), Paragraph(str(scan_data.get("scan_timestamp", "-")), body_style)],
        [Paragraph("<b>File Size:</b>", body_style), Paragraph(f"{scan_data.get('file_size', 0):,} bytes", body_style)],
        [Paragraph("<b>Detected MIME:</b>", body_style), Paragraph(str(scan_data.get("mime_type", "-")), body_style)],
        [Paragraph("<b>Shannon Byte Entropy:</b>", body_style), Paragraph(entropy_txt, body_style)]
    ]

    t_overview = Table(overview_data, colWidths=[140, 390])
    t_overview.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t_overview)
    elements.append(Spacer(1, 14))

    # Cryptographic Hashes Table
    elements.append(Paragraph("Cryptographic Hashes", h2_style))
    hash_data = [
        [Paragraph("<b>SHA-256</b>", body_style), Paragraph(str(scan_data.get("sha256", "-")), mono_style)],
        [Paragraph("<b>SHA-1</b>", body_style), Paragraph(str(scan_data.get("sha1", "-")), mono_style)],
        [Paragraph("<b>MD5</b>", body_style), Paragraph(str(scan_data.get("md5", "-")), mono_style)]
    ]
    t_hashes = Table(hash_data, colWidths=[90, 440])
    t_hashes.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_hashes)
    elements.append(Spacer(1, 14))

    # Threat Indicators
    elements.append(Paragraph("Detected Threat Indicators", h2_style))
    indicators = scan_data.get("threat_indicators", [])
    if not indicators:
        elements.append(Paragraph("No anomalous indicators or signature patterns detected.", body_style))
    else:
        for ind in indicators:
            elements.append(Paragraph(f"&bull; {ind}", body_style))
            elements.append(Spacer(1, 2))

    elements.append(Spacer(1, 10))

    # Security Recommendations
    elements.append(Paragraph("Security Directives & Guidance", h2_style))
    recommendations = scan_data.get("recommendations", [])
    if not recommendations:
        elements.append(Paragraph("Maintain standard endpoint security precautions.", body_style))
    else:
        for rec in recommendations:
            elements.append(Paragraph(f"&bull; {rec}", body_style))
            elements.append(Spacer(1, 2))

    # Footer note
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    elements.append(Paragraph(
        "Notice: This forensic audit report is generated automatically by PhishGuard. "
        "Offline static analysis cannot detect zero-day exploits or active payloads without continuous signature monitoring.",
        subtitle_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
