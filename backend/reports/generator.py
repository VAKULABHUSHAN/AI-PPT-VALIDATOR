import json
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from backend.schemas.evaluation import EvaluationResult
from backend.schemas.presentation import PresentationInfo
from backend.core.config import settings

def generate_json_report(evaluation: EvaluationResult, output_path: Path) -> Path:
    """Save full evaluation report as formatted JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evaluation.model_dump(), f, indent=2, ensure_ascii=False)
    return output_path

def generate_pdf_report(
    presentation: PresentationInfo,
    evaluation: EvaluationResult,
    output_path: Path
) -> Path:
    """Generate a high-grade professional PDF evaluation report using ReportLab."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=14
    )
    heading_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155')
    )
    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#0f172a')
    )
    score_style = ParagraphStyle(
        'ScoreBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor('#2563eb')
    )
    
    story = []
    
    # Header Banner Table
    header_data = [
        [
            Paragraph("<b>PPT VALIDATOR AI</b><br/><font size='9' color='#64748b'>Professional Presentation Quality Assurance Report</font>", title_style),
            Paragraph(f"<b>Overall Score</b><br/><font size='22' color='#2563eb'><b>{evaluation.overall_score}</b></font><font size='11' color='#64748b'>/100</font><br/><font size='9' color='#16a34a'><b>{evaluation.rating_label}</b></font>", score_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[400, 130])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))
    
    # Presentation Overview Card
    overview_data = [
        [
            Paragraph(f"<b>Document:</b> {presentation.filename}", body_style),
            Paragraph(f"<b>Slides Analyzed:</b> {presentation.slide_count}", body_style),
            Paragraph(f"<b>Mode:</b> {evaluation.mode.upper()}", body_style)
        ],
        [
            Paragraph(f"<b>Evaluation Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style),
            Paragraph(f"<b>Verdict:</b> {evaluation.rating_label}", bold_body_style),
            Paragraph(f"<b>AI Engine:</b> <font color='{'#2563eb' if 'AI' in evaluation.ai_mode_applied else '#64748b'}'><b>{evaluation.ai_mode_applied}</b></font>", body_style)
        ]
    ]
    overview_table = Table(overview_data, colWidths=[200, 160, 170])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 14))
    
    # Executive Verdict & Summary
    story.append(Paragraph("<b>1. Evaluation Summary & Verdict</b>", heading_style))
    story.append(Paragraph(f"<b>Verdict:</b> {evaluation.verdict}", bold_body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(evaluation.summary_text, body_style))
    story.append(Spacer(1, 12))
    
    # Category Scores Breakdown
    story.append(Paragraph("<b>2. Rubric Category Breakdown</b>", heading_style))
    cat_rows = [
        [
            Paragraph("<b>Evaluation Dimension</b>", bold_body_style),
            Paragraph("<b>Weight</b>", bold_body_style),
            Paragraph("<b>Score</b>", bold_body_style),
            Paragraph("<b>Weighted</b>", bold_body_style),
            Paragraph("<b>Justification & Evidence</b>", bold_body_style)
        ]
    ]
    for cs in evaluation.category_scores:
        cat_rows.append([
            Paragraph(f"<b>{cs.name}</b>", bold_body_style),
            Paragraph(f"{cs.weightage}%", body_style),
            Paragraph(f"{cs.score}/{cs.max_score}", body_style),
            Paragraph(f"<b>{cs.weighted_score}</b>", bold_body_style),
            Paragraph(f"{cs.explanation}<br/><font color='#475569'><i>Evidence: {cs.evidence}</i></font>", body_style)
        ])
    cat_table = Table(cat_rows, colWidths=[120, 45, 55, 55, 255])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 14))
    
    # Critical Issues and Action Items
    story.append(Paragraph("<b>3. Critical Issues & Key Improvements</b>", heading_style))
    if evaluation.critical_issues:
        for iss in evaluation.critical_issues:
            story.append(Paragraph(f"<font color='#dc2626'><b>[CRITICAL]</b></font> {iss}", body_style))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("No critical disqualifiers detected in presentation deck.", body_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Recommended Strategic Improvements:</b>", bold_body_style))
    for imp in evaluation.major_improvements:
        story.append(Paragraph(f"• {imp}", body_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 14))
    
    # SIH Jury Simulation Q&A
    if evaluation.jury_questions:
        story.append(Paragraph("<b>4. Jury Simulation Defense Questions & Recommended Answers</b>", heading_style))
        for idx, jq in enumerate(evaluation.jury_questions, start=1):
            q_data = [
                [Paragraph(f"<b>Q{idx} ({jq.evaluator_type} - {jq.difficulty} | Slide {jq.relevant_slide}):</b> {jq.question}", bold_body_style)],
                [Paragraph(f"<b>Why the jury asks this:</b> <font color='#475569'>{jq.reason}</font>", body_style)],
                [Paragraph(f"<b>Model Response:</b> {jq.suggested_answer}", body_style)]
            ]
            q_table = Table(q_data, colWidths=[530])
            q_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(q_table)
            story.append(Spacer(1, 6))
            
    # Slide-by-Slide Summary
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>5. Slide-by-Slide Audit Summary</b>", heading_style))
    slide_rows = [
        [
            Paragraph("<b>Slide #</b>", bold_body_style),
            Paragraph("<b>Title & Purpose</b>", bold_body_style),
            Paragraph("<b>Content</b>", bold_body_style),
            Paragraph("<b>Tech</b>", bold_body_style),
            Paragraph("<b>Visual</b>", bold_body_style),
            Paragraph("<b>Severity</b>", bold_body_style),
            Paragraph("<b>Recommendations</b>", bold_body_style)
        ]
    ]
    for sf in evaluation.slide_feedback:
        recs_str = "<br/>".join([f"• {r}" for r in sf.recommendations]) if sf.recommendations else "Meets standard."
        slide_rows.append([
            Paragraph(f"<b>Slide {sf.slide_number}</b>", bold_body_style),
            Paragraph(f"<b>{sf.slide_title}</b><br/><font color='#64748b'>{sf.purpose}</font>", body_style),
            Paragraph(f"{sf.content_score}/10", body_style),
            Paragraph(f"{sf.technical_score}/10", body_style),
            Paragraph(f"{sf.visual_score}/10", body_style),
            Paragraph(f"<font color='{'#dc2626' if sf.severity in ['Critical', 'High'] else '#2563eb'}'><b>{sf.severity}</b></font>", body_style),
            Paragraph(recs_str, body_style)
        ])
    slide_table = Table(slide_rows, colWidths=[45, 125, 45, 40, 40, 50, 185])
    slide_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(slide_table)
    
    # Build Document
    doc.build(story)
    return output_path

