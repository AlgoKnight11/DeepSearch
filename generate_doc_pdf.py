import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 752, "DEEPSEARCH")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(120, 752, "|  Biological rPPG Deepfake Detection System Specification")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(54, 744, 558, 744)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(54, 46, 558, 46)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1E3A8A"))
        self.drawString(54, 34, "DEEPSEARCH FORENSICS")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(165, 34, "•  Confidential Architecture Specification")
        self.drawRightString(558, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    PRIMARY = colors.HexColor("#0F172A")    # Deep Slate
    SECONDARY = colors.HexColor("#1E3A8A")  # Royal/Navy Blue
    ACCENT_CYAN = colors.HexColor("#0284C7")# Sky Tech Blue
    TEXT_DARK = colors.HexColor("#1E293B")  # Charcoal Body
    BG_LIGHT = colors.HexColor("#F8FAFC")   # Light Table Alternate
    BORDER_COLOR = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=PRIMARY,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=ACCENT_CYAN,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=PRIMARY,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.5,
        textColor=TEXT_DARK,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=TEXT_DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=PRIMARY
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=9.8,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=TEXT_DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=PRIMARY
    )

    story = []

    # =========================================================================
    # PAGE 1: EXECUTIVE SUMMARY, CORE BIOLOGICAL RATIONALE & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("DEEPSEARCH: BIOLOGICAL DEEPFAKE RECOGNITION", title_style))
    story.append(Paragraph("Software Specification: Architecture, UI/UX Design System, Tech Stack & Roadmap", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceBefore=0, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Project:</b> DeepSearch Forensics", table_cell_style),
            Paragraph("<b>Domain:</b> Synthetic Media Verification", table_cell_style),
            Paragraph("<b>Status:</b> Architecture Blueprint Approved", table_cell_style)
        ],
        [
            Paragraph("<b>Methodology:</b> Multi-ROI rPPG + Coherence", table_cell_style),
            Paragraph("<b>UI Style:</b> Dark Cyber Security Dashboard", table_cell_style),
            Paragraph("<b>Interface:</b> Streamlit 1.64+ / Fast Dashboard", table_cell_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[168, 168, 168])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Executive Summary & Theoretical Grounding", h1_style))
    story.append(Paragraph(
        "<b>The Problem:</b> Deepfake synthesis engines (Diffusion pipelines, StyleGAN variants, Latent FaceSwappers) "
        "have evolved beyond traditional visual detection methods. Micro-artifacts like boundary blending, warp shadows, "
        "and unnatural blinking can now be synthesized seamlessly. Forensics must shift from visual inspection to <b>involuntary human physiology</b>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Solution:</b> DeepSearch implements <b>Remote Photoplethysmography (rPPG)</b> to read the human cardiac pulse directly from facial skin "
        "sub-surface light reflectance. While generative networks create visually convincing skin textures, they do not simulate synchronous cardiac dynamics. "
        "Authentic faces exhibit phase-locked pulse waves uniformly across biological regions. Deepfakes generate either flat noise, erratic frequencies, "
        "or region-to-region phase anomalies.",
        body_style
    ))

    callout_data = [[
        Paragraph(
            "<b>Fundamental Principle:</b> High-quality face-swaps can leak the underlying actor's pulse into portions of the frame. "
            "Detecting a heart rate in a single spot is no longer proof of authenticity. DeepSearch relies on <b>multi-patch spatio-temporal coherence</b>: "
            "authentic faces pulse in harmony across all anatomical regions; synthetic faces do not.", callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. System Architecture & Processing Pipeline", h1_style))
    story.append(Paragraph(
        "The system processes video through five sequential pipeline modules without requiring GPU-heavy inference during runtime:",
        body_style
    ))

    pipe_table_data = [
        [Paragraph("Stage", table_header_style), Paragraph("Module Name", table_header_style), Paragraph("Algorithmic Function & Technical Execution", table_header_style)],
        [
            Paragraph("Stage 1", table_cell_bold),
            Paragraph("Video Decoding & 3D Landmark Tracking", table_cell_style),
            Paragraph("Decodes frames at native FPS with OpenCV. MediaPipe Face Landmarker tracks 478 3D landmarks, stabilizing facial regions against translation, tilt, and rigid motion.", table_cell_style)
        ],
        [
            Paragraph("Stage 2", table_cell_bold),
            Paragraph("Spatial ROI Extraction & Pooling", table_cell_style),
            Paragraph("Isolates 4–6 anatomical skin patches (Forehead, Left Cheek, Right Cheek, Chin, Nose Bridge). Computes per-frame spatial mean RGB intensity vectors.", table_cell_style)
        ],
        [
            Paragraph("Stage 3", table_cell_bold),
            Paragraph("Physiological Signal Conditioning", table_cell_style),
            Paragraph("Linear detrending removes slow illumination drifts. 4th-order Butterworth bandpass filter (0.7–3.0 Hz, 42–180 BPM) isolates cardiac frequencies; applies CHROM/POS color difference algorithms.", table_cell_style)
        ],
        [
            Paragraph("Stage 4", table_cell_bold),
            Paragraph("Cross-Patch Coherence Analysis", table_cell_style),
            Paragraph("Partitions signal into 5–10s windows. Computes Magnitude-Squared Coherence matrices (`scipy.signal.coherence`), cross-correlation lags, and Spectral SNR ratios across ROI pairs.", table_cell_style)
        ],
        [
            Paragraph("Stage 5", table_cell_bold),
            Paragraph("Classification & Temporal Voting", table_cell_style),
            Paragraph("Window feature vectors are classified by a trained model (SVM / Random Forest). Aggregates window predictions via majority voting into an explainable authenticity score.", table_cell_style)
        ]
    ]
    pipe_table = Table(pipe_table_data, colWidths=[48, 128, 328])
    pipe_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(pipe_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: USER INTERFACE (UI/UX) SPECIFICATION & COLOR PALETTE SYSTEM
    # =========================================================================
    story.append(Paragraph("3. User Interface (UI/UX) Specification & Design System", h1_style))
    story.append(Paragraph(
        "DeepSearch adopts a <b>Dark • Futuristic • Cyber Security Dashboard</b> design system. "
        "The interface is optimized for high-contrast forensic telemetry, deep-navy glare reduction, and instant diagnostic readability.",
        body_style
    ))

    story.append(Paragraph("3.1 Core Color Palette & Visual Token System", h2_style))

    color_table_data = [
        [Paragraph("Category", table_header_style), Paragraph("Token Name", table_header_style), Paragraph("Hex Code", table_header_style), Paragraph("RGB Values", table_header_style), Paragraph("UI / Application Context in DeepSearch", table_header_style)],
        # Primary Colors
        [Paragraph("Primary", table_cell_bold), Paragraph("Dark Navy (Background)", table_cell_style), Paragraph("#0A0E17", table_cell_bold), Paragraph("10, 14, 23", table_cell_style), Paragraph("Main application canvas; glare-free deep forensic backdrop.", table_cell_style)],
        [Paragraph("Primary", table_cell_bold), Paragraph("Deep Slate (Surface)", table_cell_style), Paragraph("#161F30", table_cell_bold), Paragraph("22, 31, 48", table_cell_style), Paragraph("Dashboard panels, navigation bar, and primary module wrappers.", table_cell_style)],
        [Paragraph("Primary", table_cell_bold), Paragraph("Card Surface", table_cell_style), Paragraph("#1E2A40", table_cell_bold), Paragraph("30, 42, 64", table_cell_style), Paragraph("Elevated inspection cards, video container, and telemetry widgets.", table_cell_style)],
        [Paragraph("Primary", table_cell_bold), Paragraph("Border / Divider", table_cell_style), Paragraph("#2D3748", table_cell_bold), Paragraph("45, 55, 72", table_cell_style), Paragraph("Card borders (10% opacity default), subtle timeline gridlines.", table_cell_style)],
        [Paragraph("Primary", table_cell_bold), Paragraph("Primary Cyan", table_cell_style), Paragraph("#00F0FF", table_cell_bold), Paragraph("0, 240, 255", table_cell_style), Paragraph("Primary CTA buttons, active focus states, live rPPG pulse waveforms.", table_cell_style)],
        [Paragraph("Primary", table_cell_bold), Paragraph("Secondary Blue", table_cell_style), Paragraph("#3B82F6", table_cell_bold), Paragraph("59, 130, 246", table_cell_style), Paragraph("Secondary action buttons, info badges, and gradient terminal stops.", table_cell_style)],
        # Accent & Status Colors
        [Paragraph("Status / Accent", table_cell_bold), Paragraph("Neon Indigo", table_cell_style), Paragraph("#6366F1", table_cell_bold), Paragraph("99, 102, 241", table_cell_style), Paragraph("3D Face Mesh wireframes, cross-ROI coherence matrix cells.", table_cell_style)],
        [Paragraph("Status / Accent", table_cell_bold), Paragraph("Vibrant Emerald (Normal)", table_cell_style), Paragraph("#10B981", table_cell_bold), Paragraph("16, 185, 129", table_cell_style), Paragraph("'AUTHENTIC / REAL' badge, verified cardiac rhythm status, success text.", table_cell_style)],
        [Paragraph("Status / Accent", table_cell_bold), Paragraph("Warning Amber (Warning)", table_cell_style), Paragraph("#F59E0B", table_cell_bold), Paragraph("245, 158, 11", table_cell_style), Paragraph("'INCONCLUSIVE / LOW SNR' alert, heavy motion warning indicator.", table_cell_style)],
        [Paragraph("Status / Accent", table_cell_bold), Paragraph("Alert Crimson (Critical)", table_cell_style), Paragraph("#EF4444", table_cell_bold), Paragraph("239, 68, 68", table_cell_style), Paragraph("'DEEPFAKE DETECTED' alert banner, erratic frequency warning.", table_cell_style)],
        [Paragraph("Status / Accent", table_cell_bold), Paragraph("Pure Light", table_cell_style), Paragraph("#F8FAFC", table_cell_bold), Paragraph("248, 250, 252", table_cell_style), Paragraph("Primary text, numeric telemetry metrics, authenticity probability gauge.", table_cell_style)],
        [Paragraph("Status / Accent", table_cell_bold), Paragraph("Info Blue", table_cell_style), Paragraph("#3B82F6", table_cell_bold), Paragraph("59, 130, 246", table_cell_style), Paragraph("Information pills, metadata tooltips, documentation links.", table_cell_style)],
        # Text & Typography Tokens
        [Paragraph("Typography", table_cell_bold), Paragraph("Secondary Text", table_cell_style), Paragraph("#94A3B8", table_cell_bold), Paragraph("148, 163, 184", table_cell_style), Paragraph("Subheadings, chart axis labels, secondary telemetry readouts.", table_cell_style)],
        [Paragraph("Typography", table_cell_bold), Paragraph("Muted Text", table_cell_style), Paragraph("#64748B", table_cell_bold), Paragraph("100, 116, 139", table_cell_style), Paragraph("Timestamps, video hash strings, inactive tab labels.", table_cell_style)],
        [Paragraph("Typography", table_cell_bold), Paragraph("Disabled Text", table_cell_style), Paragraph("#475569", table_cell_bold), Paragraph("71, 85, 105", table_cell_style), Paragraph("Disabled button labels, placeholder inputs.", table_cell_style)],
    ]
    color_table = Table(color_table_data, colWidths=[70, 110, 52, 62, 210])
    color_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(color_table)
    story.append(Spacer(1, 5))

    story.append(Paragraph("3.2 Multi-Series Signal Visualization & Visual Effects System", h2_style))
    story.append(Paragraph(
        "• <b>Chart / Signal Series Mapping:</b> Series 1: Primary Cyan (`#00F0FF`) = Forehead rPPG; Series 2: Neon Indigo (`#6366F1`) = Left Cheek rPPG; Series 3: Vibrant Emerald (`#10B981`) = Right Cheek rPPG; Series 4: Warning Amber (`#F59E0B`) = Chin rPPG; Series 5: Alert Crimson (`#EF4444`) = Spectral Noise Floor / Coherence Anomaly threshold; Series 6: Slate (`#94A3B8`) = Baseline trend.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Gradients & Glows:</b> Primary Header / Meter: Cyan → Blue (`#00F0FF` → `#3B82F6`); Coherence Range: Emerald → Cyan (`#10B981` → `#00F0FF`); Active ROI Border Focus: `#00F0FF` (60% opacity); Neon Glow: `#00F0FF` (30% blur); Modal Backdrop: `rgba(10, 14, 23, 0.8)`; Card Hover: `rgba(0, 240, 255, 0.1)`.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Typography Hierarchy:</b> Font: Inter / Poppins (clean, modern sans-serif). Heading 1: 24px Semibold; Heading 2: 18px Semibold; Body Text: 14px Regular; Caption / Telemetry: 12px Regular.",
        bullet_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.3 Dashboard Screen Layout", h2_style))
    story.append(Paragraph(
        "• <b>Panel A (Video Inspector):</b> Video scrubber (`#0A0E17`), 3D face mesh overlay (`#6366F1`), and color-coded ROI boxes for Forehead, Cheeks, and Chin.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Panel B (Signal Workbench):</b> Multi-channel rPPG waveform traces (Cyan, Indigo, Emerald) synchronized with interactive FFT Power Spectral Density (BPM readout).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Panel C (Forensic Verdict):</b> Authenticity probability gauge (Cyan/Emerald for Real, Crimson for Fake), biological coherence heatmap, and 'Export Forensic PDF' CTA.",
        bullet_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TECH STACK, ROADMAP & FAILURE MITIGATION
    # =========================================================================
    story.append(Paragraph("4. Recommended Technology Stack", h1_style))

    tech_table_data = [
        [Paragraph("System Layer", table_header_style), Paragraph("Selected Technology", table_header_style), Paragraph("Architectural Rationale & Responsibility", table_header_style)],
        [
            Paragraph("Computer Vision", table_cell_bold),
            Paragraph("OpenCV 4.14+<br/>MediaPipe Face Mesh", table_cell_style),
            Paragraph("Sub-millisecond frame decoding; 478 3D landmarks tracked at 30+ FPS on CPU without requiring heavy CUDA acceleration.", table_cell_style)
        ],
        [
            Paragraph("Signal Processing", table_cell_bold),
            Paragraph("SciPy 1.18+<br/>NumPy 2.5+", table_cell_style),
            Paragraph("Digital Butterworth filtering (`butter`, `sosfiltfilt`), baseline linear detrending, cross-correlation, and FFT spectral estimation (`numpy.fft.rfft`).", table_cell_style)
        ],
        [
            Paragraph("Machine Learning", table_cell_bold),
            Paragraph("Scikit-Learn 1.9+<br/>PyTorch 2.14+", table_cell_style),
            Paragraph("Trains tabular classifiers (SVM with RBF kernel, Random Forest) on multi-ROI coherence vectors; enforces leak-free `GroupKFold` cross-validation.", table_cell_style)
        ],
        [
            Paragraph("Frontend Dashboard", table_cell_bold),
            Paragraph("Streamlit 1.64+<br/>Plotly 7.1+", table_cell_style),
            Paragraph("Interactive browser application implementing the Cyber Security dark palette, responsive cards, and dynamic 60 FPS multi-trace waveform plots.", table_cell_style)
        ],
        [
            Paragraph("Forensic Certificate", table_cell_bold),
            Paragraph("ReportLab 5.0+<br/>Pillow 12.3+", table_cell_style),
            Paragraph("Automated export of cryptographically hashed, timestamped forensic audit certificates containing landmark snapshots and signal spectrum plots.", table_cell_style)
        ]
    ]
    tech_table = Table(tech_table_data, colWidths=[80, 115, 309])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. Phased Engineering Roadmap & Milestones", h1_style))

    phase_data = [
        [Paragraph("Phase", table_header_style), Paragraph("Objective & Scope", table_header_style), Paragraph("Concrete Deliverables & Acceptance Criteria", table_header_style)],
        [
            Paragraph("Phase 1<br/><b>Baseline Pulse PoC</b>", table_cell_bold),
            Paragraph("Single-ROI rPPG extraction from video or live webcam stream.", table_cell_style),
            Paragraph("• Ingestion pipeline extracts frames at precise native FPS from camera/file.<br/>• MediaPipe tracks forehead landmark cluster and extracts stable bounding box.<br/>• Detrending + 4th-order Butterworth bandpass (0.7–3.0 Hz).<br/>• FFT frequency peak verifies heart rate within ±4 BPM of ground truth pulse oximeter.", table_cell_style)
        ],
        [
            Paragraph("Phase 2<br/><b>Multi-ROI Coherence Engine</b>", table_cell_bold),
            Paragraph("Simultaneous multi-patch tracking and cross-region synchronization.", table_cell_style),
            Paragraph("• Extract 4–6 anatomical patches (Forehead, L-Cheek, R-Cheek, Chin).<br/>• Implement CHROM (Chrominance-based) and POS (Plane-Orthogonal-to-Skin) rPPG algorithms to withstand motion.<br/>• Compute pairwise Magnitude-Squared Coherence matrices (`scipy.signal.coherence`).<br/>• Interactive visualization of multi-patch synchronized pulse traces in UI.", table_cell_style)
        ],
        [
            Paragraph("Phase 3<br/><b>Dataset Ingestion & Benchmarking</b>", table_cell_bold),
            Paragraph("Curate authentic reference videos and deepfake pairs.", table_cell_style),
            Paragraph("• Ingest UBFC-rPPG benchmark (authentic subjects with synchronized contact-PPG sensor readings).<br/>• Curate FaceForensics++ / DeepFaceLab real and synthetic video pairs.<br/>• Implement strict `GroupKFold` cross-validation partitioning (subject-isolated splitting to prevent face memorization).", table_cell_style)
        ],
        [
            Paragraph("Phase 4<br/><b>Classifier & Temporal Aggregation</b>", table_cell_bold),
            Paragraph("Train tabular classifier to separate authentic biology from noise.", table_cell_style),
            Paragraph("• Extract window-level feature vectors: Coherence Mean/Std, Spectral Energy Ratios, Peak Discrepancies.<br/>• Train tabular classifier (Support Vector Machine with RBF kernel / Random Forest).<br/>• Implement temporal sliding window voting (majority rule / probabilistic aggregation across 10-second segments).", table_cell_style)
        ],
        [
            Paragraph("Phase 5<br/><b>Forensic UI & Edge-Case Hardening</b>", table_cell_bold),
            Paragraph("Build complete web dashboard and test degradation scenarios.", table_cell_style),
            Paragraph("• Build Cyber Security dark-mode Streamlit UI matching specified color palette tokens.<br/>• Stress-test with compressed videos (H.264 high vs low bitrate), head movement, and poor lighting.<br/>• Export automated forensic PDF certificate with SHA-256 video fingerprint.", table_cell_style)
        ]
    ]
    phase_table = Table(phase_data, colWidths=[70, 126, 308])
    phase_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(phase_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("6. Critical Failure Modes & Engineering Mitigations", h1_style))
    story.append(Paragraph("• <b>High Video Compression:</b> H.264/H.265 compression discards subtle micro-color variations. <i>Mitigation:</i> Incorporate temporal window confidence weighting; videos with low chrominance variance are flagged with Warning Amber (`#F59E0B`) as 'Inconclusive / Low Bitrate'.", bullet_style))
    story.append(Paragraph("• <b>Rigid Head Movement:</b> MediaPipe 3D point tracking normalizes patch alignment; windows with sudden landmark velocity spikes are automatically rejected.", bullet_style))
    story.append(Paragraph("• <b>Subject Identity Memorization:</b> Standard random splitting falsely inflates classifier accuracy because model memorizes face shapes. <i>Mitigation:</i> Strictly enforce `GroupKFold` by person ID.", bullet_style))
    story.append(Paragraph("• <b>Lighting Fluctuations:</b> Detrending + POS chrominance projection isolates specular reflections from diffuse subsurface scattering.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=3, spaceAfter=5))
    story.append(Paragraph(
        "<b>Next Phase Execution:</b> Development begins with <b>Phase 1: Video Ingestion & Baseline Heart Rate Reader PoC</b>. "
        "No machine learning or complex models are introduced until the underlying physiological pulse signal is verified against ground truth.",
        callout_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Document successfully created at: {filename}")

if __name__ == '__main__':
    target = os.path.abspath(r"d:\DeepSearch- Deepfake Recognition\DeepSearch_Deepfake_Detection_System_Specification.pdf")
    build_pdf(target)
