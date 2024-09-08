from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListItem, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import re

def create_hyperlink(url, text):
    return f'<link href="{url}">{text}</link>'

def generate_pdf(data, visualizations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    
    elements = []
    
    # Add title
    elements.append(Paragraph(data['topic'], styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Add content
    for section in data['content']:
        elements.append(Paragraph(section['title'], styles['Heading2']))
        
        # Process content
        content = section['content']
        
        # Convert numbered lists
        content = re.sub(r'\n(\d+)\.\s', lambda m: f'\n<seq id="list{m.group(1)}">{m.group(1)}.</seq> ', content)
        
        # Convert bullet points
        content = re.sub(r'\n•\s', '\n<bullet>•</bullet> ', content)
        
        # Convert references
        content = re.sub(r'\[(\d+)\]', lambda m: f'<super><link href="#ref{m.group(1)}">[{m.group(1)}]</link></super>', content)
        
        # Convert URLs
        content = re.sub(r'(https?://\S+)', lambda m: create_hyperlink(m.group(1), m.group(1)), content)
        
        elements.append(Paragraph(content, styles['Justify']))
        elements.append(Spacer(1, 12))
    
    # Add visualizations
    for viz in visualizations:
        elements.append(Image(viz, width=6*inch, height=4.5*inch))
        elements.append(Spacer(1, 12))
    
    # Add references
    elements.append(Paragraph("Referencias", styles['Heading2']))
    for i, ref in enumerate(data.get('references', []), 1):
        elements.append(Paragraph(f'<a name="ref{i}"/>[{i}] {ref}', styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
