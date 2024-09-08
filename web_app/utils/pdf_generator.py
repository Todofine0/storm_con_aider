from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListItem, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import re

def create_hyperlink(url, text):
    return f'<link href="{url}" color="blue">{text}</link>'

def generate_pdf(data, visualizations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles['Heading1'].fontSize = 16
    styles['Heading1'].spaceAfter = 12
    styles['Heading2'].fontSize = 14
    styles['Heading2'].spaceAfter = 10
    styles['Heading3'].fontSize = 12
    styles['Heading3'].spaceAfter = 8
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    
    elements = []
    
    # Add title
    elements.append(Paragraph(data['topic'], styles['Title']))
    elements.append(Spacer(1, 24))
    
    # Add content
    for section in data['content']:
        elements.append(Paragraph(section['title'], styles['Heading1']))
        
        # Process content
        content = section['content']
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            # Check if paragraph is a subsection
            if paragraph.startswith('## '):
                elements.append(Paragraph(paragraph[3:], styles['Heading2']))
            elif paragraph.startswith('### '):
                elements.append(Paragraph(paragraph[4:], styles['Heading3']))
            else:
                # Convert numbered lists
                paragraph = re.sub(r'^(\d+)\.\s', lambda m: f'<seq id="list{m.group(1)}">{m.group(1)}.</seq> ', paragraph, flags=re.MULTILINE)
                
                # Convert bullet points
                paragraph = re.sub(r'^•\s', '<bullet>•</bullet> ', paragraph, flags=re.MULTILINE)
                
                # Convert reference numbers to superscript
                paragraph = re.sub(r'\[(\d+)\]', lambda m: f'<super>{m.group(1)}</super>', paragraph)
                
                # Convert URLs to hyperlinks
                paragraph = re.sub(r'\[(.*?)\]\((https?://\S+)\)', lambda m: create_hyperlink(m.group(2), m.group(1)), paragraph)
                
                elements.append(Paragraph(paragraph, styles['Justify']))
            
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 12))
    
    # Add visualizations
    for viz in visualizations:
        elements.append(Image(viz, width=6*inch, height=4.5*inch))
        elements.append(Spacer(1, 12))
    
    # Add references
    if 'references' in data and data['references']:
        elements.append(Paragraph("Referencias", styles['Heading1']))
        for i, ref in enumerate(data['references'], 1):
            elements.append(Paragraph(f'{i}. {ref}', styles['Normal']))
    
    # Add external links
    if 'external_links' in data and data['external_links']:
        elements.append(Paragraph("Enlaces Externos", styles['Heading1']))
        for link in data['external_links']:
            elements.append(Paragraph(create_hyperlink(link['url'], link['text']), styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
