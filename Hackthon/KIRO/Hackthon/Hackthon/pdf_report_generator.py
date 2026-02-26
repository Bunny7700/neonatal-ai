"""
PDF Report Generator for Neonatal Cry Detection
Creates professional medical-style reports from cry detection data
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from io import BytesIO
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryReportPDFGenerator:
    """Generator for creating PDF reports from cry detection data"""
    
    def __init__(self):
        """Initialize PDF generator with styling configuration"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        logger.info("PDF generator initialized")
    
    def _setup_custom_styles(self):
        """Define custom styles for medical report formatting"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=6
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def generate_report(
        self,
        cry_data: Dict[str, Any],
        ai_insights: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF report from cry detection data
        
        Args:
            cry_data: Dictionary containing all detection parameters
            ai_insights: Optional AI-generated insights from Gemini
            
        Returns:
            PDF document as bytes
        """
        try:
            logger.info("Starting PDF report generation")
            
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build document content
            story = []
            
            # Add sections
            story.extend(self._add_header())
            story.extend(self._add_summary_section(cry_data))
            story.extend(self._add_parameters_section(cry_data))
            
            if ai_insights:
                story.extend(self._add_insights_section(ai_insights))
            else:
                story.extend(self._add_insights_section(None))
            
            story.extend(self._add_footer())
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF report generated successfully ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise
    
    def _add_header(self) -> list:
        """Add report header with title and timestamp"""
        elements = []
        
        # Title
        title = Paragraph(
            "Neonatal Cry Detection Report",
            self.styles['ReportTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Generation timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_text = Paragraph(
            f"<i>Report generated on: {timestamp}</i>",
            self.styles['ReportBody']
        )
        elements.append(timestamp_text)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _add_summary_section(self, cry_data: Dict[str, Any]) -> list:
        """Add detection summary section"""
        elements = []
        
        # Section heading
        heading = Paragraph("Detection Summary", self.styles['SectionHeading'])
        elements.append(heading)
        
        # Extract data
        cry_type = cry_data.get('cry_type', 'unknown').capitalize()
        confidence = cry_data.get('confidence', 0)
        timestamp = cry_data.get('timestamp', datetime.now().timestamp())
        
        # Format timestamp
        dt = datetime.fromtimestamp(timestamp)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Confidence interpretation
        if confidence >= 80:
            confidence_level = "High confidence"
        elif confidence >= 60:
            confidence_level = "Moderate confidence"
        else:
            confidence_level = "Low confidence"
        
        # Create summary table
        summary_data = [
            ['Cry Type:', f'<b>{cry_type}</b>'],
            ['Confidence:', f'<b>{confidence:.1f}%</b> ({confidence_level})'],
            ['Detection Time:', formatted_time]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_parameters_section(self, cry_data: Dict[str, Any]) -> list:
        """Add detailed parameters section"""
        elements = []
        
        # Section heading
        heading = Paragraph("Detailed Audio Parameters", self.styles['SectionHeading'])
        elements.append(heading)
        
        # Extract features
        features = cry_data.get('features', {})
        
        # Create parameters table
        params_data = [
            ['Parameter', 'Value', 'Unit'],
            ['Pitch (Mean)', f"{features.get('pitch', 0):.1f}", 'Hz'],
            ['Pitch Variation (Std)', f"{features.get('pitch_std', 0):.1f}", 'Hz'],
            ['Intensity', f"{features.get('intensity_db', 0):.1f}", 'dB'],
            ['Spectral Centroid', f"{features.get('spectral_centroid', 0):.1f}", 'Hz'],
            ['Zero Crossing Rate', f"{features.get('zero_crossing_rate', 0):.3f}", ''],
            ['Duration', f"{features.get('duration', 0):.1f}", 'seconds']
        ]
        
        params_table = Table(params_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        params_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(params_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_insights_section(self, insights: Optional[str]) -> list:
        """Add AI-generated insights section"""
        elements = []
        
        # Section heading
        heading = Paragraph("AI-Generated Insights", self.styles['SectionHeading'])
        elements.append(heading)
        
        if insights:
            # Add insights text
            insights_para = Paragraph(insights, self.styles['ReportBody'])
            elements.append(insights_para)
        else:
            # Fallback message
            fallback_text = Paragraph(
                "<i>AI insights were unavailable at the time of report generation. "
                "The detection results above provide the core analysis of the cry pattern.</i>",
                self.styles['ReportBody']
            )
            elements.append(fallback_text)
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _add_footer(self) -> list:
        """Add report footer with disclaimers"""
        elements = []
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>Disclaimer: This report is generated by an AI-powered cry detection system. "
            "It is intended to assist caregivers and should not replace professional medical advice. "
            "Always consult with healthcare professionals for medical concerns.</i>",
            self.styles['Footer']
        )
        elements.append(disclaimer)
        
        # System info
        system_info = Paragraph(
            "Neonatal Cry Detection System v1.0",
            self.styles['Footer']
        )
        elements.append(system_info)
        
        return elements
