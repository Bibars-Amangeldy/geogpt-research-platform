"""
ApexGIS PDF Report Generation Service
Generates beautiful environmental monitoring reports with Apex branding
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
import base64
import os

# ApexGIS Brand Colors
APEX_PRIMARY = colors.HexColor("#3B82F6")  # Blue
APEX_SECONDARY = colors.HexColor("#10B981")  # Green
APEX_ACCENT = colors.HexColor("#06B6D4")  # Cyan
APEX_WARNING = colors.HexColor("#F59E0B")  # Orange/Yellow
APEX_DANGER = colors.HexColor("#EF4444")  # Red
APEX_DARK = colors.HexColor("#1E293B")  # Dark background
APEX_GRAY = colors.HexColor("#64748B")  # Gray text


class ApexReportGenerator:
    """Generates beautiful PDF reports for ApexGIS platform"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom ApexGIS styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ApexTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=APEX_PRIMARY,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ApexSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=APEX_GRAY,
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='ApexSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=APEX_DARK,
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=(5, 5, 5, 5),
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ApexBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=APEX_DARK,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
        
        # Metric value style
        self.styles.add(ParagraphStyle(
            name='ApexMetric',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=APEX_PRIMARY,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='ApexFooter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=APEX_GRAY,
            alignment=TA_CENTER
        ))
    
    def _create_header(self, title: str) -> list:
        """Create report header with ApexGIS branding"""
        elements = []
        
        # Logo placeholder (text-based for now)
        logo_text = Drawing(200, 60)
        # Background rectangle
        logo_text.add(Rect(0, 0, 200, 60, fillColor=APEX_PRIMARY, strokeColor=None, rx=8, ry=8))
        # Globe icon (circle)
        logo_text.add(Circle(40, 30, 20, fillColor=colors.white, strokeColor=None))
        logo_text.add(Circle(40, 30, 15, fillColor=APEX_PRIMARY, strokeColor=colors.white, strokeWidth=2))
        # Text
        logo_text.add(String(70, 35, "ApexGIS", fillColor=colors.white, fontSize=20, fontName='Helvetica-Bold'))
        logo_text.add(String(70, 18, "Presidential Platform", fillColor=colors.white, fontSize=10))
        
        elements.append(logo_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Title
        elements.append(Paragraph(title, self.styles['ApexTitle']))
        
        # Subtitle with date
        date_str = datetime.now().strftime("%B %d, %Y at %H:%M")
        elements.append(Paragraph(
            f"Environmental Monitoring Report | Generated: {date_str}",
            self.styles['ApexSubtitle']
        ))
        
        # Horizontal line
        elements.append(HRFlowable(
            width="100%", 
            thickness=2, 
            color=APEX_PRIMARY,
            spaceAfter=20
        ))
        
        return elements
    
    def _create_executive_summary(self, data: dict) -> list:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("📊 Executive Summary", self.styles['ApexSection']))
        
        # Summary metrics table
        metrics_data = [
            ["Air Quality", "Methane", "CO₂ Emissions", "Active Fires"],
            [
                data.get('air_quality_status', 'Moderate'),
                f"{data.get('methane_total', 0):.1f} MT",
                f"{data.get('co2_total', 0):.1f} MT",
                str(data.get('fire_count', 0))
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), APEX_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 15),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 1, APEX_PRIMARY),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary text
        summary_text = data.get('summary', 
            "This report provides a comprehensive overview of environmental monitoring data "
            "collected from multiple sources including satellite imagery, ground sensors, and "
            "international databases. The data covers air quality indices, greenhouse gas emissions, "
            "and natural hazard monitoring for the Republic of Kazakhstan."
        )
        elements.append(Paragraph(summary_text, self.styles['ApexBody']))
        
        return elements
    
    def _create_air_quality_section(self, data: dict) -> list:
        """Create air quality section"""
        elements = []
        
        elements.append(Paragraph("🌬️ Air Quality Monitoring", self.styles['ApexSection']))
        
        air_data = data.get('air_quality', {})
        stations = air_data.get('stations', [])
        
        if stations:
            # Table header and data
            table_data = [["Station", "AQI", "Category", "PM2.5", "PM10", "Dominant"]]
            
            for station in stations[:10]:  # Limit to 10 stations
                pollutants = station.get('pollutants', {})
                pm25 = pollutants.get('pm25', {}).get('value', 'N/A')
                pm10 = pollutants.get('pm10', {}).get('value', 'N/A')
                table_data.append([
                    station.get('name', 'Unknown')[:20],
                    str(station.get('aqi', 'N/A')),
                    station.get('category', 'N/A')[:10],
                    str(pm25),
                    str(pm10),
                    station.get('dominant_pollutant', 'N/A')
                ])
            
            aq_table = Table(table_data, colWidths=[3*cm, 1.5*cm, 2.5*cm, 1.8*cm, 1.8*cm, 2.5*cm])
            aq_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), APEX_SECONDARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('BOX', (0, 0), (-1, -1), 1, APEX_SECONDARY),
                ('LINEBELOW', (0, 0), (-1, 0), 2, APEX_SECONDARY),
            ]))
            elements.append(aq_table)
        else:
            elements.append(Paragraph(
                "No air quality data available for this report.",
                self.styles['ApexBody']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_emissions_section(self, data: dict) -> list:
        """Create greenhouse gas emissions section"""
        elements = []
        
        elements.append(Paragraph("🏭 Greenhouse Gas Emissions", self.styles['ApexSection']))
        
        # Methane section
        methane_data = data.get('methane', {})
        hotspots = methane_data.get('hotspots', [])
        
        if hotspots:
            elements.append(Paragraph("<b>Methane (CH₄) Hotspots:</b>", self.styles['ApexBody']))
            
            table_data = [["Source", "Type", "Emission Rate (kt/yr)", "Concentration (ppb)", "Trend"]]
            for hs in hotspots[:8]:
                table_data.append([
                    hs.get('name', 'Unknown')[:25],
                    hs.get('type', 'N/A'),
                    f"{hs.get('emission_rate_kt_per_year', 0):.1f}",
                    f"{hs.get('concentration_ppb', 0):.0f}",
                    hs.get('trend', 'N/A')
                ])
            
            ch4_table = Table(table_data, colWidths=[4*cm, 2.5*cm, 3*cm, 3*cm, 2*cm])
            ch4_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), APEX_WARNING),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#FEF3C7")]),
                ('BOX', (0, 0), (-1, -1), 1, APEX_WARNING),
            ]))
            elements.append(ch4_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # CO2 section
        co2_data = data.get('co2', {})
        sources = co2_data.get('sources', [])
        
        if sources:
            elements.append(Paragraph("<b>CO₂ Emission Sources:</b>", self.styles['ApexBody']))
            
            table_data = [["Source", "Sector", "Annual Emissions (MT)"]]
            for src in sources[:8]:
                table_data.append([
                    src.get('name', 'Unknown')[:30],
                    src.get('sector', 'N/A'),
                    f"{src.get('annual_emissions_mt', 0):.2f}"
                ])
            
            co2_table = Table(table_data, colWidths=[5.5*cm, 4*cm, 4*cm])
            co2_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), APEX_DANGER),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#FEE2E2")]),
                ('BOX', (0, 0), (-1, -1), 1, APEX_DANGER),
            ]))
            elements.append(co2_table)
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_fire_section(self, data: dict) -> list:
        """Create active fires section"""
        elements = []
        
        elements.append(Paragraph("🔥 Active Fire Detection", self.styles['ApexSection']))
        
        fire_data = data.get('fires', {})
        fires = fire_data.get('fires', [])
        
        if fires:
            elements.append(Paragraph(
                f"<b>Total Active Fires Detected:</b> {len(fires)} | Source: NASA FIRMS",
                self.styles['ApexBody']
            ))
            
            table_data = [["Location", "Brightness (K)", "Confidence", "Satellite", "Time"]]
            for fire in fires[:10]:
                coords = fire.get('coordinates', [0, 0])
                table_data.append([
                    f"{coords[1]:.2f}°N, {coords[0]:.2f}°E",
                    f"{fire.get('brightness', 0):.0f}",
                    fire.get('confidence', 'N/A'),
                    fire.get('satellite', 'N/A'),
                    fire.get('acq_time', 'N/A')
                ])
            
            fire_table = Table(table_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
            fire_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#DC2626")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#FEF2F2")]),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#DC2626")),
            ]))
            elements.append(fire_table)
        else:
            elements.append(Paragraph(
                "✅ No active fires detected in the monitoring area.",
                self.styles['ApexBody']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_footer(self) -> list:
        """Create report footer"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(HRFlowable(width="100%", thickness=1, color=APEX_GRAY, spaceAfter=10))
        
        footer_text = (
            "This report was generated by ApexGIS Presidential Environmental Monitoring Platform. "
            "Data sources include OpenAQ, NASA FIRMS, Sentinel-5P, ERA5, and USGS. "
            "© 2024 ApexGIS - Republic of Kazakhstan"
        )
        elements.append(Paragraph(footer_text, self.styles['ApexFooter']))
        
        return elements
    
    def generate_report(self, data: dict, title: str = "Environmental Monitoring Report") -> bytes:
        """Generate complete PDF report"""
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        elements = []
        
        # Build report sections
        elements.extend(self._create_header(title))
        elements.extend(self._create_executive_summary(data))
        elements.extend(self._create_air_quality_section(data))
        elements.extend(self._create_emissions_section(data))
        elements.extend(self._create_fire_section(data))
        elements.extend(self._create_footer())
        
        # Build PDF
        doc.build(elements)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes


# Singleton instance
report_generator = ApexReportGenerator()
