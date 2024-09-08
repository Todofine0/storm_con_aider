from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListItem, ListFlowable, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io
import re

def create_hyperlink(url, text):
    return f'<link href="{url}" color="blue">{text}</link>'

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(letter[0] - 30, 30, f"Página {self._pageNumber} de {page_count}")

def generate_pdf(data, visualizations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles['Title'].fontSize = 24
    styles['Title'].alignment = TA_CENTER
    styles['Title'].spaceAfter = 24
    styles['Heading1'].fontSize = 18
    styles['Heading1'].spaceAfter = 12
    styles['Heading2'].fontSize = 16
    styles['Heading2'].spaceAfter = 10
    styles['Heading3'].fontSize = 14
    styles['Heading3'].spaceAfter = 8
    styles.add(ParagraphStyle(name='Justified', parent=styles['Normal'], alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Abstract', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY))
    
    elements = []
    
    # Add title
    elements.append(Paragraph(data['topic'], styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Add abstract
    elements.append(Paragraph("Resumen", styles['Heading2']))
    abstract = """Este documento presenta un análisis exhaustivo generado por STORM (Sistema de Tecnología Organizada para la Recopilación y Manejo de información). 
    STORM es una herramienta avanzada de investigación que utiliza inteligencia artificial para recopilar, analizar y sintetizar información de diversas fuentes. 
    El objetivo de este informe es proporcionar una visión completa y objetiva sobre el tema en cuestión, basada en datos actualizados y relevantes."""
    elements.append(Paragraph(abstract, styles['Abstract']))
    elements.append(Spacer(1, 12))
    
    # Add introduction
    elements.append(Paragraph("1. Introducción", styles['Heading1']))
    introduction = """STORM (Sistema de Tecnología Organizada para la Recopilación y Manejo de información) es una plataforma de investigación de vanguardia 
    que emplea técnicas avanzadas de inteligencia artificial para realizar análisis exhaustivos sobre diversos temas. Este informe es el resultado de un proceso 
    riguroso de recopilación, análisis y síntesis de información proveniente de múltiples fuentes confiables.

    El propósito de este documento es ofrecer una visión integral y objetiva sobre el tema "{}", abordando sus aspectos más relevantes y proporcionando 
    información actualizada y precisa. A lo largo de las siguientes secciones, se presentarán los hallazgos clave, se analizarán las tendencias actuales 
    y se explorarán las implicaciones futuras relacionadas con el tema en cuestión.

    Este informe está estructurado de manera que facilite la comprensión y el análisis del tema, comenzando con una visión general y profundizando 
    progresivamente en aspectos más específicos. Cada sección ha sido cuidadosamente elaborada para proporcionar información valiosa y perspectivas únicas, 
    respaldadas por datos y fuentes confiables.""".format(data['topic'])
    elements.append(Paragraph(introduction, styles['Justified']))
    elements.append(Spacer(1, 12))
    
    # Add table of contents
    elements.append(PageBreak())
    elements.append(Paragraph("Tabla de Contenidos", styles['Heading1']))
    toc_data = [["Sección", "Página"]]
    toc_data.append(["1. Introducción", "2"])
    for i, section in enumerate(data['content'], start=2):
        toc_data.append([f"{i}. {section['title']}", ""])
    toc_style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
    ])
    toc_table = Table(toc_data, colWidths=[5*inch, 1*inch])
    toc_table.setStyle(toc_style)
    elements.append(toc_table)
    elements.append(PageBreak())
    
    # Add content
    for i, section in enumerate(data['content'], start=2):
        elements.append(Paragraph(f"{i}. {section['title']}", styles['Heading1']))
        
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
                
                elements.append(Paragraph(paragraph, styles['Justified']))
            
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 12))
    
    # Add visualizations
    if visualizations:
        elements.append(PageBreak())
        elements.append(Paragraph("Visualizaciones", styles['Heading1']))
        for viz in visualizations:
            elements.append(Image(viz, width=6*inch, height=4.5*inch))
            elements.append(Spacer(1, 12))
    
    # Add conclusion
    elements.append(PageBreak())
    elements.append(Paragraph("Conclusión", styles['Heading1']))
    conclusion = """Este informe generado por STORM ha proporcionado un análisis detallado y exhaustivo sobre "{}". A través de la recopilación y síntesis 
    de información proveniente de diversas fuentes confiables, hemos presentado una visión integral del tema, abordando sus aspectos más relevantes y 
    explorando sus implicaciones.

    La utilización de tecnologías avanzadas de inteligencia artificial en el proceso de investigación ha permitido ofrecer un análisis objetivo y actualizado, 
    basado en datos precisos y tendencias actuales. Este enfoque innovador facilita la comprensión de temas complejos y proporciona insights valiosos para 
    la toma de decisiones informadas.

    Es importante destacar que, si bien este informe ofrece una visión completa del tema en cuestión, el conocimiento en este campo está en constante evolución. 
    Se recomienda mantener un seguimiento continuo de las nuevas investigaciones y desarrollos relacionados con este tema para estar al día con los avances más recientes.

    STORM seguirá mejorando y actualizando sus capacidades de análisis e investigación, con el objetivo de proporcionar informes cada vez más precisos, 
    completos y útiles para sus usuarios.""".format(data['topic'])
    elements.append(Paragraph(conclusion, styles['Justified']))
    elements.append(Spacer(1, 12))
    
    # Add references
    if 'references' in data and data['references']:
        elements.append(PageBreak())
        elements.append(Paragraph("Referencias", styles['Heading1']))
        for i, ref in enumerate(data['references'], 1):
            elements.append(Paragraph(f'{i}. {ref}', styles['Normal']))
    
    # Add external links
    if 'external_links' in data and data['external_links']:
        elements.append(PageBreak())
        elements.append(Paragraph("Enlaces Externos", styles['Heading1']))
        for link in data['external_links']:
            elements.append(Paragraph(create_hyperlink(link['url'], link['text']), styles['Normal']))
    
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
