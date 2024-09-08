from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import io

def generate_pdf(data, visualizations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []
    
    # Add title
    elements.append(Paragraph(data['topic'], styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Add content
    for section in data['content']:
        elements.append(Paragraph(section['title'], styles['Heading2']))
        elements.append(Paragraph(section['content'], styles['BodyText']))
        elements.append(Spacer(1, 12))
    
    # Add visualizations
    for viz in visualizations:
        elements.append(Image(viz, width=400, height=300))
        elements.append(Spacer(1, 12))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
