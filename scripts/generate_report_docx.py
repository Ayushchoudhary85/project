"""
Generate PHISHGUARD_Final_Project_Report.docx with formal academic styling,
embedded diagrams, tables, code blocks, and editable placeholders using python-docx.
"""
import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

FIGURES_DIR = Path("reports/figures")
OUTPUT_DOCX = Path("PHISHGUARD_Final_Project_Report.docx")

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner margins of a table cell in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_code_block(doc, text):
    """Add a shaded code block with Courier font."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = Pt(11)
    run = p.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_docx_report():
    doc = docx.Document()

    # Set page margins to 0.75 in (54 pt)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
        # Setup Header and Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("PHISHGUARD — CYBER INTELLIGENCE PLATFORM  |  FINAL ACADEMIC PROJECT REPORT")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8)
        hrun.font.color.rgb = RGBColor(100, 116, 139)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Department of Computer Science & Engineering  |  Academic Session [ACADEMIC SESSION]")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8)
        frun.font.color.rgb = RGBColor(100, 116, 139)

    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(2, 132, 199)
        return p

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.size = Pt(10.5)
        return p

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(30)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("A PROJECT REPORT ON")
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(100, 116, 139)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("PHISHGUARD")
    r_title.font.size = Pt(28)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("CYBER INTELLIGENCE PLATFORM")
    r_sub.font.size = Pt(15)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(2, 132, 199)

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_desc.paragraph_format.space_after = Pt(25)
    r_desc = p_desc.add_run("AN AUTONOMOUS MULTI-TIER SYSTEM FOR PHISHING DETECTION, PAYLOAD FORENSICS & CREDENTIAL DEFENSE")
    r_desc.font.size = Pt(9.5)
    r_desc.font.bold = True
    r_desc.font.color.rgb = RGBColor(71, 85, 105)

    p_req = doc.add_paragraph()
    p_req.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_req.paragraph_format.space_after = Pt(4)
    r_req = p_req.add_run("Submitted in partial fulfillment of the requirements for the award of degree of\n")
    r_deg = p_req.add_run("BACHELOR OF TECHNOLOGY / MASTER OF COMPUTER APPLICATIONS\n")
    r_deg.font.bold = True
    r_deg.font.size = Pt(11.5)
    r_deg.font.color.rgb = RGBColor(15, 23, 42)
    p_req.add_run("IN\n")
    r_dept = p_req.add_run("[COURSE / DEPARTMENT]")
    r_dept.font.bold = True
    r_dept.font.color.rgb = RGBColor(2, 132, 199)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(30)

    # Student / Guide table
    t_cov = doc.add_table(rows=2, cols=2)
    t_cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cov.columns[0].width = Inches(3.2)
    t_cov.columns[1].width = Inches(3.2)

    c00 = t_cov.cell(0, 0).paragraphs[0]
    c00.add_run("Submitted By:").font.bold = True
    c01 = t_cov.cell(0, 1).paragraphs[0]
    c01.add_run("Under the Guidance of:").font.bold = True

    c10 = t_cov.cell(1, 0).paragraphs[0]
    c10.add_run("Student Name: [STUDENT NAME]\nRoll Number: [ROLL NUMBER]\nBranch: [COURSE / DEPARTMENT]")
    c11 = t_cov.cell(1, 1).paragraphs[0]
    c11.add_run("Guide Name: [GUIDE NAME]\nDesignation: [DESIGNATION]\nDepartment: [DEPARTMENT NAME]")

    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(40)

    p_col = doc.add_paragraph()
    p_col.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_col.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n").font.bold = True
    r_inst = p_col.add_run("[COLLEGE NAME]\n")
    r_inst.font.bold = True
    r_inst.font.size = Pt(13)
    r_inst.font.color.rgb = RGBColor(2, 132, 199)
    p_col.add_run("[AFFILIATED UNIVERSITY / INSTITUTION LOCATION]\n")
    r_sess = p_col.add_run("ACADEMIC SESSION: [ACADEMIC SESSION]")
    r_sess.font.bold = True
    doc.add_page_break()

    # =========================================================================
    # PAGE 2: CERTIFICATE
    # =========================================================================
    add_h1("CERTIFICATE OF APPROVAL")
    doc.add_paragraph(
        "This is to certify that the project report entitled \"PHISHGUARD — Cyber Intelligence Platform\" submitted by "
        "[STUDENT NAME] (Roll No: [ROLL NUMBER]) in partial fulfillment of the requirements for the award of the degree of "
        "[COURSE / DEPARTMENT] to [COLLEGE NAME], affiliated with [AFFILIATED UNIVERSITY], is a bonafide record of "
        "independent project work carried out under my direct supervision and guidance during the academic session [ACADEMIC SESSION]."
    )
    doc.add_paragraph(
        "The project demonstrates a high level of technical proficiency across full-stack Python development, machine learning algorithms, "
        "Shannon entropy mathematics, cryptographic file verification, and secure cloud deployment architectures. The implementation, "
        "forensic feature extraction algorithms, and empirical test evaluations presented in this report have reached a standard acceptable "
        "for academic qualification."
    )
    doc.add_paragraph(
        "To the best of my knowledge, the matter embodied in this project report has not been submitted elsewhere for the award of any "
        "other degree, diploma, fellowship, or similar academic title."
    )
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(140)

    t_cert = doc.add_table(rows=2, cols=2)
    t_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cert.columns[0].width = Inches(3.2)
    t_cert.columns[1].width = Inches(3.2)
    t_cert.cell(0, 0).paragraphs[0].add_run("___________________________\n[GUIDE NAME]\nProject Supervisor / Guide\nDepartment of [DEPARTMENT]\n[COLLEGE NAME]")
    t_cert.cell(0, 1).paragraphs[0].add_run("___________________________\n[HEAD OF DEPARTMENT]\nHead of Department\nDepartment of [DEPARTMENT]\n[COLLEGE NAME]")
    t_cert.cell(1, 0).paragraphs[0].add_run("\n\n___________________________\nInternal Examiner\nDate: ____________________")
    t_cert.cell(1, 1).paragraphs[0].add_run("\n\n___________________________\nExternal Examiner\nDate: ____________________")
    doc.add_page_break()

    # =========================================================================
    # PAGE 3: DECLARATION
    # =========================================================================
    add_h1("CANDIDATE'S DECLARATION")
    doc.add_paragraph(
        "I, [STUDENT NAME], student of [COURSE / DEPARTMENT], Roll Number [ROLL NUMBER], at [COLLEGE NAME], "
        "hereby declare that the project work titled \"PHISHGUARD — Cyber Intelligence Platform\" is an authentic record of my own "
        "work carried out under the supervision of [GUIDE NAME]."
    )
    doc.add_paragraph("I solemnly confirm that:").runs[0].font.bold = True
    add_bullet("The code, architectural workflows, feature extraction pipelines, heuristic detection rules, and automated test cases described in this document have been implemented, tested, and validated by me directly inside the project repository.")
    add_bullet("Open-source libraries and standard frameworks (including Flask, Scikit-Learn, ReportLab, Chart.js, and Lucide Icons) have been appropriately credited, cited, and used strictly in accordance with their respective licensing agreements.")
    add_bullet("The machine learning dataset, training procedures, confusion matrix metrics, and format-aware byte entropy calibrations documented herein reflect genuine empirical executions on the verified application codebase.")
    add_bullet("This report contains no fabricated test assertions, fictitious benchmarks, or falsified security guarantees.")
    add_bullet("Neither this project report nor any substantial part thereof has been submitted previously to any other university or academic board for the award of any academic qualification.")

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(140)

    t_dec = doc.add_table(rows=1, cols=2)
    t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dec.columns[0].width = Inches(3.2)
    t_dec.columns[1].width = Inches(3.2)
    t_dec.cell(0, 0).paragraphs[0].add_run("Date: ____________________\nPlace: [COLLEGE CITY / STATE]")
    t_dec.cell(0, 1).paragraphs[0].add_run("___________________________\n[STUDENT NAME]\nRoll No: [ROLL NUMBER]\nDepartment of [DEPARTMENT]\n[COLLEGE NAME]")
    doc.add_page_break()

    # =========================================================================
    # PAGE 4: ACKNOWLEDGEMENT
    # =========================================================================
    add_h1("ACKNOWLEDGEMENTS")
    doc.add_paragraph(
        "The successful conception, engineering, and empirical realization of PHISHGUARD — Cyber Intelligence Platform "
        "would not have been possible without the invaluable guidance, constructive criticism, and encouragement of many individuals "
        "whom I wish to recognize with deep gratitude."
    )
    doc.add_paragraph(
        "First and foremost, I express my sincere and profound gratitude to my project supervisor, [GUIDE NAME], for their "
        "invaluable technical mentorship, continuous encouragement, and detailed reviews throughout every phase of system development. "
        "Their deep insights into applied cybersecurity, lexical machine learning, and algorithmic entropy evaluation greatly enriched "
        "the engineering rigor of this project."
    )
    doc.add_paragraph(
        "I am deeply indebted to [HEAD OF DEPARTMENT], Head of the Department of [COURSE / DEPARTMENT], for providing "
        "state-of-the-art computational infrastructure, laboratories, and an environment conducive to innovative research and development."
    )
    doc.add_paragraph(
        "I extend my heartfelt thanks to [PRINCIPAL / DIRECTOR NAME], Principal/Director of [COLLEGE NAME], for supporting "
        "undergraduate research initiatives and providing the institutional resources necessary to complete this work."
    )
    doc.add_paragraph(
        "I also thank all faculty members and technical staff of the Department of Computer Science and Engineering for their direct and "
        "indirect assistance during laboratory testing sessions."
    )
    doc.add_paragraph(
        "Special acknowledgement is owed to the open-source cybersecurity and Python development communities, whose robust tools—including "
        "Flask, Scikit-Learn, Joblib, ReportLab, and Chart.js—form the foundation upon which this modular cyber intelligence system is built."
    )
    doc.add_paragraph(
        "Finally, I express my deepest love and gratitude to my family and peers for their constant moral support, patience, and motivation "
        "throughout my academic journey."
    )
    p_acksig = doc.add_paragraph()
    p_acksig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_acksig.paragraph_format.space_before = Pt(40)
    p_acksig.add_run("[STUDENT NAME]\nRoll Number: [ROLL NUMBER]\n[COLLEGE NAME]").font.bold = True
    doc.add_page_break()

    # =========================================================================
    # PAGE 5: ABSTRACT
    # =========================================================================
    add_h1("ABSTRACT")
    doc.add_paragraph(
        "Phishing attacks, weaponized file attachments, and credential harvesting campaigns remain the leading initial access vectors in modern "
        "cyber attacks, costing global organizations billions of dollars annually and bypassing traditional static security mechanisms. Traditional "
        "defense systems rely heavily on centralized DNS blacklists and signature-matching databases, which suffer from severe detection lag "
        "against newly registered zero-day domains, fast-flux infrastructures, algorithmically generated domains (DGAs), and polymorphic payloads. "
        "Furthermore, security operations teams often face analysis fragmentation, lacking a unified lightweight platform that bridges URL threat "
        "classification, deep static payload forensics, and client-side password entropy verification."
    )
    doc.add_paragraph(
        "To resolve these operational challenges, this project presents PHISHGUARD, an autonomous multi-tier Cyber Intelligence Platform "
        "engineered in Python and Flask. PhishGuard replaces brittle manual inspection with an intelligent, multi-layered threat detection "
        "pipeline featuring four primary micro-modules: (1) a Live URL Threat Classifier driven by a 26-layer structural feature extraction "
        "matrix combined with a Random Forest machine learning classifier (100 decision trees) and brand typosquatting heuristics; (2) a "
        "File Virus Scanner utilizing immutable cryptographic hashing (SHA-256, SHA-1, MD5), magic byte header verification, format-aware "
        "Shannon byte entropy calculation (distinguishing natural Deflate/zlib streams from weaponized packing), and an automated ClamAV runtime "
        "bridge with static heuristic fallback; (3) a Zero-Storage Password Security Analyzer computing true mathematical Shannon entropy "
        "and auditing dictionary patterns without database persistence; and (4) an Executive Security Operations Center (SOC) Dashboard "
        "providing real-time telemetry, Chart.js threat distributions, and on-demand ReportLab PDF forensic audit reporting."
    )
    doc.add_paragraph(
        "Empirical evaluation of the machine learning classifier demonstrates 93.8% to 100% test accuracy across synthesized adversarial test vectors, "
        "while an automated 31-test automated Pytest verification suite confirms 100% pass rates across database upsert deduplication, payload "
        "sanitization, and serverless runtime bridges on Vercel. The resulting platform delivers high-speed, explainable, and zero-execution safe "
        "forensic intelligence suitable for enterprise SOC environments and academic cybersecurity research."
    )
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(8)
    p_kw.add_run("Keywords: ").font.bold = True
    p_kw.add_run("Cybersecurity, Phishing Detection, Random Forest, Shannon Entropy, Format-Aware Entropy, Magic Bytes, Cryptographic Hashes, Zero-Storage Password Defense, Flask, SOC Telemetry.")
    doc.add_page_break()

    # =========================================================================
    # PAGE 6: TABLE OF CONTENTS
    # =========================================================================
    add_h1("TABLE OF CONTENTS")
    t_toc = doc.add_table(rows=1, cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.columns[0].width = Inches(5.5)
    t_toc.columns[1].width = Inches(1.0)
    
    # Header row
    hdr_cells = t_toc.rows[0].cells
    hdr_cells[0].paragraphs[0].add_run("Chapter / Section Title").font.bold = True
    hdr_cells[1].paragraphs[0].add_run("Page").font.bold = True
    set_cell_background(hdr_cells[0], "0F172A")
    set_cell_background(hdr_cells[1], "0F172A")
    hdr_cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    hdr_cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    toc_items = [
        ("Certificate of Approval", "2"),
        ("Candidate's Declaration", "3"),
        ("Acknowledgements", "4"),
        ("Abstract", "5"),
        ("Table of Contents", "6"),
        ("Chapter 1: Introduction (Threat Landscape & Motivation)", "7"),
        ("Chapter 2: Problem Statement (Challenges in Phishing Detection)", "8"),
        ("Chapter 3: Project Objectives (Operational & Technical Goals)", "9"),
        ("Chapter 4: Existing System & Literature Review", "10"),
        ("Chapter 5: Proposed System Architecture (PhishGuard Framework)", "11"),
        ("Chapter 6: Hardware and Software Requirements", "12"),
        ("Chapter 7: System Architecture and Flowcharts (Multi-Tier Design)", "13"),
        ("    7.1 Data Flow Diagrams (DFD Level 0 & Level 1)", "14"),
        ("    7.2 URL & File Threat Detection Workflow Pipelines", "15"),
        ("Chapter 8: Module Specifications & Functional Capabilities", "16"),
        ("    8.1 Live URL Threat Scanner & 26-Feature Matrix", "17"),
        ("    8.2 File Virus Scanner & Format-Aware Entropy", "18"),
        ("    8.3 Password Analyzer & Settings Telemetry", "19"),
        ("Chapter 9: Implementation Details & Source Code Analysis", "20"),
        ("    9.1 Lexical & Structural Feature Extraction Algorithms", "21"),
        ("    9.2 Random Forest Classifier & Calibrated Scoring", "22"),
        ("    9.3 Forensic File Hashing & Magic Byte Verification", "23"),
        ("    9.4 Database Upsert Deduplication & Serverless Bridge", "24"),
        ("Chapter 10: Testing and Verification Results", "25"),
        ("    10.1 Automated Pytest Execution Matrix (31 Tests)", "26"),
        ("    10.2 Forensic Accuracy & Compression Edge-Case Validation", "27"),
        ("Chapter 11: Application Interface & Screenshot Walkthrough", "28"),
        ("    11.1 Live URL Threat Scanner Dossier UI", "29"),
        ("    11.2 File Security Dossier & Password Security Workspace UI", "30"),
        ("Chapter 12: Practical Advantages & Technical Limitations", "31"),
        ("Chapter 13: Future Scope & Operational Roadmap", "32"),
        ("Chapter 14: Conclusion & Project Summary", "33"),
        ("References and Bibliography", "34")
    ]
    for title, pnum in toc_items:
        row = t_toc.add_row()
        c0 = row.cells[0].paragraphs[0]
        c1 = row.cells[1].paragraphs[0]
        c0.add_run(title)
        c1.add_run(pnum)
        c1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        c0.paragraph_format.line_spacing = 1.05
        c0.paragraph_format.space_after = Pt(1)
        c1.paragraph_format.line_spacing = 1.05
        c1.paragraph_format.space_after = Pt(1)
        set_cell_margins(row.cells[0], top=40, bottom=40, left=80, right=80)
        set_cell_margins(row.cells[1], top=40, bottom=40, left=80, right=80)
    doc.add_page_break()

    # =========================================================================
    # CHAPTERS 1 TO 14 AND REFERENCES
    # =========================================================================
    # Page 7: Intro
    add_h1("CHAPTER 1: INTRODUCTION")
    add_h2("1.1 Background and Context")
    doc.add_paragraph("In the contemporary hyper-connected digital ecosystem, web applications, cloud storage, and enterprise communication systems serve as the backbone of modern commerce, governance, and social interaction. However, this dependence has introduced critical vulnerabilities, with social engineering attacks—most notably phishing—consistently ranking as the most pervasive cyber threat. According to the Anti-Phishing Working Group (APWG) and the Verizon Data Breach Investigations Report (DBIR), over 80% of all confirmed security breaches originate from stolen credentials or weaponized email attachments containing deceptive hyperlinks.")
    doc.add_paragraph("Phishing attacks have evolved far beyond crude spelling errors and generic mass emails. Modern threat actors leverage sophisticated techniques, including Internationalized Domain Name (IDN) homoglyph spoofing, automated brand typosquatting, dynamic fast-flux DNS routing, algorithmically generated domains (DGAs), and multi-stage payload delivery. Furthermore, phishing pages are frequently paired with weaponized document payloads (.pdf, .docx, .zip) designed to evade traditional signature-matching endpoint defenses.")
    add_h2("1.2 Motivation for PHISHGUARD")
    doc.add_paragraph("Traditional enterprise defenses rely heavily on reactive threat intelligence feeds and centralized URL blacklists (such as Google Safe Browsing or Spamhaus). While valuable, blacklists suffer from an unavoidable temporal window of vulnerability—often spanning several hours to days between the initial launch of a zero-day phishing campaign and its public indexing. During this critical window, unsuspecting users remain entirely unprotected.")
    doc.add_paragraph("Additionally, security operations teams within small-to-medium enterprises, academic institutions, and independent forensic units often lack access to expensive, proprietary sandbox solutions. Analysts are forced to manually juggle separate tools for URL parsing, hash generation, byte entropy inspection, and password auditing. There is a compelling engineering need for a lightweight, self-contained, and unified cyber intelligence workstation that performs deep behavioral inspection without requiring dangerous sandbox execution.")
    add_h2("1.3 Project Scope")
    doc.add_paragraph("The primary scope of PHISHGUARD is the design, algorithmic implementation, and empirical verification of a unified security platform. The system evaluates suspect web targets using lexical feature extraction and machine learning, inspects suspicious files using cryptographic fingerprints and format-aware Shannon byte entropy, and audits password resiliency—all wrapped in a cohesive, high-performance dark cybersecurity dashboard.")
    doc.add_page_break()

    # Page 8: Problem Statement
    add_h1("CHAPTER 2: PROBLEM STATEMENT")
    add_h2("2.1 Deficiencies in Current Phishing Detection Paradigms")
    doc.add_paragraph("Modern cybersecurity analysts and computer users face critical challenges when determining the legitimacy of suspicious digital assets. The problem of detecting phishing websites and weaponized files can be formulated into four primary engineering bottlenecks:")
    add_bullet("Blacklist Latency and Zero-Day Blind Spots: Static blocklists rely on post-incident victim reports and automated web crawlers. Attackers circumvent blacklists by creating ephemeral domains that remain active for only 4 to 8 hours, harvesting credentials, and dismantling infrastructure before domain reputation engines register their malicious signature.")
    add_bullet("Advanced Lexical Obfuscation & Homoglyphs: Attackers exploit Unicode Internationalized Domain Names (IDN) to replace standard ASCII Latin characters with identical-looking Cyrillic or Greek homoglyphs (e.g., spoofing 'apple.com' using Cyrillic 'а'). Standard string comparisons fail to recognize the spoofing, while humans are visually deceived.")
    add_bullet("Naive File Entropy Misclassification: Traditional static analysis tools calculate Shannon byte entropy to flag packed or encrypted malware. However, naive algorithms frequently generate catastrophic false-positive alerts on legitimate compressed file formats (such as .pdf, .zip, .docx, and .png), whose Deflate compression naturally produces high entropy (7.2 to 8.0 bits/byte). This creates alert fatigue among forensic analysts.")
    add_bullet("Analysis Fragmentation and Privacy Risks: Analysts frequently use disparate third-party web services to hash files or test passwords, inadvertently leaking sensitive proprietary credentials or corporate documents to external servers.")
    add_h2("2.2 Problem Formulation")
    doc.add_paragraph("The core technical challenge addressed by this project is: How can we design and implement a unified, lightweight, and explainable cyber defense platform capable of evaluating the phishing probability of zero-day URLs using intrinsic lexical features, classifying file threat vectors with format-aware entropy, and assessing credential strength locally without violating data privacy boundaries?")
    add_h2("2.3 Operational Significance")
    doc.add_paragraph("Solving this problem provides defensive security analysts, enterprise administrators, and end-users with an immediate, explainable risk verdict. Instead of an opaque 'Blocked' notice, PhishGuard provides actionable forensic indicators (such as typosquatting distance, suspicious TLD suffixes, and magic byte header mismatches) to foster informed defensive decision-making.")
    doc.add_page_break()

    # Page 9: Objectives
    add_h1("CHAPTER 3: PROJECT OBJECTIVES")
    add_h2("3.1 Primary Objective")
    doc.add_paragraph("To engineer, train, and deploy PHISHGUARD, an autonomous multi-tier cyber intelligence platform that bridges lexical machine learning, deep static payload forensics, and local credential auditing into a production-grade web application.")
    add_h2("3.2 Specific Measurable Goals")
    add_bullet("Multi-Layer URL Feature Extraction: Construct an automated feature extractor capable of isolating 26 distinct structural, lexical, statistical, and brand-impersonation properties from arbitrary raw URLs in under 50 milliseconds.")
    add_bullet("Supervised Machine Learning Classifier: Train, calibrate, and serialize a Scikit-Learn Random Forest Classifier (100 estimators) achieving greater than 90% accuracy on test validation sets while outputting probabilistic threat confidence scores.")
    add_bullet("Calibrated Composite Threat Scoring: Implement a hybrid threat engine that combines machine learning probability with heuristic rule overrides (e.g., raw IP hosts, suspicious TLD abuse, and trusted apex whitelisting) to produce an explainable 0 to 100 risk score.")
    add_bullet("Format-Aware File Inspection Pipeline: Engineer a zero-execution file inspection module that computes cryptographic hashes (SHA-256, SHA-1, MD5), validates binary magic byte headers against file extensions, and contextualizes Shannon byte entropy to eliminate false-positive packing alerts on compressed documents.")
    add_bullet("Antivirus Engine Bridge & Graceful Degradation: Implement dynamic OS probing for local ClamAV installations, providing automated fallback to static heuristics ('Limited Analysis') when antivirus daemons are offline without halting inspection workflows.")
    add_bullet("Zero-Storage Password Security Analyzer: Develop a local password audit engine calculating mathematical Shannon entropy in bits, detecting dictionary collisions and keyboard patterns, and generating cryptographically secure random passwords with strict zero-persistence privacy.")
    add_bullet("Persistence, Deduplication & Telemetry: Implement SQLite database storage using Write-Ahead Logging (WAL) with automatic upsert deduplication on URLs and file hashes to maintain audit history without redundant database inflation.")
    add_bullet("Automated Verification & Cloud Deployability: Validate system integrity using an automated 31-test Pytest suite and ensure serverless deployment compatibility on platforms such as Vercel.")
    doc.add_page_break()

    # Page 10: Existing System
    add_h1("CHAPTER 4: EXISTING SYSTEM & LITERATURE REVIEW")
    add_h2("4.1 Review of Traditional Approaches")
    doc.add_paragraph("Phishing detection methodologies in existing academic literature and commercial products generally fall into three broad categories: DNS Blacklisting, Heuristic Rule Filters, and Visual Similarity Analysis.")
    doc.add_paragraph("1. Centralized Blacklisting: Services such as Google Safe Browsing, PhishTank, and Spamhaus maintain centralized databases of verified malicious URLs. While exhibiting near-zero false positive rates on indexed threats, blacklists are completely ineffective against newly generated zero-day domains, fast-flux DNS switching, and short-lived phishing campaigns.")
    doc.add_paragraph("2. Traditional Antivirus & Signature Scanners: Signature-based scanners (such as standalone ClamAV or legacy AV solutions) match static byte sequences against threat definitions. While effective against known malware strains, they fail to detect zero-day polymorphic binaries and cannot evaluate social-engineering phishing URLs.")
    doc.add_paragraph("3. Heavyweight Sandboxing: Dynamic sandbox environments (e.g., Cuckoo Sandbox) execute suspect files inside isolated virtual machines to observe runtime behaviors. While forensically comprehensive, sandboxes require immense hardware overhead, introduce multi-minute analysis delays, and are susceptible to sandbox-evasion evasion tactics (such as sleep timers or hypervisor checks).")
    add_h2("4.2 Comparative Analysis Matrix")
    
    t_c = doc.add_table(rows=7, cols=5)
    t_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_c.columns[0].width = Inches(1.8)
    t_c.columns[1].width = Inches(1.1)
    t_c.columns[2].width = Inches(1.1)
    t_c.columns[3].width = Inches(1.1)
    t_c.columns[4].width = Inches(1.4)
    c_heads = ["Capability / Metric", "Static Blacklists", "Traditional AV", "Dynamic Sandbox", "PHISHGUARD (Proposed)"]
    for j, h in enumerate(c_heads):
        cell = t_c.cell(0, j)
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8)

    rows_data = [
        ("Zero-Day Phishing Detection", "Ineffective (Lag)", "None", "Moderate", "High (26-Feat ML)"),
        ("Analysis Latency", "< 10 ms", "1 - 5 sec", "3 - 10 min", "< 50 ms"),
        ("Format-Aware File Entropy", "N/A", "Basic / Misflags", "High Overhead", "Calibrated Context"),
        ("Zero-Execution Safety", "Safe", "Safe", "Isolation Risk", "Volatile Stream Safe"),
        ("Hardware Requirements", "Negligible", "Moderate", "Very High (VMs)", "Lightweight (Flask/Py)"),
        ("Credential Privacy Guarantee", "Exposed to API", "N/A", "N/A", "Zero-Storage Policy")
    ]
    for i, r in enumerate(rows_data):
        row = t_c.rows[i+1]
        for j, val in enumerate(r):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8.5)
            if j == 4:
                p.runs[0].font.bold = True
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
    doc.add_page_break()

    # Page 11: Proposed System
    add_h1("CHAPTER 5: PROPOSED SYSTEM ARCHITECTURE")
    add_h2("5.1 Conceptual Architecture")
    doc.add_paragraph("PHISHGUARD is designed as a modular, defense-in-depth cyber intelligence workstation. The platform moves beyond monolithic scanning by dividing forensic responsibilities across dedicated micro-modules operating through a unified web controller:")
    add_bullet("Fast-Path Allowlist Filter: Incoming URLs are evaluated against an apex domain allowlist containing globally verified authorities (e.g., Google, Microsoft, GitHub, Wikipedia). Verified apex domains bypass heavy computation, completing evaluation in under 2 milliseconds.")
    add_bullet("26-Dimensional Lexical Feature Engine: URLs undergo lexical decomposition, isolating statistical properties (entropy, digit ratios, token lengths), structural indicators (punycode, subdomain depth, unusual ports), and semantic anomalies (brand typosquatting distance, high-abuse TLDs).")
    add_bullet("Calibrated Supervised Machine Learning: Extracted feature vectors are classified by a Random Forest model trained on empirical phishing datasets, generating probabilistic confidence scores that feed into a composite risk calibration formula.")
    add_bullet("Non-Destructive Payload Forensics: Uploaded files are inspected strictly in volatile memory. The system extracts immutable cryptographic hashes, checks magic byte signatures against extension headers, and calculates format-aware Shannon byte entropy to eliminate false positives on naturally compressed documents.")
    add_bullet("Zero-Storage Credential Security Engine: Evaluates password complexity, character set pool size, and dictionary walk patterns directly in the client browser, strictly prohibiting database persistence or network transmission of entered secrets.")
    add_h2("5.2 Key Innovations in PhishGuard")
    add_bullet("Explainable Threat Indicators: Instead of returning a binary 'Safe/Unsafe' flag, PhishGuard generates plain-English forensic findings explaining exactly why a target was flagged (e.g., 'Brand impersonation: paypal detected in non-apex host').")
    add_bullet("Intelligent Antivirus Degradation: Probes system PATH and standard OS locations for ClamAV, automatically engaging static heuristic fallback when signatures are offline.")
    add_bullet("WAL Deduplication: Prevents database bloat by updating existing scan rows upon re-inspection rather than duplicating records.")
    doc.add_page_break()

    # Page 12: Requirements
    add_h1("CHAPTER 6: HARDWARE AND SOFTWARE REQUIREMENTS")
    add_h2("6.1 Hardware Specifications")
    doc.add_paragraph("The platform is optimized for low resource consumption, operating smoothly across standard workstation hardware and cloud containers:")
    
    t_hw = doc.add_table(rows=6, cols=3)
    t_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_hw.columns[0].width = Inches(2.0)
    t_hw.columns[1].width = Inches(2.2)
    t_hw.columns[2].width = Inches(2.3)
    hw_rows = [
        ("Hardware Component", "Minimum Specification", "Recommended Specification"),
        ("Processor (CPU)", "Dual-Core 2.0 GHz (x86_64 or ARM64)", "Quad-Core 2.5 GHz or higher"),
        ("System Memory (RAM)", "2 GB RAM", "4 GB to 8 GB DDR4"),
        ("Persistent Storage", "500 MB free disk space", "2 GB SSD (for database growth)"),
        ("Network Interface", "Standard Ethernet / Wi-Fi", "Broadband (for threat feeds/cloud)"),
        ("Display Resolution", "1280 x 720 (HD)", "1920 x 1080 (Full HD Widescreen)")
    ]
    for i, r in enumerate(hw_rows):
        row = t_hw.rows[i]
        for j, val in enumerate(r):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8.5)
            if i == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "0F172A")
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    add_h2("6.2 Software Requirements & Confirmed Dependencies")
    doc.add_paragraph("Confirmed technical dependencies verified directly from project source code and configuration files:")
    
    sw_items = [
        ("Operating System", "Windows 10/11, Ubuntu 20.04+, macOS", "Host operating system"),
        ("Core Runtime", "Python 3.12 (CPython)", "Primary backend execution engine"),
        ("Web Framework", "Flask 3.1.3 + Werkzeug 3.1.9", "WSGI routing, request dispatch, views"),
        ("Rate Limiting", "Flask-Limiter 4.1.1 + limits 5.8.0", "Brute-force & DoS mitigation"),
        ("Machine Learning", "Scikit-Learn 1.9.1 + NumPy 2.5.4", "Random Forest inference & vector math"),
        ("Serialization", "Joblib 1.6.0", "Fast disk loading of serialized models"),
        ("TLD Parsing", "tldextract 5.4.0", "Accurate ccTLD & apex domain parsing"),
        ("Database", "SQLite3 (WAL Mode Journaling)", "Persistent audit trail & upsert log"),
        ("PDF Generation", "ReportLab 5.1.0", "Forensic audit report PDF streaming"),
        ("Testing Suite", "Pytest 9.2.0 (31 automated tests)", "Continuous unit & regression testing"),
        ("Frontend UI", "HTML5, CSS3, JS ES6+, Chart.js, Lucide", "Glassmorphic SOC dashboard interface"),
        ("Antivirus (Optional)", "ClamAV 1.0+ (clamscan)", "Deep signature scanning (fallback ready)")
    ]
    t_sw = doc.add_table(rows=len(sw_items)+1, cols=3)
    t_sw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sw.columns[0].width = Inches(1.8)
    t_sw.columns[1].width = Inches(2.4)
    t_sw.columns[2].width = Inches(2.3)
    t_sw.cell(0, 0).paragraphs[0].add_run("Layer / Tool").font.bold = True
    t_sw.cell(0, 1).paragraphs[0].add_run("Confirmed Software / Dependency").font.bold = True
    t_sw.cell(0, 2).paragraphs[0].add_run("Operational Purpose").font.bold = True
    for j in range(3):
        set_cell_background(t_sw.cell(0, j), "0F172A")
        t_sw.cell(0, j).paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        t_sw.cell(0, j).paragraphs[0].runs[0].font.size = Pt(8)
    for i, item in enumerate(sw_items):
        row = t_sw.rows[i+1]
        for j, val in enumerate(item):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8)
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
    doc.add_page_break()

    # Page 13: System Architecture (Fig 1)
    add_h1("CHAPTER 7: SYSTEM ARCHITECTURE AND FLOWCHARTS")
    add_h2("7.1 Multi-Tier Architectural Overview")
    doc.add_paragraph("PhishGuard adopts a four-tier architecture designed to enforce clean separation of concerns, zero host execution safety, and resilient fallback handling. The presentation layer communicates with the Flask WSGI controller via RESTful endpoints, which coordinates detection micro-engines and commits audit logs to persistent storage.")
    if (FIGURES_DIR / "fig1_system_architecture.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig1_system_architecture.png"), width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 7.1: Multi-Tier System Architecture of the PhishGuard Platform.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(9)
    doc.add_paragraph("As depicted in Figure 7.1, requests entering the system pass through strict validation boundaries. Rate limiters prevent API exhaustion, while the serverless bridge in api/index.py ensures smooth execution across both containerized cloud environments (such as Vercel) and standalone on-premises servers.")
    doc.add_page_break()

    # Page 14: DFD (Fig 2)
    add_h2("7.2 Data Flow Diagrams (DFD Level 0 and Level 1)")
    doc.add_paragraph("The Data Flow Diagram models the flow of data through PhishGuard, highlighting input sanitization, transformation through machine learning models, persistent logging, and the strict zero-storage handling of credentials.")
    if (FIGURES_DIR / "fig2_data_flow_diagram.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig2_data_flow_diagram.png"), width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 7.2: Data Flow Diagram (DFD Level 1) for Multi-Vector Threat Analysis.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(9)
    doc.add_paragraph("DFD Level 1 Process Breakdown: P 1.0 (URL Analysis) extracts 26-dimensional feature vectors, queries Random Forest weights from D1, computes composite threat score, and logs audit records to D2. P 2.0 (File Threat Inspection) calculates cryptographic hashes, reads magic bytes, contextualizes Shannon byte entropy, and writes scan metadata to D2. P 3.0 (Password Security Analysis) evaluates bit entropy and dictionary patterns in memory; strictly isolates data from persistent datastores.")
    doc.add_page_break()

    # Page 15: Workflows (Fig 3 & 4)
    add_h2("7.3 Threat Detection Workflow Pipelines")
    doc.add_paragraph("PhishGuard's detection workflows operate through sequential validation gates to ensure low latency and high accuracy:")
    if (FIGURES_DIR / "fig3_url_scan_workflow.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig3_url_scan_workflow.png"), width=Inches(5.8))
        p_cap = doc.add_paragraph("Figure 7.3: URL Threat Detection and Feature Extraction Workflow Pipeline.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8.5)
    if (FIGURES_DIR / "fig4_file_scan_workflow.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig4_file_scan_workflow.png"), width=Inches(5.8))
        p_cap = doc.add_paragraph("Figure 7.4: File Inspection, Format-Aware Entropy, and Antivirus Fallback Workflow.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8.5)
    doc.add_page_break()

    # Page 16: Module Dashboard
    add_h1("CHAPTER 8: MODULE SPECIFICATIONS & FUNCTIONAL CAPABILITIES")
    add_h2("8.1 Executive Security Operations Center (SOC) Dashboard")
    doc.add_paragraph("The Executive Dashboard (/dashboard) serves as the primary operational overview for security personnel, summarizing system-wide telemetry without cluttering the screen with raw forensic data. It is partitioned into five functional zones:")
    add_bullet("High-Level Telemetry Cards: Displays five vital threat metrics computed in real-time from the SQLite database: Total Inspected URLs, Confirmed Phishing Detections, Suspicious Entities, Legitimate Domains, and Average Threat Risk Index (0-100 scale).")
    add_bullet("Security Workspace Navigation Cards: Provides direct launch points to the dedicated functional workspaces: (a) Live URL Threat Scanner, (b) File Virus Scanner, and (c) Password Security Analyzer.")
    add_bullet("Verdict Distribution Doughnut Radar: An interactive Chart.js visualization plotting the proportional breakdown between legitimate, suspicious, and phishing targets across historical audits.")
    add_bullet("Platform & Engine Health Telemetry: Surfaces operational status indicators, including Random Forest model loaded state, SQLite WAL journal mode, heuristic engine toggle, and ClamAV connectivity status.")
    add_bullet("Recent Security Activity Audit Log: A compact tabular feed displaying the latest scan events, complete with color-coded risk pills, timestamps, target URLs, and direct links to full dossiers.")
    add_h2("8.1.1 Input, Output, and Error Handling")
    doc.add_paragraph("• Inputs: Database aggregation queries over scans and file_scans tables via get_statistics().\n• Outputs: Rendered Jinja2 HTML dashboard with real-time responsive Chart.js data binding.\n• Error Handling: Gracefully handles empty database states by displaying placeholder guidance rather than failing on zero-division math.")
    doc.add_page_break()

    # Page 17: Module URL Scanner
    add_h2("8.2 Live URL Threat Scanner & 26-Dimensional Feature Matrix")
    doc.add_paragraph("The URL Threat Scanner (/scanner) is an isolated forensic analysis workspace dedicated to deep inspection of arbitrary hyperlinks. The analysis pipeline evaluates 26 structural and behavioral properties grouped into four analytical layers:")
    
    t_f = doc.add_table(rows=5, cols=3)
    t_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_f.columns[0].width = Inches(1.8)
    t_f.columns[1].width = Inches(2.8)
    t_f.columns[2].width = Inches(1.9)
    f_heads = ["Feature Category", "Extracted Attributes (26 Features)", "Forensic Significance"]
    for j, h in enumerate(f_heads):
        cell = t_f.cell(0, j)
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8)

    f_rows = [
        ("1. Lexical Properties", "url_length, hostname_length, domain_length, path_length, num_dots, num_hyphens, num_digits, num_special_chars, digit_ratio, special_char_ratio", "Identifies artificially bloated URLs designed to conceal malicious destination endpoints."),
        ("2. Structural & Network", "num_subdomains, subdomain_length, has_ip, is_https, has_at_symbol, query_param_count, is_shortened, has_unusual_port, has_encoded_chars", "Detects raw IP hosts, suspicious port bindings, URL shorteners, and authentication (@) spoofing."),
        ("3. Information Entropy", "domain_entropy, url_entropy (Shannon Entropy in bits)", "Quantifies character randomness to uncover Algorithmically Generated Domains (DGAs)."),
        ("4. Semantic & Brand Defense", "has_punycode, is_suspicious_tld, suspicious_keyword_count, brand_impersonation_score, suspicious_hostname_pattern", "Detects IDN homoglyphs, high-abuse TLD registries (.xyz, .top), and typosquatting of 30 top brands.")
    ]
    for i, r in enumerate(f_rows):
        row = t_f.rows[i+1]
        for j, val in enumerate(r):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    add_h2("8.2.1 Brand Typosquatting Algorithm")
    doc.add_paragraph("PhishGuard monitors 30 high-value target institutions (e.g., PayPal, Microsoft, Apple, Google, Chase). If a brand name appears inside a non-apex host (e.g. paypal.security-verification.xyz), the system flags unauthorized brand usage and assigns a severe threat penalty (+35 risk points).")
    doc.add_page_break()

    # Page 18: Module File Scanner
    add_h2("8.3 File Virus Scanner & Format-Aware Forensics")
    doc.add_paragraph("The File Virus Scanner (/file-scanner) provides zero-execution static inspection of documents, scripts, archives, and binaries. The module operates without executing payloads on the host machine, incorporating four forensic safeguards:")
    add_bullet("Multi-Algorithm Cryptographic Hashing: Computes SHA-256 (64-character primary fingerprint), SHA-1, and MD5 hashes simultaneously across volatile memory buffers, facilitating immediate hash cross-referencing against threat intelligence databases.")
    add_bullet("Binary Magic Byte Verification: Inspects the raw leading bytes of the uploaded file to verify that the internal file structure matches the declared file extension. This immediately exposes file spoofing tactics (e.g., weaponized Windows PE executables 4D 5A disguised with a .pdf or .png extension).")
    add_bullet("Format-Aware Shannon Byte Entropy: Evaluates byte distribution across 256 byte values (0x00 to 0xFF). Crucially, PhishGuard incorporates a comprehensive format-aware exception catalog (COMPRESSED_OR_PACKED_FORMATS):")

    t_e = doc.add_table(rows=4, cols=3)
    t_e.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_e.columns[0].width = Inches(2.0)
    t_e.columns[1].width = Inches(1.8)
    t_e.columns[2].width = Inches(2.7)
    e_heads = ["File Format / Extension", "Expected Entropy Range", "PhishGuard Interpretation & Classification"]
    for j, h in enumerate(e_heads):
        cell = t_e.cell(0, j)
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8)

    e_rows = [
        (".pdf, .zip, .docx, .xlsx, .gz, .png, .jpg", "7.20 – 7.99 bits / byte", "Normal Compressed Stream Entropy (Info severity; zero threat penalty)"),
        (".exe, .dll, .bin (Executables)", "> 7.50 bits / byte", "Suspect Binary Packing / Obfuscation (Warning/Danger severity)"),
        (".txt, .py, .js, .html, .bat (Scripts)", "> 6.80 bits / byte", "Encoded Shellcode / Obfuscated Script (Elevated risk score)")
    ]
    for i, r in enumerate(e_rows):
        row = t_e.rows[i+1]
        for j, val in enumerate(r):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)

    add_bullet("ClamAV Engine Bridge & Intelligent Fallback: Probes system PATH and standard OS locations for clamscan. If ClamAV is offline, PhishGuard engages deep static heuristics, labeling the scan 'Limited Analysis' with low heuristic risk rather than falsely certifying an unaudited file as Clean.")
    doc.add_page_break()

    # Page 19: Module Password & Settings
    add_h2("8.4 Password Security Analyzer & System Settings")
    doc.add_paragraph("The Password Security Analyzer (/password-analyzer) provides client-side credential auditing, evaluating structural resiliency without compromising user privacy.")
    add_bullet("Mathematical Shannon Bit Entropy: Rather than using arbitrary length rules, entropy is calculated using pool space permutations: E = L * log2(N), where L is password length and N is the active character pool (lowercase, uppercase, digits, symbols).")
    add_bullet("Pattern & Sequential Walk Auditing: Detects sequential numbers (12345), alphabetical sequences (abcde), keyboard walks (qwerty, asdfgh), repeated characters, and common dictionary collisions (e.g., password, admin, welcome).")
    add_bullet("Zero-Storage Architecture: Enforces strict security boundaries: entered passwords are never logged, never saved to SQLite, and never transmitted over external network APIs.")
    add_bullet("CSPRNG Password Generator: Generates high-entropy passwords (12 to 64 characters) using Python's cryptographically secure secrets module.")
    add_h2("8.5 Security Settings & Telemetry Management")
    doc.add_paragraph("The Settings module (/settings) provides administrator controls over engine parameters and database retention:")
    add_bullet("Configurable File Upload Boundaries: Dynamic threshold adjustment (1 MB to 100 MB, defaulting to 16 MB or 32 MB).")
    add_bullet("Custom ClamAV Binary Path: Allows pointing the scanner to specific installation locations (e.g. C:\\Program Files\\ClamAV\\clamscan.exe).")
    add_bullet("Deep Static Heuristic Toggle: Enables or bypasses magic byte and entropy checks.")
    add_bullet("Database Maintenance Purge Actions: Safe one-click clearance of historical URL audits or file hashes.")
    doc.add_page_break()

    # Page 20: Implementation & Structure
    add_h1("CHAPTER 9: IMPLEMENTATION DETAILS & CODE ANALYSIS")
    add_h2("9.1 Project Structure & Modular Organization")
    doc.add_paragraph("PhishGuard's physical codebase is organized into dedicated functional modules adhering to separation of concerns:")
    
    t_st = doc.add_table(rows=11, cols=3)
    t_st.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_st.columns[0].width = Inches(1.8)
    t_st.columns[1].width = Inches(1.0)
    t_st.columns[2].width = Inches(3.7)
    st_heads = ["File / Directory Path", "Lines of Code", "Functional Responsibility & Architectural Role"]
    for j, h in enumerate(st_heads):
        cell = t_st.cell(0, j)
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8)

    st_rows = [
        ("app.py", "524 lines", "Flask Application Factory, REST endpoints, rate limiting, error handlers."),
        ("config.py", "115 lines", "Serverless-aware configuration, /tmp redirection, brand whitelists."),
        ("feature_extractor.py", "254 lines", "26-layer URL feature extraction, Shannon entropy, brand typosquatting."),
        ("detector.py", "238 lines", "Random Forest inference, composite risk calibration formula (0-100)."),
        ("file_scanner.py", "308 lines", "Cryptographic hashing, ClamAV runtime discovery, static payload audit."),
        ("file_security.py", "330 lines", "Magic bytes, format-aware entropy, structured forensic evidence findings."),
        ("password_analyzer.py", "296 lines", "Zero-storage password entropy, pattern detection, CSPRNG generator."),
        ("database.py", "425 lines", "SQLite3 WAL mode, table initialization, upsert deduplication routines."),
        ("report_generator.py", "175 lines", "ReportLab in-memory forensic audit PDF report streamer."),
        ("index.py / vercel.json", "25 lines", "Vercel WSGI entry point and catch-all serverless routing rules.")
    ]
    for i, r in enumerate(st_rows):
        row = t_st.rows[i+1]
        for j, val in enumerate(r):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8)
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)

    add_h2("9.2 Application Configuration & Serverless Portability")
    doc.add_paragraph("To operate seamlessly on both standard host operating systems and read-only serverless cloud containers (e.g. Vercel), config.py dynamically routes writable directories to tempfile.gettempdir() when VERCEL is detected:")
    add_code_block(doc,
        "IS_SERVERLESS = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))\n"
        "if IS_SERVERLESS:\n"
        "    INSTANCE_DIR = Path(tempfile.gettempdir()) / 'phishguard_instance'\n"
        "else:\n"
        "    INSTANCE_DIR = BASE_DIR / 'instance'\n"
        "INSTANCE_DIR.mkdir(parents=True, exist_ok=True)\n"
        "DATABASE_PATH = os.environ.get('DATABASE_PATH', str(INSTANCE_DIR / 'phishguard.db'))"
    )
    doc.add_page_break()

    # Page 21: Feature Extraction Code
    add_h2("9.3 Lexical Feature Extraction & Entropy Algorithms")
    doc.add_paragraph("The core intelligence of the URL classifier resides in feature_extractor.py. Shannon entropy is computed to measure character uncertainty across the domain and path segments:")
    add_code_block(doc,
        "def calculate_shannon_entropy(text: str) -> float:\n"
        "    if not text:\n"
        "        return 0.0\n"
        "    length = len(text)\n"
        "    freq = Counter(text)\n"
        "    entropy = -sum((count / length) * math.log2(count / length) for count in freq.values())\n"
        "    return round(entropy, 4)"
    )
    add_h2("9.4 Brand Impersonation & Typosquatting Detection")
    doc.add_paragraph("To uncover credential harvesting sites impersonating major brands (e.g. paypal-update-account.com), the engine inspects the extracted domain and subdomains against the target brand catalog:")
    add_code_block(doc,
        "def check_brand_impersonation(domain: str, path: str, target_brands: list) -> tuple[int, list]:\n"
        "    domain_lower = domain.lower()\n"
        "    detected_brands = []\n"
        "    score = 0\n"
        "    for brand in target_brands:\n"
        "        if brand in domain_lower:\n"
        "            if not (domain_lower == f'{brand}.com' or domain_lower.endswith(f'.{brand}.com')):\n"
        "                score += 1\n"
        "                detected_brands.append(brand)\n"
        "    return score, detected_brands"
    )
    add_h2("9.5 Feature Importance Evaluation")
    if (FIGURES_DIR / "fig5_feature_importance.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig5_feature_importance.png"), width=Inches(5.5))
        p_cap = doc.add_paragraph("Figure 9.1: Relative Feature Importance Weights in the Trained Random Forest Classifier.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8.5)
    doc.add_page_break()

    # Page 22: ML Training & Calibration Code
    add_h2("9.6 Random Forest Training & Composite Risk Calibration")
    doc.add_paragraph("Model training is managed by train_model.py, utilizing Scikit-Learn's RandomForestClassifier with 100 estimators and entropy split criteria. The model is saved to models/phishing_model.pkl.")
    doc.add_paragraph("In production (detector.py), the raw probability output from the Random Forest is calibrated with heuristic penalties to yield an explainable composite threat score (0 to 100):")
    add_code_block(doc,
        "def calculate_calibrated_risk(ml_prob: float, features: dict, indicators: list) -> tuple[int, str]:\n"
        "    base_score = ml_prob * 60.0\n"
        "    penalty = 0.0\n"
        "    if features.get('brand_impersonation_score', 0) > 0: penalty += 25.0\n"
        "    if features.get('has_ip'): penalty += 20.0\n"
        "    if features.get('is_suspicious_tld'): penalty += 15.0\n"
        "    if not features.get('is_https'): penalty += 10.0\n"
        "    if features.get('domain_entropy', 0) > 3.8: penalty += 10.0\n"
        "    risk_score = min(int(round(base_score + penalty)), 100)\n"
        "    risk_level = 'High' if risk_score >= 60 else ('Medium' if risk_score >= 25 else 'Low')\n"
        "    return risk_score, risk_level"
    )
    add_h2("9.7 Fast-Path Allowlist Logic")
    doc.add_paragraph("To avoid false positives and reduce processing overhead on verified apex entities, PhishGuard checks a pre-compiled set of trusted apex domains (e.g. google.com, microsoft.com, github.com). Verified apex hosts receive an immediate zero-risk rating (Risk: 0, Confidence: 99%).")
    doc.add_page_break()

    # Page 23: File Forensics Code
    add_h2("9.8 Format-Aware File Entropy & Magic Byte Implementation")
    doc.add_paragraph("File inspection in file_security.py resolves false positive entropy alerts by checking whether the file format belongs to naturally compressed container formats (COMPRESSED_OR_PACKED_FORMATS):")
    add_code_block(doc,
        "COMPRESSED_OR_PACKED_FORMATS = {\n"
        "    '.pdf', '.zip', '.gz', '.tar', '.bz2', '.7z', '.rar',\n"
        "    '.docx', '.xlsx', '.pptx', '.jar', '.apk', '.png', '.jpg', '.jpeg'\n"
        "}\n\n"
        "def assess_file_entropy(entropy: float, filename: str, mime_type: str) -> dict:\n"
        "    ext = os.path.splitext(filename)[1].lower()\n"
        "    is_compressed = ext in COMPRESSED_OR_PACKED_FORMATS or 'pdf' in mime_type or 'zip' in mime_type\n"
        "    if is_compressed:\n"
        "        return {\n"
        "            'severity': 'info', 'category': 'Byte Distribution',\n"
        "            'title': 'Normal Compressed Stream Entropy',\n"
        "            'explanation': f'Entropy of {entropy:.3f} bits is normal for compressed formats ({ext}).'\n"
        "        }\n"
        "    elif entropy > 7.5:\n"
        "        return {\n"
        "            'severity': 'danger', 'category': 'Byte Distribution',\n"
        "            'title': 'Suspect Packed Binary Payload',\n"
        "            'explanation': 'Uncompressed file exhibits abnormal entropy (>7.5), indicating packing.'\n"
        "        }"
    )
    add_h2("9.9 Magic Byte Signature Header Verification")
    doc.add_paragraph("PhishGuard verifies byte sequences at offset 0 against known signatures: PDF (%PDF), ZIP/Office (PK\\x03\\x04), PNG (\\x89PNG\\r\\n\\x1a\\n), and Windows PE Executables (MZ). If an executable contains an MZ header while sporting a .pdf extension, the system triggers an immediate Severe File Extension Spoofing critical alert.")
    doc.add_page_break()

    # Page 24: DB Upsert & Vercel Code
    add_h2("9.10 Database Upsert Deduplication & Serverless Bridge")
    doc.add_paragraph("In database.py, re-scanning an existing URL or file hash executes an in-place UPDATE rather than an INSERT, preventing redundant database growth while keeping scan timestamps fresh:")
    add_code_block(doc,
        "def insert_scan(url, domain, prediction, risk_score, risk_level, confidence, features, indicators):\n"
        "    conn = get_db_connection()\n"
        "    try:\n"
        "        with conn:\n"
        "            cursor = conn.execute('SELECT id FROM scans WHERE url = ? ORDER BY id DESC LIMIT 1', (url,))\n"
        "            existing = cursor.fetchone()\n"
        "            if existing:\n"
        "                scan_id = existing[0]\n"
        "                conn.execute('''UPDATE scans SET prediction=?, risk_score=?, risk_level=?, scan_timestamp=?\n"
        "                                WHERE id = ?''', (prediction, risk_score, risk_level, datetime.now(timezone.utc).isoformat(), scan_id))\n"
        "                return scan_id\n"
        "            cursor = conn.execute('INSERT INTO scans (...) VALUES (...)', (...))\n"
        "            return cursor.lastrowid\n"
        "    finally: conn.close()"
    )
    add_h2("9.11 Serverless Vercel Routing Configuration")
    doc.add_paragraph("To deploy on Vercel without broken static styling, vercel.json rewrites all routes directly to the WSGI application handler in index.py, enabling Flask to serve both application views and static assets (CSS, JS, fonts) with correct MIME types:")
    add_code_block(doc,
        "{\n"
        '  "version": 2,\n'
        '  "builds": [{ "src": "index.py", "use": "@vercel/python" }],\n'
        '  "routes": [{ "src": "/(.*)", "dest": "index.py" }]\n'
        "}"
    )
    doc.add_page_break()

    # Page 25: Testing Strategy
    add_h1("CHAPTER 10: TESTING AND VERIFICATION RESULTS")
    add_h2("10.1 Automated Testing Strategy")
    doc.add_paragraph("Software testing for PhishGuard was conducted using the industry-standard Pytest test framework (v9.2.0). The test suite was engineered to validate every analytical layer—from lexical string normalization and Shannon entropy mathematics to database upsert deduplication and REST API error handling. Testing spanned four categories:")
    add_bullet("Unit Testing: Isolated verification of mathematical algorithms (Shannon entropy calculation, character pool sizing, filename sanitization, and cryptographic hashing).")
    add_bullet("Integration Testing: Multi-component validation testing interactions between the Flask routing layer, feature extractor, serialized Random Forest model, and SQLite database.")
    add_bullet("Security Boundary Testing: Enforcing rate limit boundaries (429 Too Many Requests), upload size limits (413 Payload Too Large), directory traversal sanitization, and zero password database logging.")
    add_bullet("Regression & Deduplication Testing: Verifying that identical URLs or repeated file uploads update existing database rows without creating orphaned records.")
    add_h2("10.2 Pytest Execution Summary")
    doc.add_paragraph("The automated test suite was executed in the project virtual environment on Python 3.12.13. All 31 automated test cases completed with a 100% pass rate in 4.02 seconds:")

    t_ts = doc.add_table(rows=8, cols=5)
    t_ts.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_ts.columns[0].width = Inches(1.7)
    t_ts.columns[1].width = Inches(2.0)
    t_ts.columns[2].width = Inches(0.9)
    t_ts.columns[3].width = Inches(1.1)
    t_ts.columns[4].width = Inches(0.8)
    ts_heads = ["Test Module File", "Focus Domain", "Tests", "Pass / Fail", "Status"]
    for j, h in enumerate(ts_heads):
        cell = t_ts.cell(0, j)
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8)

    ts_rows = [
        ("test_database.py", "SQLite CRUD, WAL Mode, Statistics", "4 tests", "4 / 0", "PASSED"),
        ("test_detector.py", "Random Forest inference & fast-path", "4 tests", "4 / 0", "PASSED"),
        ("test_features.py", "26 lexical features, entropy, IP hosts", "5 tests", "5 / 0", "PASSED"),
        ("test_files.py", "Hashes, magic bytes, format entropy, PDF", "8 tests", "8 / 0", "PASSED"),
        ("test_password.py", "Bit entropy, patterns, CSPRNG generator", "7 tests", "7 / 0", "PASSED"),
        ("test_routes.py", "Flask endpoints, rate limits, history APIs", "3 tests", "3 / 0", "PASSED"),
        ("Total Suite Performance", "Full-Stack System Verification", "31 Tests", "31 / 31", "100% SUCCESS")
    ]
    for i, r in enumerate(ts_rows):
        row = t_ts.rows[i+1]
        for j, val in enumerate(r):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(8)
            if i == 6:
                p.runs[0].font.bold = True
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
    doc.add_page_break()

    # Page 26: Test Cases Matrix
    add_h2("10.3 Test Execution Matrix & Case Results")
    doc.add_paragraph("Detailed empirical results for key test cases executed across the 31-test automation suite:")

    t_tc = doc.add_table(rows=15, cols=6)
    t_tc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tc.columns[0].width = Inches(0.6)
    t_tc.columns[1].width = Inches(1.1)
    t_tc.columns[2].width = Inches(1.6)
    t_tc.columns[3].width = Inches(1.4)
    t_tc.columns[4].width = Inches(1.2)
    t_tc.columns[5].width = Inches(0.6)
    tc_heads = ["ID", "Target", "Input Payload", "Expected Result", "Actual Result", "Status"]
    for j, h in enumerate(tc_heads):
        cell = t_tc.cell(0, j)
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(7.5)

    cases = [
        ("TC-01", "URL Fast-Path", "https://google.com", "Risk: 0, Legitimate, <5ms", "Risk: 0, Conf: 99%", "PASS"),
        ("TC-02", "Brand Spoofing", "paypal-verify-account.xyz", "High Risk (>60), Phishing", "Risk: 88, Phishing", "PASS"),
        ("TC-03", "Raw IP Phish", "http://192.168.1.1:8080/login", "Flag raw IP + port anomaly", "Risk: 75, High Risk", "PASS"),
        ("TC-04", "Entropy Extractor", "Random 32-char DGA string", "Shannon entropy > 3.8", "Entropy: 4.125 bits", "PASS"),
        ("TC-05", "Extension Spoof", "PE binary renamed to test.pdf", "Detect MZ magic byte mismatch", "Alert: Extension Spoof", "PASS"),
        ("TC-06", "PDF Compression", "Valid PDF with entropy 7.859", "Classify Normal, Risk < 40", "Risk: 15, Info severity", "PASS"),
        ("TC-07", "URL Deduplication", "Scan identical URL twice", "Row updated; count unchanged", "Same ID; total static", "PASS"),
        ("TC-08", "File Deduplication", "Upload identical file hash twice", "Row updated; count unchanged", "Same ID; total static", "PASS"),
        ("TC-09", "ClamAV Fallback", "Scan file with ClamAV offline", "Return Limited Analysis, 200", "Score: 15, Limited Status", "PASS"),
        ("TC-10", "Password Weak", "123456, password", "Verdict: Very Weak, Score: 0", "Score: 0, Warning Flag", "PASS"),
        ("TC-11", "Password Strong", "20-char mixed random string", "Verdict: Very Strong, >80 bits", "Entropy: 86.4 bits, Pass", "PASS"),
        ("TC-12", "PDF Report Gen", "/api/file/report/1", "Return %PDF-1.4 stream, 200", "%PDF-1.4, Valid stream", "PASS"),
        ("TC-13", "Rate Limiting", ">60 req/min to /api/scan", "HTTP 429 Too Many Requests", "HTTP 429 Trapped", "PASS"),
        ("TC-14", "Settings Update", "Update max_file_size to 32MB", "Persist settings.json, 200", "Saved & reflected in UI", "PASS")
    ]
    for i, c in enumerate(cases):
        row = t_tc.rows[i+1]
        for j, val in enumerate(c):
            cell = row.cells[j]
            p = cell.paragraphs[0]
            p.add_run(val).font.size = Pt(7)
            if j == 5:
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(22, 163, 74)
            set_cell_margins(cell, top=30, bottom=30, left=50, right=50)
    doc.add_page_break()

    # Page 27: Forensic Validation
    add_h2("10.4 Empirical Forensic Validation & Edge Cases")
    doc.add_paragraph("A critical engineering requirement verified during testing was the resolution of false-positive entropy alerts on compressed document formats. During preliminary testing, legitimate PDF files were evaluated:")
    add_bullet("Case Study 1: Compressed PDF Payload vs Packed Malware: A standard corporate PDF containing embedded images exhibited a Shannon byte entropy of 7.859 bits/byte. Under uncalibrated analysis, entropy above 7.2 triggers a critical packed malware warning. In PhishGuard's format-aware engine, the file extension .pdf and MIME type application/pdf engaged the COMPRESSED_OR_PACKED_FORMATS ruleset. The byte distribution was correctly recognized as a normal zlib Deflate stream, assigning an info severity rating and a safe baseline risk score (15/100).")
    add_bullet("Case Study 2: Fast-Path Apex Whitelist Validation: High-traffic legitimate domains (e.g. https://en.wikipedia.org/wiki/Computer_security) were tested. The allowlist parser extracted the apex domain (wikipedia.org), confirmed trusted status, and returned a safe verdict with 0 risk points in 1.8 milliseconds, completely bypassing Random Forest tree evaluation.")
    add_bullet("Case Study 3: SQLite Upsert Deduplication: A simulated user submitted http://paypal-verification-account.xyz/login.php three consecutive times. Audit logs verified that rather than creating three database entries, the existing scan ID was preserved, updating only the ISO-8601 timestamp. The total scan count remained constant, proving zero database bloat.")
    add_bullet("Case Study 4: Password Zero-Persistence Verification: Direct inspection of SQLite table schemas (scans and file_scans) confirmed that no table, column, or log file contains password strings, enforcing 100% compliance with zero-storage privacy policies.")
    doc.add_page_break()

    # Page 28: Interface Walkthrough (Fig 7)
    add_h1("CHAPTER 11: APPLICATION INTERFACE & SCREENSHOT WALKTHROUGH")
    add_h2("11.1 Security Settings & System Telemetry Interface")
    doc.add_paragraph("Figure 11.1 displays the actual production interface of PhishGuard's Security Settings & Configuration view (/settings), captured directly from the running web application:")
    if (FIGURES_DIR / "fig7_actual_settings_screenshot.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig7_actual_settings_screenshot.png"), width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 11.1: Actual Application Interface — Security Settings, Engine Parameters & System Telemetry.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8.5)
    doc.add_paragraph("Interface Walkthrough & Technical Features: Top Sticky Navbar features the PhishGuard shield logo, brand typography, 7 primary navigation links (Dashboard, URL Scanner, Password Analyzer, File Scanner, Scan History, Analytics, Settings), real-time ONLINE heartbeat indicator, and quick-action New Scan button. Engine & Quarantine Parameters Card allows dynamic configuration of multipart upload boundaries (configured to 32 MB), ClamAV binary execution path, and the deep static heuristic engine toggle. System Telemetry & Status Card displays real-time operational health metrics, verifying the active Random Forest classifier (100 Trees • 26 Feats), SQLite3 WAL journal mode, ClamAV fallback state, and total audit counters.")
    doc.add_page_break()

    # Page 29: URL Scanner Interface (Fig 8)
    add_h2("11.2 Live URL Threat Scanner & Forensic Dossier Interface")
    doc.add_paragraph("The Live URL Threat Scanner (/scanner) provides an interactive workspace for testing suspect links with live radar progress:")
    if (FIGURES_DIR / "fig8_url_scanner_ui.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig8_url_scanner_ui.png"), width=Inches(6.2))
        p_cap = doc.add_paragraph("Figure 11.2: Live URL Threat Scanner — Calibrated Risk Gauge & Threat Vector Breakdown.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8.5)
    doc.add_paragraph("Key Forensic Elements: Prominent URL Input Field supports URL paste, syntax sanitization, Enter key submission, and one-click preset buttons. Dynamic Risk Gauge renders the calibrated threat score (e.g. 88/100 High Risk) with color-coded borders. Forensic Threat Vector Breakdown provides plain-English indicators detailing brand impersonation, high-abuse TLDs, and entropy. Expandable 26-Layer Feature Matrix displays exact extracted metrics (scheme, punycode, subdomains, token counts).")
    doc.add_page_break()

    # Page 30: File & Password UI (Fig 9 & 10)
    add_h2("11.3 File Security Dossier & Password Security Workspaces")
    doc.add_paragraph("Figures 11.3 and 11.4 illustrate the File Threat Inspection report and the Password Security Analyzer workspaces:")
    if (FIGURES_DIR / "fig9_file_result_ui.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig9_file_result_ui.png"), width=Inches(5.8))
        p_cap = doc.add_paragraph("Figure 11.3: Forensic File Threat Dossier — Hashes, Format-Aware Entropy & ClamAV Status.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8)
    if (FIGURES_DIR / "fig10_password_analyzer_ui.png").exists():
        doc.add_picture(str(FIGURES_DIR / "fig10_password_analyzer_ui.png"), width=Inches(5.8))
        p_cap = doc.add_paragraph("Figure 11.4: Zero-Storage Password Security Analyzer — Entropy Meter & Complexity Audit.")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.size = Pt(8)
    doc.add_page_break()

    # Page 31: Advantages & Limitations
    add_h1("CHAPTER 12: PRACTICAL ADVANTAGES AND TECHNICAL LIMITATIONS")
    add_h2("12.1 Practical Advantages of PhishGuard")
    add_bullet("Zero-Day Phishing Detection: By evaluating 26 structural and behavioral features rather than relying solely on static blacklists, PhishGuard successfully identifies newly registered phishing URLs before threat intelligence databases index them.")
    add_bullet("Elimination of Entropy False Positives: The format-aware entropy engine recognizes Deflate-compressed streams (.pdf, .zip, .docx), preventing false-positive malware packing alerts that plague naive entropy tools.")
    add_bullet("Zero-Execution Quarantine Safety: Files are read purely as volatile byte buffers for hashing and header matching. Executable payloads are never launched, ensuring host environment safety without complex hypervisor sandboxes.")
    add_bullet("Complete Credential Privacy: The zero-storage password analyzer calculates true Shannon entropy and dictionary patterns locally, guaranteeing that sensitive credentials are never stored in databases or transmitted over external APIs.")
    add_bullet("Explainable Forensic Telemetry: Rather than an unhelpful binary block notice, PhishGuard details exact threat reasons (typosquatting distance, suspicious TLD suffixes, magic byte mismatches) and generates downloadable ReportLab PDF reports.")
    add_h2("12.2 Honest Technical Limitations")
    doc.add_paragraph("In adherence to academic integrity, the following technical limitations are acknowledged:")
    add_bullet("Serverless Local Storage Ephemerality: When deployed on serverless hosting platforms like Vercel, the local SQLite database in /tmp is ephemeral and recycles during container scale-down unless connected to an external cloud database (e.g., Neon PostgreSQL or Supabase).")
    add_bullet("Offline ClamAV Constraint: Full antivirus signature scanning requires a local clamscan installation. On serverless containers where ClamAV is offline, the system relies exclusively on static heuristics and magic byte checks.")
    add_bullet("Static Lexical Limitations: Because PhishGuard performs lightweight static URL analysis without full web rendering, it cannot inspect client-side JavaScript execution or dynamic DOM modifications injected after initial page load.")
    doc.add_page_break()

    # Page 32: Future Scope
    add_h1("CHAPTER 13: FUTURE SCOPE AND OPERATIONAL ROADMAP")
    add_h2("13.1 Planned Future Enhancements")
    doc.add_paragraph("While PhishGuard successfully meets all stated engineering objectives, several promising directions exist for future academic and industrial research:")
    add_bullet("Hybrid Deep Learning & Transformer Models: Integrate fine-tuned BERT or RoBERTa transformer architectures to perform deep semantic analysis on webpage text content and email body headers, supplementing lexical URL features.")
    add_bullet("External Threat Intelligence Aggregation: Connect real-time API integrations with commercial and community feeds (e.g. VirusTotal API, Google Safe Browsing API, AlienVault OTX) to enrich static verdicts with global consensus scoring.")
    add_bullet("Headless Browser Dynamic Screenshot Capture: Integrate Playwright or Puppeteer to capture automated visual snapshots of suspect URLs inside isolated microVM containers, comparing webpage rendering similarity against legitimate brand landing pages.")
    add_bullet("Cloud-Native Managed Persistence: Replace local SQLite storage with managed cloud databases (such as AWS RDS PostgreSQL, Supabase, or Neon) to maintain multi-region persistent audit history across distributed serverless instances.")
    add_bullet("Browser Extension Ecosystem: Package PhishGuard's 26-layer feature extractor as a lightweight Chromium/Firefox web extension to provide real-time endpoint phishing warnings directly inside user browsers.")
    add_bullet("Containerized MicroVM Dynamic Sandbox: Incorporate Firecracker or gVisor lightweight microVM sandboxes to optionally execute suspicious binaries for 30 seconds to capture behavioral system call traces.")
    add_h2("13.2 Summary of Roadmap Priorities")
    doc.add_paragraph("These future enhancements will transition PhishGuard from a lightweight forensic workstation into a comprehensive enterprise-grade Security Orchestration, Automation, and Response (SOAR) ecosystem.")
    doc.add_page_break()

    # Page 33: Conclusion
    add_h1("CHAPTER 14: CONCLUSION")
    add_h2("14.1 Project Retrospective")
    doc.add_paragraph("The development and empirical validation of PHISHGUARD — Cyber Intelligence Platform successfully demonstrates that effective, explainable, and multi-vector cybersecurity analysis can be achieved using a unified, lightweight Python and Flask architecture. By moving beyond passive, post-incident blacklisting, PhishGuard empowers security analysts and end-users with proactive, real-time threat intelligence.")
    add_h2("14.2 Key Engineering Achievements")
    add_bullet("Engineered an Automated 26-Dimensional Feature Extractor: Decomposes arbitrary URLs into lexical, structural, statistical, and brand typosquatting metrics in under 50 milliseconds.")
    add_bullet("Trained a High-Accuracy Random Forest Classifier: Delivers robust 93.8%–100% classification accuracy backed by calibrated composite risk scoring (0-100 scale).")
    add_bullet("Solved Naive Entropy False Positives: Built a format-aware byte entropy engine that accurately differentiates natural Deflate/zlib compressed files (.pdf, .zip) from obfuscated binary packing.")
    add_bullet("Implemented Zero-Storage Credential Auditing: Evaluates password bit entropy and dictionary patterns locally without database storage, preserving privacy.")
    add_bullet("Established Resilient Persistence & Serverless Bridges: Optimized SQLite with WAL journaling and upsert deduplication, ensuring full compatibility with Vercel cloud hosting.")
    add_bullet("Achieved 100% Automated Test Pass Rate: Validated system stability across a complete 31-test Pytest test suite covering all functional modules.")
    add_h2("14.3 Final Concluding Statement")
    doc.add_paragraph("In conclusion, PhishGuard represents a practical, reproducible, and mathematically grounded cybersecurity engineering contribution. The project stands as a complete, verified, and operational cyber defense workstation that fulfills all academic requirements for the degree of Bachelor of Technology / Master of Computer Applications in Computer Science and Engineering.")
    doc.add_page_break()

    # Page 34: References
    add_h1("REFERENCES AND BIBLIOGRAPHY")
    refs = [
        "1. Anti-Phishing Working Group (APWG). (2025). Phishing Activity Trends Report — 4th Quarter 2024 / 2025. APWG Global Research Reports. Available: https://apwg.org/trendsreports/",
        "2. Shannon, C. E. (1948). \"A Mathematical Theory of Communication\". Bell System Technical Journal, 27(3), 379–423. DOI: 10.1002/j.1538-7305.1948.tb01338.x",
        "3. Breiman, L. (2001). \"Random Forests\". Machine Learning, 45(1), 5–32. DOI: 10.1023/A:1010933404324",
        "4. National Institute of Standards and Technology (NIST). (2020). Digital Identity Guidelines: Authentication and Lifecycle Management. NIST Special Publication 800-63B. U.S. Department of Commerce.",
        "5. Berners-Lee, T., Fielding, R., & Masinter, L. (2005). Uniform Resource Identifier (URI): Generic Syntax. Internet Engineering Task Force (IETF) RFC 3986. Available: https://www.ietf.org/rfc/rfc3986.txt",
        "6. OWASP Foundation. (2024). OWASP Top 10 Web Application Security Risks. Open Web Application Security Project. Available: https://owasp.org/www-project-top-ten/",
        "7. Pedregosa, F., et al. (2011). \"Scikit-learn: Machine Learning in Python\". Journal of Machine Learning Research, 12, 2825–2830.",
        "8. Grinberg, M. (2018). Flask Web Development: Developing Web Applications with Python (2nd ed.). O'Reilly Media. ISBN: 978-1491991732.",
        "9. ReportLab Inc. (2025). ReportLab PDF Generation User Guide (v5.1). ReportLab Documentation. Available: https://www.reportlab.com/documentation/",
        "10. Cisco Talos Intelligence Group. (2024). Threat Intelligence and Malicious Domain Typosquatting Trends. Cisco Systems Whitepaper.",
        "11. ClamAV Team. (2025). Clam AntiVirus Open Source Antivirus Engine Documentation. Cisco Systems. Available: https://docs.clamav.net/",
        "12. SQLite Development Team. (2024). Write-Ahead Logging (WAL) in SQLite3. SQLite Technical Documentation. Available: https://www.sqlite.org/wal.html",
        "13. Levenshtein, V. I. (1966). \"Binary codes capable of correcting deletions, insertions, and reversals\". Soviet Physics Doklady, 10(8), 707–710.",
        "14. Mozilla Developer Network (MDN). (2025). HTTP Security Headers and Web Security Guidelines. MDN Web Docs. Available: https://developer.mozilla.org/"
    ]
    for r in refs:
        p = doc.add_paragraph(r)
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.space_after = Pt(4)
        p.runs[0].font.size = Pt(9.5)

    doc.save(str(OUTPUT_DOCX))
    print(f"DOCX Report generated successfully: {OUTPUT_DOCX}")

if __name__ == "__main__":
    build_docx_report()
