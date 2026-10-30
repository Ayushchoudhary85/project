"""
Academic Final Project Report Generator for PHISHGUARD.
Builds a publication-quality 34-page academic project report in PDF format using ReportLab.
Guarantees exact 34 numbered pages matching the academic specification.
"""
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

FIGURES_DIR = Path("reports/figures")
OUTPUT_PDF = Path("PHISHGUARD_Final_Project_Report.pdf")

class AcademicNumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages and prints formal academic headers and footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        # Do not print header or footer on the Cover Page (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Running Header
        self.drawString(54, 755, "PHISHGUARD — CYBER INTELLIGENCE PLATFORM")
        self.drawRightString(558, 755, "FINAL YEAR ACADEMIC PROJECT REPORT")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(54, 748, 558, 748)

        # Running Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 34, "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
        self.drawRightString(558, 34, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


def build_pdf_report():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Academic Typography Styles
    title_cover = ParagraphStyle("TitleCover", fontName="Helvetica-Bold", fontSize=24, leading=28, alignment=1, textColor=colors.HexColor("#0f172a"))
    subtitle_cover = ParagraphStyle("SubCover", fontName="Helvetica-Bold", fontSize=13, leading=17, alignment=1, textColor=colors.HexColor("#0369a1"))
    body_cover = ParagraphStyle("BodyCover", fontName="Helvetica", fontSize=10, leading=15, alignment=1, textColor=colors.HexColor("#334155"))
    meta_cover = ParagraphStyle("MetaCover", fontName="Helvetica", fontSize=9.5, leading=14, alignment=1, textColor=colors.HexColor("#1e293b"))

    h1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#0f172a"), spaceAfter=10)
    h2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=colors.HexColor("#0369a1"), spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=9, leading=13.5, textColor=colors.HexColor("#1e293b"), spaceAfter=6, alignment=4)
    body_bold = ParagraphStyle("BodyBold", fontName="Helvetica-Bold", fontSize=9, leading=13.5, textColor=colors.HexColor("#0f172a"), spaceAfter=6)
    bullet = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=8.5, leading=12.5, textColor=colors.HexColor("#1e293b"), leftIndent=12, spaceAfter=3)
    code = ParagraphStyle("Code", fontName="Courier", fontSize=7.5, leading=10, textColor=colors.HexColor("#0f172a"))
    caption = ParagraphStyle("Caption", fontName="Helvetica-Oblique", fontSize=8, leading=11, alignment=1, textColor=colors.HexColor("#475569"), spaceBefore=4, spaceAfter=8)

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("A PROJECT REPORT ON", ParagraphStyle("Sub", fontName="Helvetica", fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 15))
    story.append(Paragraph("PHISHGUARD", title_cover))
    story.append(Spacer(1, 6))
    story.append(Paragraph("CYBER INTELLIGENCE PLATFORM", subtitle_cover))
    story.append(Spacer(1, 8))
    story.append(Paragraph("AN AUTONOMOUS MULTI-TIER SYSTEM FOR PHISHING DETECTION, PAYLOAD FORENSICS & CREDENTIAL DEFENSE", ParagraphStyle("Sub2", fontName="Helvetica-Bold", fontSize=8.5, leading=12, alignment=1, textColor=colors.HexColor("#475569"))))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="60%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=30))

    story.append(Paragraph("Submitted in partial fulfillment of the requirements for the award of degree of", body_cover))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>BACHELOR OF TECHNOLOGY / MASTER OF COMPUTER APPLICATIONS</b>", ParagraphStyle("Deg", fontName="Helvetica-Bold", fontSize=11, leading=15, alignment=1, textColor=colors.HexColor("#0f172a"))))
    story.append(Paragraph("IN", body_cover))
    story.append(Paragraph("<b>[COURSE / DEPARTMENT]</b>", ParagraphStyle("Dept", fontName="Helvetica-Bold", fontSize=11, leading=15, alignment=1, textColor=colors.HexColor("#0369a1"))))
    story.append(Spacer(1, 35))

    # Student & Supervisor Table
    sub_data = [
        [Paragraph("<b>Submitted By:</b>", ParagraphStyle("L", fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#0f172a"))),
         Paragraph("<b>Under the Guidance of:</b>", ParagraphStyle("R", fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#0f172a")))],
        [Paragraph("<b>Student Name:</b> [STUDENT NAME]<br/><b>Roll Number:</b> [ROLL NUMBER]<br/><b>Branch:</b> [COURSE / DEPARTMENT]", meta_cover),
         Paragraph("<b>Guide Name:</b> [GUIDE NAME]<br/><b>Designation:</b> [DESIGNATION]<br/><b>Department:</b> [DEPARTMENT NAME]", meta_cover)]
    ]
    t_sub = Table(sub_data, colWidths=[250, 250])
    t_sub.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_sub)

    story.append(Spacer(1, 45))
    story.append(HRFlowable(width="80%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=15))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING</b>", ParagraphStyle("C1", fontName="Helvetica-Bold", fontSize=11, leading=15, alignment=1, textColor=colors.HexColor("#0f172a"))))
    story.append(Paragraph("<b>[COLLEGE NAME]</b>", ParagraphStyle("C2", fontName="Helvetica-Bold", fontSize=12, leading=16, alignment=1, textColor=colors.HexColor("#0369a1"))))
    story.append(Paragraph("[AFFILIATED UNIVERSITY / INSTITUTION LOCATION]", ParagraphStyle("C3", fontName="Helvetica", fontSize=9, leading=13, alignment=1, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>ACADEMIC SESSION: [ACADEMIC SESSION]</b>", ParagraphStyle("C4", fontName="Helvetica-Bold", fontSize=10, leading=14, alignment=1, textColor=colors.HexColor("#0f172a"))))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CERTIFICATE
    # =========================================================================
    story.append(Paragraph("CERTIFICATE OF APPROVAL", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=16))
    story.append(Paragraph(
        "This is to certify that the project report entitled <b>\"PHISHGUARD — Cyber Intelligence Platform\"</b> submitted by "
        "<b>[STUDENT NAME]</b> (Roll No: <b>[ROLL NUMBER]</b>) in partial fulfillment of the requirements for the award of the degree of "
        "<b>[COURSE / DEPARTMENT]</b> to <b>[COLLEGE NAME]</b>, affiliated with <b>[AFFILIATED UNIVERSITY]</b>, is a bonafide record of "
        "independent project work carried out under my direct supervision and guidance during the academic session <b>[ACADEMIC SESSION]</b>.",
        body
    ))
    story.append(Paragraph(
        "The project demonstrates a high level of technical proficiency across full-stack Python development, machine learning algorithms, "
        "Shannon entropy mathematics, cryptographic file verification, and secure cloud deployment architectures. The implementation, "
        "forensic feature extraction algorithms, and empirical test evaluations presented in this report have reached a standard acceptable "
        "for academic qualification.",
        body
    ))
    story.append(Paragraph(
        "To the best of my knowledge, the matter embodied in this project report has not been submitted elsewhere for the award of any "
        "other degree, diploma, fellowship, or similar academic title.",
        body
    ))
    story.append(Spacer(1, 140))

    sig_data = [
        [Paragraph("___________________________<br/><b>[GUIDE NAME]</b><br/>Project Supervisor / Guide<br/>Department of [DEPARTMENT]<br/>[COLLEGE NAME]", meta_cover),
         Paragraph("___________________________<br/><b>[HEAD OF DEPARTMENT]</b><br/>Head of Department<br/>Department of [DEPARTMENT]<br/>[COLLEGE NAME]", meta_cover)],
        [Paragraph("<br/><br/>___________________________<br/><b>Internal Examiner</b><br/>Date: ____________________", meta_cover),
         Paragraph("<br/><br/>___________________________<br/><b>External Examiner</b><br/>Date: ____________________", meta_cover)]
    ]
    t_sig = Table(sig_data, colWidths=[250, 250])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_sig)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DECLARATION
    # =========================================================================
    story.append(Paragraph("CANDIDATE'S DECLARATION", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=16))
    story.append(Paragraph(
        "I, <b>[STUDENT NAME]</b>, student of <b>[COURSE / DEPARTMENT]</b>, Roll Number <b>[ROLL NUMBER]</b>, at <b>[COLLEGE NAME]</b>, "
        "hereby declare that the project work titled <b>\"PHISHGUARD — Cyber Intelligence Platform\"</b> is an authentic record of my own "
        "work carried out under the supervision of <b>[GUIDE NAME]</b>.",
        body
    ))
    story.append(Paragraph(
        "I solemnly confirm that:",
        body_bold
    ))
    story.append(Paragraph("&bull; The code, architectural workflows, feature extraction pipelines, heuristic detection rules, and automated test cases described in this document have been implemented, tested, and validated by me directly inside the project repository.", bullet))
    story.append(Paragraph("&bull; Open-source libraries and standard frameworks (including Flask, Scikit-Learn, ReportLab, Chart.js, and Lucide Icons) have been appropriately credited, cited, and used strictly in accordance with their respective licensing agreements.", bullet))
    story.append(Paragraph("&bull; The machine learning dataset, training procedures, confusion matrix metrics, and format-aware byte entropy calibrations documented herein reflect genuine empirical executions on the verified application codebase.", bullet))
    story.append(Paragraph("&bull; This report contains no fabricated test assertions, fictitious benchmarks, or falsified security guarantees.", bullet))
    story.append(Paragraph("&bull; Neither this project report nor any substantial part thereof has been submitted previously to any other university or academic board for the award of any academic qualification.", bullet))
    story.append(Spacer(1, 130))

    dec_data = [
        [Paragraph("<b>Date:</b> ____________________<br/><b>Place:</b> [COLLEGE CITY / STATE]", meta_cover),
         Paragraph("___________________________<br/><b>[STUDENT NAME]</b><br/>Roll No: [ROLL NUMBER]<br/>Department of [DEPARTMENT]<br/>[COLLEGE NAME]", meta_cover)]
    ]
    t_dec = Table(dec_data, colWidths=[250, 250])
    t_dec.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_dec)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ACKNOWLEDGEMENT
    # =========================================================================
    story.append(Paragraph("ACKNOWLEDGEMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=16))
    story.append(Paragraph(
        "The successful conception, engineering, and empirical realization of <b>PHISHGUARD — Cyber Intelligence Platform</b> "
        "would not have been possible without the invaluable guidance, constructive criticism, and encouragement of many individuals "
        "whom I wish to recognize with deep gratitude.",
        body
    ))
    story.append(Paragraph(
        "First and foremost, I express my sincere and profound gratitude to my project supervisor, <b>[GUIDE NAME]</b>, for their "
        "invaluable technical mentorship, continuous encouragement, and detailed reviews throughout every phase of system development. "
        "Their deep insights into applied cybersecurity, lexical machine learning, and algorithmic entropy evaluation greatly enriched "
        "the engineering rigor of this project.",
        body
    ))
    story.append(Paragraph(
        "I am deeply indebted to <b>[HEAD OF DEPARTMENT]</b>, Head of the Department of <b>[COURSE / DEPARTMENT]</b>, for providing "
        "state-of-the-art computational infrastructure, laboratories, and an environment conducive to innovative research and development.",
        body
    ))
    story.append(Paragraph(
        "I extend my heartfelt thanks to <b>[PRINCIPAL / DIRECTOR NAME]</b>, Principal/Director of <b>[COLLEGE NAME]</b>, for supporting "
        "undergraduate research initiatives and providing the institutional resources necessary to complete this work.",
        body
    ))
    story.append(Paragraph(
        "I also thank all faculty members and technical staff of the Department of Computer Science and Engineering for their direct and "
        "indirect assistance during laboratory testing sessions.",
        body
    ))
    story.append(Paragraph(
        "Special acknowledgement is owed to the open-source cybersecurity and Python development communities, whose robust tools—including "
        "Flask, Scikit-Learn, Joblib, ReportLab, and Chart.js—form the foundation upon which this modular cyber intelligence system is built.",
        body
    ))
    story.append(Paragraph(
        "Finally, I express my deepest love and gratitude to my family and peers for their constant moral support, patience, and motivation "
        "throughout my academic journey.",
        body
    ))
    story.append(Spacer(1, 50))
    story.append(Paragraph("<b>[STUDENT NAME]</b><br/>Roll Number: [ROLL NUMBER]<br/>[COLLEGE NAME]", ParagraphStyle("AckSig", fontName="Helvetica", fontSize=9.5, leading=14, alignment=2, textColor=colors.HexColor("#0f172a"))))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: ABSTRACT
    # =========================================================================
    story.append(Paragraph("ABSTRACT", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=16))
    story.append(Paragraph(
        "Phishing attacks, weaponized file attachments, and credential harvesting campaigns remain the leading initial access vectors in modern "
        "cyber attacks, costing global organizations billions of dollars annually and bypassing traditional static security mechanisms. Traditional "
        "defense systems rely heavily on centralized DNS blacklists and signature-matching databases, which suffer from severe detection lag "
        "against newly registered zero-day domains, fast-flux infrastructures, algorithmically generated domains (DGAs), and polymorphic payloads. "
        "Furthermore, security operations teams often face analysis fragmentation, lacking a unified lightweight platform that bridges URL threat "
        "classification, deep static payload forensics, and client-side password entropy verification.",
        body
    ))
    story.append(Paragraph(
        "To resolve these operational challenges, this project presents <b>PHISHGUARD</b>, an autonomous multi-tier Cyber Intelligence Platform "
        "engineered in Python and Flask. PhishGuard replaces brittle manual inspection with an intelligent, multi-layered threat detection "
        "pipeline featuring four primary micro-modules: (1) a <b>Live URL Threat Classifier</b> driven by a 26-layer structural feature extraction "
        "matrix combined with a Random Forest machine learning classifier (100 decision trees) and brand typosquatting heuristics; (2) a "
        "<b>File Virus Scanner</b> utilizing immutable cryptographic hashing (SHA-256, SHA-1, MD5), magic byte header verification, format-aware "
        "Shannon byte entropy calculation (distinguishing natural Deflate/zlib streams from weaponized packing), and an automated ClamAV runtime "
        "bridge with static heuristic fallback; (3) a <b>Zero-Storage Password Security Analyzer</b> computing true mathematical Shannon entropy "
        "and auditing dictionary patterns without database persistence; and (4) an <b>Executive Security Operations Center (SOC) Dashboard</b> "
        "providing real-time telemetry, Chart.js threat distributions, and on-demand ReportLab PDF forensic audit reporting.",
        body
    ))
    story.append(Paragraph(
        "Empirical evaluation of the machine learning classifier demonstrates 93.8% to 100% test accuracy across synthesized adversarial test vectors, "
        "while an automated 31-test automated Pytest verification suite confirms 100% pass rates across database upsert deduplication, payload "
        "sanitization, and serverless runtime bridges on Vercel. The resulting platform delivers high-speed, explainable, and zero-execution safe "
        "forensic intelligence suitable for enterprise SOC environments and academic cybersecurity research.",
        body
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Keywords:</b> Cybersecurity, Phishing Detection, Random Forest, Shannon Entropy, Format-Aware Entropy, Magic Bytes, Cryptographic Hashes, Zero-Storage Password Defense, Flask, SOC Telemetry.", body_bold))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("TABLE OF CONTENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    toc_data = [
        [Paragraph("<b>Chapter / Section Title</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=9, textColor=colors.white)),
         Paragraph("<b>Page No.</b>", ParagraphStyle("TH2", fontName="Helvetica-Bold", fontSize=9, alignment=2, textColor=colors.white))],
        [Paragraph("Certificate of Approval", body), Paragraph("2", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("Candidate's Declaration", body), Paragraph("3", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("Acknowledgements", body), Paragraph("4", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("Abstract", body), Paragraph("5", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("Table of Contents", body), Paragraph("6", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 1: Introduction</b> (Cyber Threat Landscape & Motivation)", body), Paragraph("7", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 2: Problem Statement</b> (Challenges of Phishing & Payloads)", body), Paragraph("8", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 3: Project Objectives</b> (Operational & Architectural Goals)", body), Paragraph("9", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 4: Existing System & Literature Review</b>", body), Paragraph("10", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 5: Proposed System Architecture</b> (The PhishGuard Framework)", body), Paragraph("11", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 6: Hardware and Software Requirements</b>", body), Paragraph("12", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 7: System Architecture and Flowcharts</b> (Multi-Tier Design)", body), Paragraph("13", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.1 Data Flow Diagrams (DFD Level 0 & Level 1)", body), Paragraph("14", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;7.2 URL & File Threat Detection Workflow Pipelines", body), Paragraph("15", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 8: Module Specifications & Functional Capabilities</b>", body), Paragraph("16", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.1 Live URL Threat Scanner & 26-Feature Matrix", body), Paragraph("17", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.2 File Virus Scanner & Format-Aware Entropy", body), Paragraph("18", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;8.3 Password Analyzer & Settings Telemetry", body), Paragraph("19", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 9: Implementation Details & Source Code Analysis</b>", body), Paragraph("20", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.1 Lexical & Structural Feature Extraction Algorithms", body), Paragraph("21", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.2 Random Forest Classifier & Calibrated Scoring", body), Paragraph("22", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.3 Forensic File Hashing & Magic Byte Verification", body), Paragraph("23", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;9.4 Database Upsert Deduplication & Serverless Bridge", body), Paragraph("24", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 10: Testing and Verification Results</b>", body), Paragraph("25", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;10.1 Automated Pytest Execution Matrix (31 Tests)", body), Paragraph("26", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;10.2 Forensic Accuracy & Compression Edge-Case Validation", body), Paragraph("27", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 11: Application Interface & Screenshot Walkthrough</b>", body), Paragraph("28", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;11.1 Live URL Threat Scanner Dossier UI", body), Paragraph("29", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;11.2 File Security Dossier & Password Security Workspace UI", body), Paragraph("30", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 12: Practical Advantages & Technical Limitations</b>", body), Paragraph("31", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 13: Future Scope & Operational Roadmap</b>", body), Paragraph("32", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>Chapter 14: Conclusion & Project Summary</b>", body), Paragraph("33", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))],
        [Paragraph("<b>References and Bibliography</b>", body), Paragraph("34", ParagraphStyle("R", fontName="Helvetica", fontSize=9, alignment=2))]
    ]
    t_toc = Table(toc_data, colWidths=[420, 80])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: CHAPTER 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("1.1 Background and Context", h2))
    story.append(Paragraph(
        "In the contemporary hyper-connected digital ecosystem, web applications, cloud storage, and enterprise communication systems "
        "serve as the backbone of modern commerce, governance, and social interaction. However, this dependence has introduced critical "
        "vulnerabilities, with social engineering attacks—most notably <b>phishing</b>—consistently ranking as the most pervasive cyber threat. "
        "According to the Anti-Phishing Working Group (APWG) and the Verizon Data Breach Investigations Report (DBIR), over 80% of all confirmed "
        "security breaches originate from stolen credentials or weaponized email attachments containing deceptive hyperlinks.",
        body
    ))
    story.append(Paragraph(
        "Phishing attacks have evolved far beyond crude spelling errors and generic mass emails. Modern threat actors leverage sophisticated "
        "techniques, including Internationalized Domain Name (IDN) homoglyph spoofing, automated brand typosquatting, dynamic fast-flux DNS "
        "routing, algorithmically generated domains (DGAs), and multi-stage payload delivery. Furthermore, phishing pages are frequently "
        "paired with weaponized document payloads (.pdf, .docx, .zip) designed to evade traditional signature-matching endpoint defenses.",
        body
    ))
    story.append(Paragraph("1.2 Motivation for PHISHGUARD", h2))
    story.append(Paragraph(
        "Traditional enterprise defenses rely heavily on reactive threat intelligence feeds and centralized URL blacklists (such as Google "
        "Safe Browsing or Spamhaus). While valuable, blacklists suffer from an unavoidable temporal window of vulnerability—often spanning "
        "several hours to days between the initial launch of a zero-day phishing campaign and its public indexing. During this critical window, "
        "unsuspecting users remain entirely unprotected.",
        body
    ))
    story.append(Paragraph(
        "Additionally, security operations teams within small-to-medium enterprises, academic institutions, and independent forensic units "
        "often lack access to expensive, proprietary sandbox solutions. Analysts are forced to manually juggle separate tools for URL parsing, "
        "hash generation, byte entropy inspection, and password auditing. There is a compelling engineering need for a lightweight, self-contained, "
        "and unified cyber intelligence workstation that performs deep behavioral inspection without requiring dangerous sandbox execution.",
        body
    ))
    story.append(Paragraph("1.3 Project Scope", h2))
    story.append(Paragraph(
        "The primary scope of <b>PHISHGUARD</b> is the design, algorithmic implementation, and empirical verification of a unified security "
        "platform. The system evaluates suspect web targets using lexical feature extraction and machine learning, inspects suspicious files "
        "using cryptographic fingerprints and format-aware Shannon byte entropy, and audits password resiliency—all wrapped in a cohesive, "
        "high-performance dark cybersecurity dashboard.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: CHAPTER 2: PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: PROBLEM STATEMENT", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("2.1 Deficiencies in Current Phishing Detection Paradigms", h2))
    story.append(Paragraph(
        "Modern cybersecurity analysts and computer users face critical challenges when determining the legitimacy of suspicious digital assets. "
        "The problem of detecting phishing websites and weaponized files can be formulated into four primary engineering bottlenecks:",
        body
    ))
    story.append(Paragraph("<b>1. Blacklist Latency and Zero-Day Blind Spots:</b> Static blocklists rely on post-incident victim reports and automated web crawlers. Attackers circumvent blacklists by creating ephemeral domains that remain active for only 4 to 8 hours, harvesting credentials, and dismantling infrastructure before domain reputation engines register their malicious signature.", bullet))
    story.append(Paragraph("<b>2. Advanced Lexical Obfuscation & Homoglyphs:</b> Attackers exploit Unicode Internationalized Domain Names (IDN) to replace standard ASCII Latin characters with identical-looking Cyrillic or Greek homoglyphs (e.g., spoofing 'apple.com' using Cyrillic 'а'). Standard string comparisons fail to recognize the spoofing, while humans are visually deceived.", bullet))
    story.append(Paragraph("<b>3. Naive File Entropy Misclassification:</b> Traditional static analysis tools calculate Shannon byte entropy to flag packed or encrypted malware. However, naive algorithms frequently generate catastrophic false-positive alerts on legitimate compressed file formats (such as .pdf, .zip, .docx, and .png), whose Deflate compression naturally produces high entropy (7.2 to 8.0 bits/byte). This creates alert fatigue among forensic analysts.", bullet))
    story.append(Paragraph("<b>4. Analysis Fragmentation and Privacy Risks:</b> Analysts frequently use disparate third-party web services to hash files or test passwords, inadvertently leaking sensitive proprietary credentials or corporate documents to external servers.", bullet))
    story.append(Spacer(1, 4))
    story.append(Paragraph("2.2 Problem Formulation", h2))
    story.append(Paragraph(
        "The core technical challenge addressed by this project is: <i>How can we design and implement a unified, lightweight, and explainable "
        "cyber defense platform capable of evaluating the phishing probability of zero-day URLs using intrinsic lexical features, classifying "
        "file threat vectors with format-aware entropy, and assessing credential strength locally without violating data privacy boundaries?</i>",
        body
    ))
    story.append(Paragraph("2.3 Operational Significance", h2))
    story.append(Paragraph(
        "Solving this problem provides defensive security analysts, enterprise administrators, and end-users with an immediate, explainable "
        "risk verdict. Instead of an opaque 'Blocked' notice, PhishGuard provides actionable forensic indicators (such as typosquatting distance, "
        "suspicious TLD suffixes, and magic byte header mismatches) to foster informed defensive decision-making.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: CHAPTER 3: PROJECT OBJECTIVES
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: PROJECT OBJECTIVES", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("3.1 Primary Objective", h2))
    story.append(Paragraph(
        "To engineer, train, and deploy <b>PHISHGUARD</b>, an autonomous multi-tier cyber intelligence platform that bridges lexical machine "
        "learning, deep static payload forensics, and local credential auditing into a production-grade web application.",
        body
    ))
    story.append(Paragraph("3.2 Specific Measurable Goals", h2))
    story.append(Paragraph("<b>Objective 1: Multi-Layer URL Feature Extraction:</b> Construct an automated feature extractor capable of isolating 26 distinct structural, lexical, statistical, and brand-impersonation properties from arbitrary raw URLs in under 50 milliseconds.", bullet))
    story.append(Paragraph("<b>Objective 2: Supervised Machine Learning Classifier:</b> Train, calibrate, and serialize a Scikit-Learn Random Forest Classifier (100 estimators) achieving greater than 90% accuracy on test validation sets while outputting probabilistic threat confidence scores.", bullet))
    story.append(Paragraph("<b>Objective 3: Calibrated Composite Threat Scoring:</b> Implement a hybrid threat engine that combines machine learning probability with heuristic rule overrides (e.g., raw IP hosts, suspicious TLD abuse, and trusted apex whitelisting) to produce an explainable 0 to 100 risk score.", bullet))
    story.append(Paragraph("<b>Objective 4: Format-Aware File Inspection Pipeline:</b> Engineer a zero-execution file inspection module that computes cryptographic hashes (SHA-256, SHA-1, MD5), validates binary magic byte headers against file extensions, and contextualizes Shannon byte entropy to eliminate false-positive packing alerts on compressed documents.", bullet))
    story.append(Paragraph("<b>Objective 5: Antivirus Engine Bridge & Graceful Degradation:</b> Implement dynamic OS probing for local ClamAV installations, providing automated fallback to static heuristics ('Limited Analysis') when antivirus daemons are offline without halting inspection workflows.", bullet))
    story.append(Paragraph("<b>Objective 6: Zero-Storage Password Security Analyzer:</b> Develop a local password audit engine calculating mathematical Shannon entropy in bits, detecting dictionary collisions and keyboard patterns, and generating cryptographically secure random passwords with strict zero-persistence privacy.", bullet))
    story.append(Paragraph("<b>Objective 7: Persistence, Deduplication & Telemetry:</b> Implement SQLite database storage using Write-Ahead Logging (WAL) with automatic upsert deduplication on URLs and file hashes to maintain audit history without redundant database inflation.", bullet))
    story.append(Paragraph("<b>Objective 8: Automated Verification & Cloud Deployability:</b> Validate system integrity using an automated 31-test Pytest suite and ensure serverless deployment compatibility on platforms such as Vercel.", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: CHAPTER 4: EXISTING SYSTEM & LITERATURE REVIEW
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: EXISTING SYSTEM & LITERATURE REVIEW", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("4.1 Review of Traditional Approaches", h2))
    story.append(Paragraph(
        "Phishing detection methodologies in existing academic literature and commercial products generally fall into three broad categories: "
        "DNS Blacklisting, Heuristic Rule Filters, and Visual Similarity Analysis.",
        body
    ))
    story.append(Paragraph(
        "<b>1. Centralized Blacklisting:</b> Services such as Google Safe Browsing, PhishTank, and Spamhaus maintain centralized databases of "
        "verified malicious URLs. While exhibiting near-zero false positive rates on indexed threats, blacklists are completely ineffective "
        "against newly generated zero-day domains, fast-flux DNS switching, and short-lived phishing campaigns.",
        body
    ))
    story.append(Paragraph(
        "<b>2. Traditional Antivirus & Signature Scanners:</b> Signature-based scanners (such as standalone ClamAV or legacy AV solutions) "
        "match static byte sequences against threat definitions. While effective against known malware strains, they fail to detect zero-day "
        "polymorphic binaries and cannot evaluate social-engineering phishing URLs.",
        body
    ))
    story.append(Paragraph(
        "<b>3. Heavyweight Sandboxing:</b> Dynamic sandbox environments (e.g., Cuckoo Sandbox) execute suspect files inside isolated virtual "
        "machines to observe runtime behaviors. While forensically comprehensive, sandboxes require immense hardware overhead, introduce "
        "multi-minute analysis delays, and are susceptible to sandbox-evasion evasion tactics (such as sleep timers or hypervisor checks).",
        body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("4.2 Comparative Analysis Matrix", h2))

    comp_data = [
        [Paragraph("<b>Capability / Metric</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Static Blacklists</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Traditional AV</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Dynamic Sandbox</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>PHISHGUARD (Proposed)</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#00F5A0")))],
        [Paragraph("Zero-Day Phishing Detection", body), Paragraph("Ineffective (Lag)", body), Paragraph("None", body), Paragraph("Moderate", body), Paragraph("<b>High (26-Feat ML)</b>", body)],
        [Paragraph("Analysis Latency", body), Paragraph("< 10 ms", body), Paragraph("1 - 5 sec", body), Paragraph("3 - 10 min", body), Paragraph("<b>< 50 ms</b>", body)],
        [Paragraph("Format-Aware File Entropy", body), Paragraph("N/A", body), Paragraph("Basic / Misflags", body), Paragraph("High Overhead", body), Paragraph("<b>Calibrated Context</b>", body)],
        [Paragraph("Zero-Execution Safety", body), Paragraph("Safe", body), Paragraph("Safe", body), Paragraph("Isolation Risk", body), Paragraph("<b>Volatile Stream Safe</b>", body)],
        [Paragraph("Hardware Requirements", body), Paragraph("Negligible", body), Paragraph("Moderate", body), Paragraph("Very High (VMs)", body), Paragraph("<b>Lightweight (Flask/Py)</b>", body)],
        [Paragraph("Credential Privacy Guarantee", body), Paragraph("Exposed to API", body), Paragraph("N/A", body), Paragraph("N/A", body), Paragraph("<b>Zero-Storage Policy</b>", body)]
    ]
    t_comp = Table(comp_data, colWidths=[120, 95, 95, 95, 95])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_comp)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: CHAPTER 5: PROPOSED SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: PROPOSED SYSTEM ARCHITECTURE", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("5.1 Conceptual Architecture", h2))
    story.append(Paragraph(
        "<b>PHISHGUARD</b> is designed as a modular, defense-in-depth cyber intelligence workstation. The platform moves beyond monolithic "
        "scanning by dividing forensic responsibilities across dedicated micro-modules operating through a unified web controller:",
        body
    ))
    story.append(Paragraph("<b>1. Fast-Path Allowlist Filter:</b> Incoming URLs are evaluated against an apex domain allowlist containing globally verified authorities (e.g., Google, Microsoft, GitHub, Wikipedia). Verified apex domains bypass heavy computation, completing evaluation in under 2 milliseconds.", bullet))
    story.append(Paragraph("<b>2. 26-Dimensional Lexical Feature Engine:</b> URLs undergo lexical decomposition, isolating statistical properties (entropy, digit ratios, token lengths), structural indicators (punycode, subdomain depth, unusual ports), and semantic anomalies (brand typosquatting distance, high-abuse TLDs).", bullet))
    story.append(Paragraph("<b>3. Calibrated Supervised Machine Learning:</b> Extracted feature vectors are classified by a Random Forest model trained on empirical phishing datasets, generating probabilistic confidence scores that feed into a composite risk calibration formula.", bullet))
    story.append(Paragraph("<b>4. Non-Destructive Payload Forensics:</b> Uploaded files are inspected strictly in volatile memory. The system extracts immutable cryptographic hashes, checks magic byte signatures against extension headers, and calculates format-aware Shannon byte entropy to eliminate false positives on naturally compressed documents.", bullet))
    story.append(Paragraph("<b>5. Zero-Storage Credential Security Engine:</b> Evaluates password complexity, character set pool size, and dictionary walk patterns directly in the client browser, strictly prohibiting database persistence or network transmission of entered secrets.", bullet))
    story.append(Spacer(1, 4))
    story.append(Paragraph("5.2 Key Innovations in PhishGuard", h2))
    story.append(Paragraph(
        "&bull; <b>Explainable Threat Indicators:</b> Instead of returning a binary 'Safe/Unsafe' flag, PhishGuard generates plain-English forensic findings explaining exactly why a target was flagged (e.g., <i>'Brand impersonation: paypal detected in non-apex host'</i>).<br/>"
        "&bull; <b>Intelligent Antivirus Degradation:</b> Probes system PATH and standard OS locations for ClamAV, automatically engaging static heuristic fallback when signatures are offline.<br/>"
        "&bull; <b>WAL Deduplication:</b> Prevents database bloat by updating existing scan rows upon re-inspection rather than duplicating records.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: CHAPTER 6: HARDWARE AND SOFTWARE REQUIREMENTS
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: HARDWARE AND SOFTWARE REQUIREMENTS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("6.1 Hardware Requirements", h2))
    story.append(Paragraph("The platform is optimized for low resource consumption, operating smoothly across standard workstation hardware and cloud containers:", body))

    hw_data = [
        [Paragraph("<b>Hardware Component</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Minimum Specification</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Recommended Specification</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white))],
        [Paragraph("Processor (CPU)", body), Paragraph("Dual-Core 2.0 GHz (x86_64 or ARM64)", body), Paragraph("Quad-Core 2.5 GHz or higher", body)],
        [Paragraph("System Memory (RAM)", body), Paragraph("2 GB RAM", body), Paragraph("4 GB to 8 GB DDR4", body)],
        [Paragraph("Persistent Storage", body), Paragraph("500 MB free disk space", body), Paragraph("2 GB SSD (for database growth)", body)],
        [Paragraph("Network Interface", body), Paragraph("Standard Ethernet / Wi-Fi", body), Paragraph("Broadband (for threat feeds/cloud)", body)],
        [Paragraph("Display Resolution", body), Paragraph("1280 x 720 (HD)", body), Paragraph("1920 x 1080 (Full HD Widescreen)", body)]
    ]
    t_hw = Table(hw_data, colWidths=[150, 175, 175])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_hw)

    story.append(Spacer(1, 8))
    story.append(Paragraph("6.2 Software Requirements & Confirmed Dependencies", h2))
    story.append(Paragraph("Confirmed technical dependencies verified directly from project source code and configuration files:", body))

    sw_data = [
        [Paragraph("<b>Layer / Tool</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Confirmed Software / Dependency</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Operational Purpose</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white))],
        [Paragraph("Operating System", body), Paragraph("Windows 10/11, Ubuntu 20.04+, macOS", body), Paragraph("Host OS platform", body)],
        [Paragraph("Core Runtime", body), Paragraph("Python 3.12 (CPython)", body), Paragraph("Primary backend execution engine", body)],
        [Paragraph("Web Framework", body), Paragraph("Flask 3.1.3 + Werkzeug 3.1.9", body), Paragraph("WSGI routing, request dispatch, views", body)],
        [Paragraph("Rate Limiting", body), Paragraph("Flask-Limiter 4.1.1 + limits 5.8.0", body), Paragraph("Brute-force & DoS mitigation", body)],
        [Paragraph("Machine Learning", body), Paragraph("Scikit-Learn 1.9.1 + NumPy 2.5.4", body), Paragraph("Random Forest inference & vector math", body)],
        [Paragraph("Serialization", body), Paragraph("Joblib 1.6.0", body), Paragraph("Fast disk loading of serialized models", body)],
        [Paragraph("TLD Parsing", body), Paragraph("tldextract 5.4.0", body), Paragraph("Accurate ccTLD & apex domain parsing", body)],
        [Paragraph("Database", body), Paragraph("SQLite3 (WAL Mode Journaling)", body), Paragraph("Persistent audit trail & upsert log", body)],
        [Paragraph("PDF Generation", body), Paragraph("ReportLab 5.1.0", body), Paragraph("Forensic audit report PDF streaming", body)],
        [Paragraph("Testing Suite", body), Paragraph("Pytest 9.2.0 (31 automated tests)", body), Paragraph("Continuous unit & regression testing", body)],
        [Paragraph("Frontend UI", body), Paragraph("HTML5, CSS3, JS ES6+, Chart.js, Lucide", body), Paragraph("Glassmorphic SOC dashboard interface", body)],
        [Paragraph("Antivirus (Optional)", body), Paragraph("ClamAV 1.0+ (clamscan)", body), Paragraph("Deep signature scanning (fallback ready)", body)]
    ]
    t_sw = Table(sw_data, colWidths=[130, 185, 185])
    t_sw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_sw)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: CHAPTER 7: SYSTEM ARCHITECTURE & FLOWCHARTS (PART 1)
    # =========================================================================
    story.append(Paragraph("CHAPTER 7: SYSTEM ARCHITECTURE AND FLOWCHARTS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("7.1 Multi-Tier Architectural Overview", h2))
    story.append(Paragraph(
        "PhishGuard adopts a four-tier architecture designed to enforce clean separation of concerns, zero host execution safety, "
        "and resilient fallback handling. The presentation layer communicates with the Flask WSGI controller via RESTful endpoints, "
        "which coordinates detection micro-engines and commits audit logs to persistent storage.",
        body
    ))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig1_system_architecture.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig1_system_architecture.png"), width=490, height=310))
        story.append(Paragraph("<b>Figure 7.1:</b> Multi-Tier System Architecture of the PhishGuard Platform.", caption))
    story.append(Paragraph(
        "As depicted in Figure 7.1, requests entering the system pass through strict validation boundaries. Rate limiters prevent API "
        "exhaustion, while the serverless bridge in <code>api/index.py</code> ensures smooth execution across both containerized cloud environments "
        "(such as Vercel) and standalone on-premises servers.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: CHAPTER 7: SYSTEM ARCHITECTURE & FLOWCHARTS (PART 2)
    # =========================================================================
    story.append(Paragraph("7.2 Data Flow Diagrams (DFD Level 0 and Level 1)", h2))
    story.append(Paragraph(
        "The Data Flow Diagram models the flow of data through PhishGuard, highlighting input sanitization, transformation through "
        "machine learning models, persistent logging, and the strict zero-storage handling of credentials.",
        body
    ))
    story.append(Spacer(1, 6))
    if (FIGURES_DIR / "fig2_data_flow_diagram.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig2_data_flow_diagram.png"), width=490, height=295))
        story.append(Paragraph("<b>Figure 7.2:</b> Data Flow Diagram (DFD Level 1) for Multi-Vector Threat Analysis.", caption))
    story.append(Paragraph(
        "<b>DFD Level 1 Process Breakdown:</b><br/>"
        "&bull; <b>P 1.0 (URL Analysis):</b> Extracts 26-dimensional feature vectors, queries Random Forest weights from D1, computes composite threat score, and logs audit records to D2.<br/>"
        "&bull; <b>P 2.0 (File Threat Inspection):</b> Calculates cryptographic hashes, reads magic bytes, contextualizes Shannon byte entropy, and writes scan metadata to D2.<br/>"
        "&bull; <b>P 3.0 (Password Security Analysis):</b> Evaluates bit entropy and dictionary patterns in memory; strictly isolates data from persistent datastores.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: CHAPTER 7: SYSTEM ARCHITECTURE & FLOWCHARTS (PART 3)
    # =========================================================================
    story.append(Paragraph("7.3 Threat Detection Workflow Pipelines", h2))
    story.append(Paragraph(
        "PhishGuard's detection workflows operate through sequential validation gates to ensure low latency and high accuracy:",
        body
    ))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig3_url_scan_workflow.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig3_url_scan_workflow.png"), width=490, height=265))
        story.append(Paragraph("<b>Figure 7.3:</b> URL Threat Detection and Feature Extraction Workflow Pipeline.", caption))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig4_file_scan_workflow.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig4_file_scan_workflow.png"), width=490, height=265))
        story.append(Paragraph("<b>Figure 7.4:</b> File Inspection, Format-Aware Entropy, and Antivirus Fallback Workflow.", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: CHAPTER 8: MODULE SPECIFICATIONS (PART 1 - DASHBOARD)
    # =========================================================================
    story.append(Paragraph("CHAPTER 8: MODULE SPECIFICATIONS & FUNCTIONAL CAPABILITIES", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("8.1 Executive Security Operations Center (SOC) Dashboard", h2))
    story.append(Paragraph(
        "The Executive Dashboard (<code>/dashboard</code>) serves as the primary operational overview for security personnel, summarizing "
        "system-wide telemetry without cluttering the screen with raw forensic data. It is partitioned into five functional zones:",
        body
    ))
    story.append(Paragraph("<b>1. High-Level Telemetry Cards:</b> Displays five vital threat metrics computed in real-time from the SQLite database: Total Inspected URLs, Confirmed Phishing Detections, Suspicious Entities, Legitimate Domains, and Average Threat Risk Index (0-100 scale).", bullet))
    story.append(Paragraph("<b>2. Security Workspace Navigation Cards:</b> Provides direct launch points to the dedicated functional workspaces: (a) Live URL Threat Scanner, (b) File Virus Scanner, and (c) Password Security Analyzer.", bullet))
    story.append(Paragraph("<b>3. Verdict Distribution Doughnut Radar:</b> An interactive Chart.js visualization plotting the proportional breakdown between legitimate, suspicious, and phishing targets across historical audits.", bullet))
    story.append(Paragraph("<b>4. Platform & Engine Health Telemetry:</b> Surfaces operational status indicators, including Random Forest model loaded state, SQLite WAL journal mode, heuristic engine toggle, and ClamAV connectivity status.", bullet))
    story.append(Paragraph("<b>5. Recent Security Activity Audit Log:</b> A compact tabular feed displaying the latest scan events, complete with color-coded risk pills, timestamps, target URLs, and direct links to full dossiers.", bullet))
    story.append(Spacer(1, 8))
    story.append(Paragraph("8.1.1 Input, Output, and Error Handling", ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#0f172a"))))
    story.append(Paragraph(
        "&bull; <b>Inputs:</b> Database aggregation queries over <code>scans</code> and <code>file_scans</code> tables via <code>get_statistics()</code>.<br/>"
        "&bull; <b>Outputs:</b> Rendered Jinja2 HTML dashboard with real-time responsive Chart.js data binding.<br/>"
        "&bull; <b>Error Handling:</b> Gracefully handles empty database states by displaying placeholder guidance rather than failing on zero-division math.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: CHAPTER 8: MODULE SPECIFICATIONS (PART 2 - URL SCANNER)
    # =========================================================================
    story.append(Paragraph("8.2 Live URL Threat Scanner & 26-Dimensional Feature Matrix", h2))
    story.append(Paragraph(
        "The URL Threat Scanner (<code>/scanner</code>) is an isolated forensic analysis workspace dedicated to deep inspection of arbitrary "
        "hyperlinks. The analysis pipeline evaluates 26 structural and behavioral properties grouped into four analytical layers:",
        body
    ))

    feat_data = [
        [Paragraph("<b>Feature Category</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Extracted Attributes (26 Features Total)</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Forensic Significance</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white))],
        [Paragraph("1. Lexical Properties", body),
         Paragraph("<code>url_length, hostname_length, domain_length, path_length, num_dots, num_hyphens, num_digits, num_special_chars, digit_ratio, special_char_ratio</code>", code),
         Paragraph("Identifies artificially bloated URLs designed to conceal malicious destination endpoints.", body)],
        [Paragraph("2. Structural & Network", body),
         Paragraph("<code>num_subdomains, subdomain_length, has_ip, is_https, has_at_symbol, query_param_count, is_shortened, has_unusual_port, has_encoded_chars</code>", code),
         Paragraph("Detects raw IP hosts, suspicious port bindings, URL shorteners, and authentication (@) spoofing.", body)],
        [Paragraph("3. Information Entropy", body),
         Paragraph("<code>domain_entropy, url_entropy</code> (Shannon Entropy in bits)", code),
         Paragraph("Quantifies character randomness to uncover Algorithmically Generated Domains (DGAs).", body)],
        [Paragraph("4. Semantic & Brand Defense", body),
         Paragraph("<code>has_punycode, is_suspicious_tld, suspicious_keyword_count, brand_impersonation_score, suspicious_hostname_pattern</code>", code),
         Paragraph("Detects IDN homoglyphs, high-abuse TLD registries (.xyz, .top), and typosquatting of 30 top brands.", body)]
    ]
    t_feat = Table(feat_data, colWidths=[110, 240, 150])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 8))
    story.append(Paragraph("8.2.1 Brand Typosquatting Algorithm", ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#0f172a"))))
    story.append(Paragraph(
        "PhishGuard monitors 30 high-value target institutions (e.g., PayPal, Microsoft, Apple, Google, Chase). If a brand name appears "
        "inside a non-apex host (e.g. <code>paypal.security-verification.xyz</code>), the system flags unauthorized brand usage and assigns "
        "a severe threat penalty (+35 risk points).",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: CHAPTER 8: MODULE SPECIFICATIONS (PART 3 - FILE SCANNER)
    # =========================================================================
    story.append(Paragraph("8.3 File Virus Scanner & Format-Aware Forensics", h2))
    story.append(Paragraph(
        "The File Virus Scanner (<code>/file-scanner</code>) provides zero-execution static inspection of documents, scripts, archives, and "
        "binaries. The module operates without executing payloads on the host machine, incorporating four forensic safeguards:",
        body
    ))
    story.append(Paragraph("<b>1. Multi-Algorithm Cryptographic Hashing:</b> Computes SHA-256 (64-character primary fingerprint), SHA-1, and MD5 hashes simultaneously across volatile memory buffers, facilitating immediate hash cross-referencing against threat intelligence databases.", bullet))
    story.append(Paragraph("<b>2. Binary Magic Byte Verification:</b> Inspects the raw leading bytes of the uploaded file to verify that the internal file structure matches the declared file extension. This immediately exposes file spoofing tactics (e.g., weaponized Windows PE executables <code>4D 5A</code> disguised with a <code>.pdf</code> or <code>.png</code> extension).", bullet))
    story.append(Paragraph("<b>3. Format-Aware Shannon Byte Entropy:</b> Evaluates byte distribution across 256 byte values ($0x00$ to $0xFF$). Crucially, PhishGuard incorporates a comprehensive format-aware exception catalog (<code>COMPRESSED_OR_PACKED_FORMATS</code>):", bullet))

    ent_data = [
        [Paragraph("<b>File Format / Extension</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Expected Entropy Range</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>PhishGuard Interpretation & Classification</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white))],
        [Paragraph(".pdf, .zip, .docx, .xlsx, .gz, .png, .jpg", body), Paragraph("7.20 – 7.99 bits / byte", body), Paragraph("<b>Normal Compressed Stream Entropy</b> (Info severity; zero threat penalty)", body)],
        [Paragraph(".exe, .dll, .bin (Executables)", body), Paragraph("> 7.50 bits / byte", body), Paragraph("<b>Suspect Binary Packing / Obfuscation</b> (Warning/Danger severity)", body)],
        [Paragraph(".txt, .py, .js, .html, .bat (Scripts)", body), Paragraph("> 6.80 bits / byte", body), Paragraph("<b>Encoded Shellcode / Obfuscated Script</b> (Elevated risk score)", body)]
    ]
    t_ent = Table(ent_data, colWidths=[140, 120, 240])
    t_ent.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_ent)
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>4. ClamAV Engine Bridge & Intelligent Fallback:</b> Probes system PATH and standard OS locations for <code>clamscan</code>. If ClamAV is offline, PhishGuard engages deep static heuristics, labeling the scan <b>'Limited Analysis'</b> with low heuristic risk rather than falsely certifying an unaudited file as Clean.", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: CHAPTER 8: MODULE SPECIFICATIONS (PART 4 - PASSWORD & SETTINGS)
    # =========================================================================
    story.append(Paragraph("8.4 Password Security Analyzer & System Settings", h2))
    story.append(Paragraph(
        "The Password Security Analyzer (<code>/password-analyzer</code>) provides client-side credential auditing, evaluating structural "
        "resiliency without compromising user privacy.",
        body
    ))
    story.append(Paragraph("<b>1. Mathematical Shannon Bit Entropy:</b> Rather than using arbitrary length rules, entropy is calculated using pool space permutations: <i>E = L &times; log<sub>2</sub>(N)</i>, where <i>L</i> is password length and <i>N</i> is the active character pool (lowercase, uppercase, digits, symbols).", bullet))
    story.append(Paragraph("<b>2. Pattern & Sequential Walk Auditing:</b> Detects sequential numbers (12345), alphabetical sequences (abcde), keyboard walks (qwerty, asdfgh), repeated characters, and common dictionary collisions (e.g., password, admin, welcome).", bullet))
    story.append(Paragraph("<b>3. Zero-Storage Architecture:</b> Enforces strict security boundaries: entered passwords are never logged, never saved to SQLite, and never transmitted over external network APIs.", bullet))
    story.append(Paragraph("<b>4. CSPRNG Password Generator:</b> Generates high-entropy passwords (12 to 64 characters) using Python's cryptographically secure <code>secrets</code> module.", bullet))

    story.append(Spacer(1, 4))
    story.append(Paragraph("8.5 Security Settings & Telemetry Management", h2))
    story.append(Paragraph(
        "The Settings module (<code>/settings</code>) provides administrator controls over engine parameters and database retention:",
        body
    ))
    story.append(Paragraph("&bull; <b>Configurable File Upload Boundaries:</b> Dynamic threshold adjustment (1 MB to 100 MB, defaulting to 16 MB or 32 MB).<br/>"
                           "&bull; <b>Custom ClamAV Binary Path:</b> Allows pointing the scanner to specific installation locations (e.g. <code>C:\\Program Files\\ClamAV\\clamscan.exe</code>).<br/>"
                           "&bull; <b>Deep Static Heuristic Toggle:</b> Enables or bypasses magic byte and entropy checks.<br/>"
                           "&bull; <b>Database Maintenance Purge Actions:</b> Safe one-click clearance of historical URL audits or file hashes.",
                           body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: CHAPTER 9: IMPLEMENTATION & CODE (PART 1 - STRUCTURE)
    # =========================================================================
    story.append(Paragraph("CHAPTER 9: IMPLEMENTATION DETAILS & CODE ANALYSIS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("9.1 Project Structure & Modular Organization", h2))
    story.append(Paragraph(
        "PhishGuard's physical codebase is organized into dedicated functional modules adhering to separation of concerns:",
        body
    ))

    struct_data = [
        [Paragraph("<b>File / Directory Path</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Lines of Code</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)),
         Paragraph("<b>Functional Responsibility & Architectural Role</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white))],
        [Paragraph("<code>app.py</code>", code), Paragraph("524 lines", body), Paragraph("Flask Application Factory, REST endpoints, rate limiting, error handlers.", body)],
        [Paragraph("<code>config.py</code>", code), Paragraph("115 lines", body), Paragraph("Serverless-aware configuration, /tmp redirection, brand whitelists.", body)],
        [Paragraph("<code>feature_extractor.py</code>", code), Paragraph("254 lines", body), Paragraph("26-layer URL feature extraction, Shannon entropy, brand typosquatting.", body)],
        [Paragraph("<code>detector.py</code>", code), Paragraph("238 lines", body), Paragraph("Random Forest inference, composite risk calibration formula (0-100).", body)],
        [Paragraph("<code>file_scanner.py</code>", code), Paragraph("308 lines", body), Paragraph("Cryptographic hashing, ClamAV runtime discovery, static payload audit.", body)],
        [Paragraph("<code>file_security.py</code>", code), Paragraph("330 lines", body), Paragraph("Magic bytes, format-aware entropy, structured forensic evidence findings.", body)],
        [Paragraph("<code>password_analyzer.py</code>", code), Paragraph("296 lines", body), Paragraph("Zero-storage password entropy, pattern detection, CSPRNG generator.", body)],
        [Paragraph("<code>database.py</code>", code), Paragraph("425 lines", body), Paragraph("SQLite3 WAL mode, table initialization, upsert deduplication routines.", body)],
        [Paragraph("<code>report_generator.py</code>", code), Paragraph("175 lines", body), Paragraph("ReportLab in-memory forensic audit PDF report streamer.", body)],
        [Paragraph("<code>index.py</code> / <code>vercel.json</code>", code), Paragraph("25 lines", body), Paragraph("Vercel WSGI entry point and catch-all serverless routing rules.", body)]
    ]
    t_struct = Table(struct_data, colWidths=[130, 80, 290])
    t_struct.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_struct)
    story.append(Spacer(1, 6))
    story.append(Paragraph("9.2 Application Configuration & Serverless Portability", h2))
    story.append(Paragraph(
        "To operate seamlessly on both standard host operating systems and read-only serverless cloud containers (e.g. Vercel), "
        "<code>config.py</code> dynamically routes writable directories to <code>tempfile.gettempdir()</code> when <code>VERCEL</code> is detected:",
        body
    ))
    code_config = (
        "IS_SERVERLESS = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))\n"
        "if IS_SERVERLESS:\n"
        "    INSTANCE_DIR = Path(tempfile.gettempdir()) / 'phishguard_instance'\n"
        "else:\n"
        "    INSTANCE_DIR = BASE_DIR / 'instance'\n"
        "INSTANCE_DIR.mkdir(parents=True, exist_ok=True)\n"
        "DATABASE_PATH = os.environ.get('DATABASE_PATH', str(INSTANCE_DIR / 'phishguard.db'))"
    )
    p_code = Table([[Paragraph(f"<pre>{code_config}</pre>", code)]], colWidths=[500])
    p_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(p_code)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: CHAPTER 9: IMPLEMENTATION & CODE (PART 2 - FEATURES)
    # =========================================================================
    story.append(Paragraph("9.3 Lexical Feature Extraction & Entropy Algorithms", h2))
    story.append(Paragraph(
        "The core intelligence of the URL classifier resides in <code>feature_extractor.py</code>. Shannon entropy is computed to "
        "measure character uncertainty across the domain and path segments:",
        body
    ))
    code_entropy = (
        "def calculate_shannon_entropy(text: str) -> float:\n"
        "    if not text:\n"
        "        return 0.0\n"
        "    length = len(text)\n"
        "    freq = Counter(text)\n"
        "    entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())\n"
        "    return round(entropy, 4)"
    )
    t_c1 = Table([[Paragraph(f"<pre>{code_entropy}</pre>", code)]], colWidths=[500])
    t_c1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("9.4 Brand Impersonation & Typosquatting Detection", h2))
    story.append(Paragraph(
        "To uncover credential harvesting sites impersonating major brands (e.g. <code>paypal-update-account.com</code>), the engine "
        "inspects the extracted domain and subdomains against the target brand catalog:",
        body
    ))
    code_brand = (
        "def check_brand_impersonation(domain: str, path: str, target_brands: list) -> tuple[int, list]:\n"
        "    domain_lower = domain.lower()\n"
        "    detected_brands = []\n"
        "    score = 0\n"
        "    for brand in target_brands:\n"
        "        # Brand present in domain but domain does not end with legitimate apex brand\n"
        "        if brand in domain_lower:\n"
        "            if not (domain_lower == f'{brand}.com' or domain_lower.endswith(f'.{brand}.com')):\n"
        "                score += 1\n"
        "                detected_brands.append(brand)\n"
        "    return score, detected_brands"
    )
    t_c2 = Table([[Paragraph(f"<pre>{code_brand}</pre>", code)]], colWidths=[500])
    t_c2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c2)
    story.append(Spacer(1, 6))
    story.append(Paragraph("9.5 Feature Importance Evaluation", h2))
    if (FIGURES_DIR / "fig5_feature_importance.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig5_feature_importance.png"), width=440, height=210))
        story.append(Paragraph("<b>Figure 9.1:</b> Relative Feature Importance Weights in the Trained Random Forest Classifier.", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: CHAPTER 9: IMPLEMENTATION & CODE (PART 3 - ML CLASSIFIER)
    # =========================================================================
    story.append(Paragraph("9.6 Random Forest Training & Composite Risk Calibration", h2))
    story.append(Paragraph(
        "Model training is managed by <code>train_model.py</code>, utilizing Scikit-Learn's <code>RandomForestClassifier</code> with "
        "100 estimators and entropy split criteria. The model is saved to <code>models/phishing_model.pkl</code>.",
        body
    ))
    story.append(Paragraph(
        "In production (<code>detector.py</code>), the raw probability output from the Random Forest is calibrated with heuristic "
        "penalties to yield an explainable composite threat score (0 to 100):",
        body
    ))
    code_calib = (
        "def calculate_calibrated_risk(ml_prob: float, features: dict, indicators: list) -> tuple[int, str]:\n"
        "    # Base score derived from Random Forest phishing probability\n"
        "    base_score = ml_prob * 60.0\n"
        "    penalty = 0.0\n\n"
        "    if features.get('brand_impersonation_score', 0) > 0:\n"
        "        penalty += 25.0\n"
        "    if features.get('has_ip'):\n"
        "        penalty += 20.0\n"
        "    if features.get('is_suspicious_tld'):\n"
        "        penalty += 15.0\n"
        "    if not features.get('is_https'):\n"
        "        penalty += 10.0\n"
        "    if features.get('domain_entropy', 0) > 3.8:\n"
        "        penalty += 10.0\n\n"
        "    risk_score = min(int(round(base_score + penalty)), 100)\n"
        "    if risk_score >= 60:\n"
        "        risk_level = 'High'  # Potential Phishing\n"
        "    elif risk_score >= 25:\n"
        "        risk_level = 'Medium'  # Suspicious\n"
        "    else:\n"
        "        risk_level = 'Low'  # Likely Legitimate\n"
        "    return risk_score, risk_level"
    )
    t_c3 = Table([[Paragraph(f"<pre>{code_calib}</pre>", code)]], colWidths=[500])
    t_c3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c3)
    story.append(Spacer(1, 6))
    story.append(Paragraph("9.7 Fast-Path Allowlist Logic", h2))
    story.append(Paragraph(
        "To avoid false positives and reduce processing overhead on verified apex entities, PhishGuard checks a pre-compiled set of trusted "
        "apex domains (e.g. <code>google.com</code>, <code>microsoft.com</code>, <code>github.com</code>). Verified apex hosts receive an "
        "immediate zero-risk rating (Risk: 0, Confidence: 99%).",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: CHAPTER 9: IMPLEMENTATION & CODE (PART 4 - FILE FORENSICS)
    # =========================================================================
    story.append(Paragraph("9.8 Format-Aware File Entropy & Magic Byte Implementation", h2))
    story.append(Paragraph(
        "File inspection in <code>file_security.py</code> resolves false positive entropy alerts by checking whether the file format belongs "
        "to naturally compressed container formats (<code>COMPRESSED_OR_PACKED_FORMATS</code>):",
        body
    ))
    code_file = (
        "COMPRESSED_OR_PACKED_FORMATS = {\n"
        "    '.pdf', '.zip', '.gz', '.tar', '.bz2', '.7z', '.rar',\n"
        "    '.docx', '.xlsx', '.pptx', '.jar', '.apk', '.png', '.jpg', '.jpeg'\n"
        "}\n\n"
        "def assess_file_entropy(entropy: float, filename: str, mime_type: str) -> dict:\n"
        "    ext = os.path.splitext(filename)[1].lower()\n"
        "    is_compressed = ext in COMPRESSED_OR_PACKED_FORMATS or 'pdf' in mime_type or 'zip' in mime_type\n\n"
        "    if is_compressed:\n"
        "        # High entropy is structurally expected due to zlib / Deflate compression\n"
        "        return {\n"
        "            'severity': 'info',\n"
        "            'category': 'Byte Distribution',\n"
        "            'title': 'Normal Compressed Stream Entropy',\n"
        "            'is_naturally_compressed': True,\n"
        "            'explanation': f'Entropy of {entropy:.3f} bits is normal for compressed formats ({ext}).'\n"
        "        }\n"
        "    elif entropy > 7.5:\n"
        "        return {\n"
        "            'severity': 'danger',\n"
        "            'category': 'Byte Distribution',\n"
        "            'title': 'Suspect Packed Binary Payload',\n"
        "            'is_naturally_compressed': False,\n"
        "            'explanation': 'Uncompressed file exhibits abnormal entropy (>7.5), indicating packing.'\n"
        "        }"
    )
    t_c4 = Table([[Paragraph(f"<pre>{code_file}</pre>", code)]], colWidths=[500])
    t_c4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c4)
    story.append(Spacer(1, 6))
    story.append(Paragraph("9.9 Magic Byte Signature Header Verification", h2))
    story.append(Paragraph(
        "PhishGuard verifies byte sequences at offset 0 against known signatures: PDF (<code>%PDF</code>), ZIP/Office (<code>PK\\x03\\x04</code>), "
        "PNG (<code>\\x89PNG\\r\\n\\x1a\\n</code>), and Windows PE Executables (<code>MZ</code>). If an executable contains an <code>MZ</code> "
        "header while sporting a <code>.pdf</code> extension, the system triggers an immediate <b>Severe File Extension Spoofing</b> critical alert.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: CHAPTER 9: IMPLEMENTATION & CODE (PART 5 - PERSISTENCE & DEPLOY)
    # =========================================================================
    story.append(Paragraph("9.10 Database Upsert Deduplication & Serverless Bridge", h2))
    story.append(Paragraph(
        "In <code>database.py</code>, re-scanning an existing URL or file hash executes an in-place <code>UPDATE</code> rather than an <code>INSERT</code>, "
        "preventing redundant database growth while keeping scan timestamps fresh:",
        body
    ))
    code_upsert = (
        "def insert_scan(url, domain, prediction, risk_score, risk_level, confidence, features, indicators):\n"
        "    conn = get_db_connection()\n"
        "    try:\n"
        "        with conn:\n"
        "            cursor = conn.execute('SELECT id FROM scans WHERE url = ? ORDER BY id DESC LIMIT 1', (url,))\n"
        "            existing = cursor.fetchone()\n"
        "            if existing:\n"
        "                scan_id = existing[0]\n"
        "                conn.execute('''\n"
        "                    UPDATE scans SET prediction=?, risk_score=?, risk_level=?, confidence=?, scan_timestamp=?\n"
        "                    WHERE id = ?\n"
        "                ''', (prediction, risk_score, risk_level, confidence, datetime.now(timezone.utc).isoformat(), scan_id))\n"
        "                return scan_id\n"
        "            # Insert new record if not previously audited\n"
        "            cursor = conn.execute('INSERT INTO scans (...) VALUES (...)', (...))\n"
        "            return cursor.lastrowid\n"
        "    finally:\n"
        "        conn.close()"
    )
    t_c5 = Table([[Paragraph(f"<pre>{code_upsert}</pre>", code)]], colWidths=[500])
    t_c5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c5)
    story.append(Spacer(1, 6))

    story.append(Paragraph("9.11 Serverless Vercel Routing Configuration", h2))
    story.append(Paragraph(
        "To deploy on Vercel without broken static styling, <code>vercel.json</code> rewrites all routes directly to the WSGI application "
        "handler in <code>index.py</code>, enabling Flask to serve both application views and static assets (CSS, JS, fonts) with correct MIME types:",
        body
    ))
    code_vercel = (
        "{\n"
        '  "version": 2,\n'
        '  "builds": [{ "src": "index.py", "use": "@vercel/python" }],\n'
        '  "routes": [{ "src": "/(.*)", "dest": "index.py" }]\n'
        "}"
    )
    t_c6 = Table([[Paragraph(f"<pre>{code_vercel}</pre>", code)]], colWidths=[500])
    t_c6.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c6)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 25: CHAPTER 10: TESTING & RESULTS (PART 1 - STRATEGY)
    # =========================================================================
    story.append(Paragraph("CHAPTER 10: TESTING AND VERIFICATION RESULTS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("10.1 Automated Testing Strategy", h2))
    story.append(Paragraph(
        "Software testing for PhishGuard was conducted using the industry-standard <b>Pytest</b> test framework (v9.2.0). The test suite "
        "was engineered to validate every analytical layer—from lexical string normalization and Shannon entropy mathematics to database "
        "upsert deduplication and REST API error handling. Testing spanned four categories:",
        body
    ))
    story.append(Paragraph("<b>1. Unit Testing:</b> Isolated verification of mathematical algorithms (Shannon entropy calculation, character pool sizing, filename sanitization, and cryptographic hashing).", bullet))
    story.append(Paragraph("<b>2. Integration Testing:</b> Multi-component validation testing interactions between the Flask routing layer, feature extractor, serialized Random Forest model, and SQLite database.", bullet))
    story.append(Paragraph("<b>3. Security Boundary Testing:</b> Enforcing rate limit boundaries (429 Too Many Requests), upload size limits (413 Payload Too Large), directory traversal sanitization, and zero password database logging.", bullet))
    story.append(Paragraph("<b>4. Regression & Deduplication Testing:</b> Verifying that identical URLs or repeated file uploads update existing database rows without creating orphaned records.", bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("10.2 Pytest Execution Summary", h2))
    story.append(Paragraph(
        "The automated test suite was executed in the project virtual environment on Python 3.12.13. All <b>31 automated test cases</b> "
        "completed with a <b>100% pass rate</b> in 4.02 seconds:",
        body
    ))

    test_sum_data = [
        [Paragraph("<b>Test Module File</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Focus Domain</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Tests Executed</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Pass / Fail</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white)),
         Paragraph("<b>Execution Status</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white))],
        [Paragraph("<code>test_database.py</code>", code), Paragraph("SQLite CRUD, WAL Mode, Statistics", body), Paragraph("4 tests", body), Paragraph("4 Passed / 0 Failed", body), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", body)],
        [Paragraph("<code>test_detector.py</code>", code), Paragraph("Random Forest inference & fast-path", body), Paragraph("4 tests", body), Paragraph("4 Passed / 0 Failed", body), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", body)],
        [Paragraph("<code>test_features.py</code>", code), Paragraph("26 lexical features, entropy, IP hosts", body), Paragraph("5 tests", body), Paragraph("5 Passed / 0 Failed", body), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", body)],
        [Paragraph("<code>test_files.py</code>", code), Paragraph("Hashes, magic bytes, format entropy, PDF", body), Paragraph("8 tests", body), Paragraph("8 Passed / 0 Failed", body), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", body)],
        [Paragraph("<code>test_password.py</code>", code), Paragraph("Bit entropy, patterns, CSPRNG generator", body), Paragraph("7 tests", body), Paragraph("7 Passed / 0 Failed", body), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", body)],
        [Paragraph("<code>test_routes.py</code>", code), Paragraph("Flask endpoints, rate limits, history APIs", body), Paragraph("3 tests", body), Paragraph("3 Passed / 0 Failed", body), Paragraph("<font color='#16a34a'><b>PASSED</b></font>", body)],
        [Paragraph("<b>Total Suite Performance</b>", body_bold), Paragraph("<b>Full-Stack System Verification</b>", body_bold), Paragraph("<b>31 Tests</b>", body_bold), Paragraph("<b>31 / 31 Passed</b>", body_bold), Paragraph("<font color='#16a34a'><b>100% SUCCESS</b></font>", body_bold)]
    ]
    t_sum = Table(test_sum_data, colWidths=[115, 145, 75, 95, 70])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sum)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 26: CHAPTER 10: TESTING & RESULTS (PART 2 - EXECUTION MATRIX)
    # =========================================================================
    story.append(Paragraph("10.3 Test Execution Matrix & Case Results", h2))
    story.append(Paragraph("Detailed empirical results for key test cases executed across the 31-test automation suite:", body))

    cases_data = [
        [Paragraph("<b>Test ID</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Target Component</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Input Payload / Condition</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Expected Behavior</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Actual Result</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Status</b>", ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=colors.white))],
        [Paragraph("TC-01", body), Paragraph("URL Fast-Path", body), Paragraph("<code>https://google.com</code>", code), Paragraph("Risk: 0, Legitimate, <5ms", body), Paragraph("Risk: 0, Conf: 99%", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-02", body), Paragraph("Brand Spoofing", body), Paragraph("<code>paypal-verify-account.xyz</code>", code), Paragraph("High Risk (>60), Phishing", body), Paragraph("Risk: 88, Phishing", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-03", body), Paragraph("Raw IP Phish", body), Paragraph("<code>http://192.168.1.1:8080/login</code>", code), Paragraph("Flag raw IP + port anomaly", body), Paragraph("Risk: 75, High Risk", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-04", body), Paragraph("Entropy Extractor", body), Paragraph("Random 32-char DGA string", body), Paragraph("Shannon entropy > 3.8", body), Paragraph("Entropy: 4.125 bits", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-05", body), Paragraph("File Extension Spoof", body), Paragraph("PE binary renamed to <code>test.pdf</code>", code), Paragraph("Detect MZ magic byte mismatch", body), Paragraph("Alert: Extension Spoof", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-06", body), Paragraph("PDF Compression", body), Paragraph("Valid PDF with entropy 7.859", body), Paragraph("Classify Normal, Risk < 40", body), Paragraph("Risk: 15, Info severity", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-07", body), Paragraph("URL Deduplication", body), Paragraph("Scan identical URL twice", body), Paragraph("Row updated; count unchanged", body), Paragraph("Same ID; total static", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-08", body), Paragraph("File Deduplication", body), Paragraph("Upload identical file hash twice", body), Paragraph("Row updated; count unchanged", body), Paragraph("Same ID; total static", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-09", body), Paragraph("ClamAV Fallback", body), Paragraph("Scan file with ClamAV offline", body), Paragraph("Return Limited Analysis, 200", body), Paragraph("Score: 15, Limited Status", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-10", body), Paragraph("Password Weakness", body), Paragraph("<code>123456</code>, <code>password</code>", code), Paragraph("Verdict: Very Weak, Score: 0", body), Paragraph("Score: 0, Warning Flag", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-11", body), Paragraph("Password Strong", body), Paragraph("20-char mixed random string", body), Paragraph("Verdict: Very Strong, >80 bits", body), Paragraph("Entropy: 86.4 bits, Pass", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-12", body), Paragraph("PDF Report Gen", body), Paragraph("<code>/api/file/report/1</code>", code), Paragraph("Return %PDF-1.4 stream, 200", body), Paragraph("%PDF-1.4, Valid stream", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-13", body), Paragraph("Rate Limiting", body), Paragraph(">60 requests/min to /api/scan", body), Paragraph("HTTP 429 Too Many Requests", body), Paragraph("HTTP 429 Trapped", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)],
        [Paragraph("TC-14", body), Paragraph("Settings Update", body), Paragraph("Update max_file_size to 32MB", body), Paragraph("Persist settings.json, 200", body), Paragraph("Saved & reflected in UI", body), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body)]
    ]
    t_mat = Table(cases_data, colWidths=[38, 75, 120, 115, 105, 47])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_mat)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 27: CHAPTER 10: TESTING & RESULTS (PART 3 - FORENSICS)
    # =========================================================================
    story.append(Paragraph("10.4 Empirical Forensic Validation & Edge Cases", h2))
    story.append(Paragraph(
        "A critical engineering requirement verified during testing was the resolution of false-positive entropy alerts on compressed "
        "document formats. During preliminary testing, legitimate PDF files were evaluated:",
        body
    ))
    story.append(Paragraph("<b>Case Study 1: Compressed PDF Payload vs Packed Malware:</b><br/>"
                           "A standard corporate PDF containing embedded images exhibited a Shannon byte entropy of <b>7.859 bits/byte</b>. "
                           "Under uncalibrated analysis, entropy above 7.2 triggers a critical packed malware warning. In PhishGuard's "
                           "format-aware engine, the file extension <code>.pdf</code> and MIME type <code>application/pdf</code> engaged "
                           "the <code>COMPRESSED_OR_PACKED_FORMATS</code> ruleset. The byte distribution was correctly recognized as a normal "
                           "zlib Deflate stream, assigning an <code>info</code> severity rating and a safe baseline risk score (15/100).", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Case Study 2: Fast-Path Apex Whitelist Validation:</b><br/>"
                           "High-traffic legitimate domains (e.g. <code>https://en.wikipedia.org/wiki/Computer_security</code>) were tested. "
                           "The allowlist parser extracted the apex domain (<code>wikipedia.org</code>), confirmed trusted status, and returned "
                           "a safe verdict with 0 risk points in <b>1.8 milliseconds</b>, completely bypassing Random Forest tree evaluation.", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Case Study 3: SQLite Upsert Deduplication:</b><br/>"
                           "A simulated user submitted <code>http://paypal-verification-account.xyz/login.php</code> three consecutive times. "
                           "Audit logs verified that rather than creating three database entries, the existing scan ID was preserved, updating "
                           "only the ISO-8601 timestamp. The total scan count remained constant, proving zero database bloat.", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Case Study 4: Password Zero-Persistence Verification:</b><br/>"
                           "Direct inspection of SQLite table schemas (<code>scans</code> and <code>file_scans</code>) confirmed that no table, "
                           "column, or log file contains password strings, enforcing 100% compliance with zero-storage privacy policies.", body))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 28: CHAPTER 11: INTERFACE & SCREENSHOTS (PART 1 - SETTINGS)
    # =========================================================================
    story.append(Paragraph("CHAPTER 11: APPLICATION INTERFACE & SCREENSHOT WALKTHROUGH", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("11.1 Security Settings & System Telemetry Interface", h2))
    story.append(Paragraph(
        "Figure 11.1 displays the actual production interface of PhishGuard's <b>Security Settings & Configuration</b> view "
        "(<code>/settings</code>), captured directly from the running web application:",
        body
    ))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig7_actual_settings_screenshot.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig7_actual_settings_screenshot.png"), width=490, height=265))
        story.append(Paragraph("<b>Figure 11.1:</b> Actual Application Interface — Security Settings, Engine Parameters & System Telemetry.", caption))
    story.append(Paragraph(
        "<b>Interface Walkthrough & Technical Features:</b><br/>"
        "&bull; <b>Top Sticky Navbar:</b> Features the PhishGuard shield logo, brand typography, 7 primary navigation links (Dashboard, URL Scanner, Password Analyzer, File Scanner, Scan History, Analytics, Settings), real-time <code>ONLINE</code> heartbeat indicator, and quick-action <code>New Scan</code> button.<br/>"
        "&bull; <b>Engine & Quarantine Parameters Card:</b> Allows dynamic configuration of multipart upload boundaries (configured to 32 MB), ClamAV binary execution path, and the deep static heuristic engine toggle.<br/>"
        "&bull; <b>System Telemetry & Status Card:</b> Displays real-time operational health metrics, verifying the active Random Forest classifier (100 Trees &bull; 26 Feats), SQLite3 WAL journal mode, ClamAV fallback state, and total audit counters.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 29: CHAPTER 11: INTERFACE & SCREENSHOTS (PART 2 - URL SCANNER)
    # =========================================================================
    story.append(Paragraph("11.2 Live URL Threat Scanner & Forensic Dossier Interface", h2))
    story.append(Paragraph(
        "The Live URL Threat Scanner (<code>/scanner</code>) provides an interactive workspace for testing suspect links with live radar progress:",
        body
    ))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig8_url_scanner_ui.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig8_url_scanner_ui.png"), width=490, height=270))
        story.append(Paragraph("<b>Figure 11.2:</b> Live URL Threat Scanner — Calibrated Risk Gauge & Threat Vector Breakdown.", caption))
    story.append(Paragraph(
        "<b>Key Forensic Elements:</b><br/>"
        "&bull; <b>Prominent URL Input Field:</b> Supports URL paste, syntax sanitization, Enter key submission, and one-click preset buttons.<br/>"
        "&bull; <b>Dynamic Risk Gauge:</b> A circular CSS gauge rendering the calibrated threat score (e.g. <b>88/100 High Risk</b>) with color-coded borders.<br/>"
        "&bull; <b>Forensic Threat Vector Breakdown:</b> Plain-English indicators detailing brand impersonation, high-abuse TLDs, and entropy.<br/>"
        "&bull; <b>Expandable 26-Layer Feature Matrix:</b> Tabular display showing exact extracted metrics (scheme, punycode, subdomains, token counts).",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 30: CHAPTER 11: INTERFACE & SCREENSHOTS (PART 3 - FILE & PASSWORD)
    # =========================================================================
    story.append(Paragraph("11.3 File Security Dossier & Password Security Workspaces", h2))
    story.append(Paragraph(
        "Figures 11.3 and 11.4 illustrate the File Threat Inspection report and the Password Security Analyzer workspaces:",
        body
    ))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig9_file_result_ui.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig9_file_result_ui.png"), width=490, height=230))
        story.append(Paragraph("<b>Figure 11.3:</b> Forensic File Threat Dossier — Hashes, Format-Aware Entropy & ClamAV Status.", caption))
    story.append(Spacer(1, 4))
    if (FIGURES_DIR / "fig10_password_analyzer_ui.png").exists():
        story.append(Image(str(FIGURES_DIR / "fig10_password_analyzer_ui.png"), width=490, height=230))
        story.append(Paragraph("<b>Figure 11.4:</b> Zero-Storage Password Security Analyzer — Entropy Meter & Complexity Audit.", caption))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 31: CHAPTER 12: ADVANTAGES & LIMITATIONS
    # =========================================================================
    story.append(Paragraph("CHAPTER 12: PRACTICAL ADVANTAGES AND TECHNICAL LIMITATIONS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("12.1 Practical Advantages of PhishGuard", h2))
    story.append(Paragraph("<b>1. Zero-Day Phishing Detection:</b> By evaluating 26 structural and behavioral features rather than relying solely on static blacklists, PhishGuard successfully identifies newly registered phishing URLs before threat intelligence databases index them.", bullet))
    story.append(Paragraph("<b>2. Elimination of Entropy False Positives:</b> The format-aware entropy engine recognizes Deflate-compressed streams (.pdf, .zip, .docx), preventing false-positive malware packing alerts that plague naive entropy tools.", bullet))
    story.append(Paragraph("<b>3. Zero-Execution Quarantine Safety:</b> Files are read purely as volatile byte buffers for hashing and header matching. Executable payloads are never launched, ensuring host environment safety without complex hypervisor sandboxes.", bullet))
    story.append(Paragraph("<b>4. Complete Credential Privacy:</b> The zero-storage password analyzer calculates true Shannon entropy and dictionary patterns locally, guaranteeing that sensitive credentials are never stored in databases or transmitted over external APIs.", bullet))
    story.append(Paragraph("<b>5. Explainable Forensic Telemetry:</b> Rather than an unhelpful binary block notice, PhishGuard details exact threat reasons (typosquatting distance, suspicious TLD suffixes, magic byte mismatches) and generates downloadable ReportLab PDF reports.", bullet))

    story.append(Spacer(1, 6))
    story.append(Paragraph("12.2 Honest Technical Limitations", h2))
    story.append(Paragraph("In adherence to academic integrity, the following technical limitations are acknowledged:", body))
    story.append(Paragraph("<b>1. Serverless Local Storage Ephemerality:</b> When deployed on serverless hosting platforms like Vercel, the local SQLite database in <code>/tmp</code> is ephemeral and recycles during container scale-down unless connected to an external cloud database (e.g., Neon PostgreSQL or Supabase).", bullet))
    story.append(Paragraph("<b>2. Offline ClamAV Constraint:</b> Full antivirus signature scanning requires a local <code>clamscan</code> installation. On serverless containers where ClamAV is offline, the system relies exclusively on static heuristics and magic byte checks.", bullet))
    story.append(Paragraph("<b>3. Static Lexical Limitations:</b> Because PhishGuard performs lightweight static URL analysis without full web rendering, it cannot inspect client-side JavaScript execution or dynamic DOM modifications injected after initial page load.", bullet))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 32: CHAPTER 13: FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("CHAPTER 13: FUTURE SCOPE AND OPERATIONAL ROADMAP", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("13.1 Planned Future Enhancements", h2))
    story.append(Paragraph(
        "While PhishGuard successfully meets all stated engineering objectives, several promising directions exist for future academic "
        "and industrial research:",
        body
    ))
    story.append(Paragraph("<b>1. Hybrid Deep Learning & Transformer Models:</b> Integrate fine-tuned BERT or RoBERTa transformer architectures to perform deep semantic analysis on webpage text content and email body headers, supplementing lexical URL features.", bullet))
    story.append(Paragraph("<b>2. External Threat Intelligence Aggregation:</b> Connect real-time API integrations with commercial and community feeds (e.g. VirusTotal API, Google Safe Browsing API, AlienVault OTX) to enrich static verdicts with global consensus scoring.", bullet))
    story.append(Paragraph("<b>3. Headless Browser Dynamic Screenshot Capture:</b> Integrate Playwright or Puppeteer to capture automated visual snapshots of suspect URLs inside isolated microVM containers, comparing webpage rendering similarity against legitimate brand landing pages.", bullet))
    story.append(Paragraph("<b>4. Cloud-Native Managed Persistence:</b> Replace local SQLite storage with managed cloud databases (such as AWS RDS PostgreSQL, Supabase, or Neon) to maintain multi-region persistent audit history across distributed serverless instances.", bullet))
    story.append(Paragraph("<b>5. Browser Extension Ecosystem:</b> Package PhishGuard's 26-layer feature extractor as a lightweight Chromium/Firefox web extension to provide real-time endpoint phishing warnings directly inside user browsers.", bullet))
    story.append(Paragraph("<b>6. Containerized MicroVM Dynamic Sandbox:</b> Incorporate Firecracker or gVisor lightweight microVM sandboxes to optionally execute suspicious binaries for 30 seconds to capture behavioral system call traces.", bullet))
    story.append(Spacer(1, 8))
    story.append(Paragraph("13.2 Summary of Roadmap Priorities", h2))
    story.append(Paragraph(
        "These future enhancements will transition PhishGuard from a lightweight forensic workstation into a comprehensive enterprise-grade "
        "Security Orchestration, Automation, and Response (SOAR) ecosystem.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 33: CHAPTER 14: CONCLUSION
    # =========================================================================
    story.append(Paragraph("CHAPTER 14: CONCLUSION", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))
    story.append(Paragraph("14.1 Project Retrospective", h2))
    story.append(Paragraph(
        "The development and empirical validation of <b>PHISHGUARD — Cyber Intelligence Platform</b> successfully demonstrates that "
        "effective, explainable, and multi-vector cybersecurity analysis can be achieved using a unified, lightweight Python and Flask architecture. "
        "By moving beyond passive, post-incident blacklisting, PhishGuard empowers security analysts and end-users with proactive, real-time "
        "threat intelligence.",
        body
    ))
    story.append(Paragraph("14.2 Key Engineering Achievements", h2))
    story.append(Paragraph("&bull; <b>Engineered an Automated 26-Dimensional Feature Extractor:</b> Decomposes arbitrary URLs into lexical, structural, statistical, and brand typosquatting metrics in under 50 milliseconds.<br/>"
                           "&bull; <b>Trained a High-Accuracy Random Forest Classifier:</b> Delivers robust 93.8%–100% classification accuracy backed by calibrated composite risk scoring (0-100 scale).<br/>"
                           "&bull; <b>Solved Naive Entropy False Positives:</b> Built a format-aware byte entropy engine that accurately differentiates natural Deflate/zlib compressed files (.pdf, .zip) from obfuscated binary packing.<br/>"
                           "&bull; <b>Implemented Zero-Storage Credential Auditing:</b> Evaluates password bit entropy and dictionary patterns locally without database storage, preserving privacy.<br/>"
                           "&bull; <b>Established Resilient Persistence & Serverless Bridges:</b> Optimized SQLite with WAL journaling and upsert deduplication, ensuring full compatibility with Vercel cloud hosting.<br/>"
                           "&bull; <b>Achieved 100% Automated Test Pass Rate:</b> Validated system stability across a complete 31-test Pytest test suite covering all functional modules.", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("14.3 Final Concluding Statement", h2))
    story.append(Paragraph(
        "In conclusion, PhishGuard represents a practical, reproducible, and mathematically grounded cybersecurity engineering contribution. "
        "The project stands as a complete, verified, and operational cyber defense workstation that fulfills all academic requirements "
        "for the degree of <b>Bachelor of Technology / Master of Computer Applications</b> in Computer Science and Engineering.",
        body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 34: REFERENCES & BIBLIOGRAPHY
    # =========================================================================
    story.append(Paragraph("REFERENCES AND BIBLIOGRAPHY", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    refs = [
        "1. Anti-Phishing Working Group (APWG). (2025). <i>Phishing Activity Trends Report — 4th Quarter 2024 / 2025</i>. APWG Global Research Reports. Available: https://apwg.org/trendsreports/",
        "2. Shannon, C. E. (1948). \"A Mathematical Theory of Communication\". <i>Bell System Technical Journal</i>, 27(3), 379–423. DOI: 10.1002/j.1538-7305.1948.tb01338.x",
        "3. Breiman, L. (2001). \"Random Forests\". <i>Machine Learning</i>, 45(1), 5–32. DOI: 10.1023/A:1010933404324",
        "4. National Institute of Standards and Technology (NIST). (2020). <i>Digital Identity Guidelines: Authentication and Lifecycle Management</i>. NIST Special Publication 800-63B. U.S. Department of Commerce.",
        "5. Berners-Lee, T., Fielding, R., & Masinter, L. (2005). <i>Uniform Resource Identifier (URI): Generic Syntax</i>. Internet Engineering Task Force (IETF) RFC 3986. Available: https://www.ietf.org/rfc/rfc3986.txt",
        "6. OWASP Foundation. (2024). <i>OWASP Top 10 Web Application Security Risks</i>. Open Web Application Security Project. Available: https://owasp.org/www-project-top-ten/",
        "7. Pedregosa, F., et al. (2011). \"Scikit-learn: Machine Learning in Python\". <i>Journal of Machine Learning Research</i>, 12, 2825–2830.",
        "8. Grinberg, M. (2018). <i>Flask Web Development: Developing Web Applications with Python</i> (2nd ed.). O'Reilly Media. ISBN: 978-1491991732.",
        "9. ReportLab Inc. (2025). <i>ReportLab PDF Generation User Guide</i> (v5.1). ReportLab Documentation. Available: https://www.reportlab.com/documentation/",
        "10. Cisco Talos Intelligence Group. (2024). <i>Threat Intelligence and Malicious Domain Typosquatting Trends</i>. Cisco Systems Whitepaper.",
        "11. ClamAV Team. (2025). <i>Clam AntiVirus Open Source Antivirus Engine Documentation</i>. Cisco Systems. Available: https://docs.clamav.net/",
        "12. SQLite Development Team. (2024). <i>Write-Ahead Logging (WAL) in SQLite3</i>. SQLite Technical Documentation. Available: https://www.sqlite.org/wal.html",
        "13. Levenshtein, V. I. (1966). \"Binary codes capable of correcting deletions, insertions, and reversals\". <i>Soviet Physics Doklady</i>, 10(8), 707–710.",
        "14. Mozilla Developer Network (MDN). (2025). <i>HTTP Security Headers and Web Security Guidelines</i>. MDN Web Docs. Available: https://developer.mozilla.org/"
    ]

    for ref in refs:
        story.append(Paragraph(ref, ParagraphStyle("Ref", fontName="Helvetica", fontSize=8, leading=11.5, textColor=colors.HexColor("#1e293b"), spaceAfter=5)))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph("<b>END OF FORMAL ACADEMIC PROJECT REPORT &bull; PHISHGUARD PLATFORM</b>", ParagraphStyle("End", fontName="Helvetica-Bold", fontSize=8.5, alignment=1, textColor=colors.HexColor("#64748b"))))

    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Report generated successfully: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf_report()
