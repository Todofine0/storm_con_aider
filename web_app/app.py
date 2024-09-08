import os
import json
import sys
import subprocess
import logging
import re

logging.basicConfig(level=logging.DEBUG)

def install_package(package):
    try:
        subprocess.check_call(["sudo", "apt-get", "update"])
        subprocess.check_call(["sudo", "apt-get", "install", "-y", f"python3-{package}"])
    except subprocess.CalledProcessError:
        logging.error(f"Failed to install {package}. Please install it manually.")
        sys.exit(1)

required_packages = ['flask', 'reportlab', 'matplotlib', 'networkx', 'pillow']

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        logging.info(f"{package} not found. Installing...")
        install_package(package)

from flask import Flask, render_template, send_file, abort
from utils.pdf_generator import generate_pdf
from utils.ai_visualizer import generate_visualizations

app = Flask(__name__)

STORM_OUTPUT_DIR = '/home/ubuntu/storm/archivos_de_salida/'

@app.route('/')
def index():
    investigations = []
    logging.debug(f"Scanning directory: {STORM_OUTPUT_DIR}")
    for dirname in os.listdir(STORM_OUTPUT_DIR):
        dirpath = os.path.join(STORM_OUTPUT_DIR, dirname)
        if os.path.isdir(dirpath):
            logging.debug(f"Processing directory: {dirpath}")
            storm_gen_article_path = os.path.join(dirpath, 'storm_gen_article.txt')
            if os.path.exists(storm_gen_article_path):
                with open(storm_gen_article_path, 'r') as f:
                    content = f.read()
                    title = os.path.basename(dirpath).replace('_', ' ')
                    investigations.append({
                        'id': dirname,
                        'title': title
                    })
    logging.debug(f"Found {len(investigations)} investigations")
    return render_template('index.html', investigations=investigations)

@app.route('/view/<investigation_id>')
def view_investigation(investigation_id):
    dirpath = os.path.join(STORM_OUTPUT_DIR, investigation_id)
    filepath = os.path.join(dirpath, 'storm_gen_article.txt')
    
    logging.debug(f"Attempting to view investigation: {filepath}")
    if not os.path.exists(filepath):
        logging.error(f"Investigation not found: {filepath}")
        abort(404)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Parse the content into sections
    sections = []
    current_section = {'title': '', 'content': ''}
    for line in content.split('\n'):
        if line.startswith('# '):
            if current_section['title']:
                sections.append(current_section)
                current_section = {'title': '', 'content': ''}
            current_section['title'] = line.strip('# ')
        else:
            current_section['content'] += line + '\n'
    if current_section['title']:
        sections.append(current_section)
    
    data = {
        'id': investigation_id,
        'topic': sections[0]['title'] if sections else 'Untitled Investigation',
        'content': sections[1:] if len(sections) > 1 else []
    }
    return render_template('view.html', investigation=data)

@app.route('/download/<investigation_id>')
def download_pdf(investigation_id):
    dirpath = os.path.join(STORM_OUTPUT_DIR, investigation_id)
    filepath = os.path.join(dirpath, 'storm_gen_article.txt')
    
    logging.debug(f"Attempting to download PDF for investigation: {filepath}")
    if not os.path.exists(filepath):
        logging.error(f"Investigation not found: {filepath}")
        abort(404)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Parse the content into sections
    sections = []
    current_section = {'title': '', 'content': ''}
    for line in content.split('\n'):
        if line.startswith('# '):
            if current_section['title']:
                sections.append(current_section)
                current_section = {'title': '', 'content': ''}
            current_section['title'] = line.strip('# ')
        else:
            current_section['content'] += line + '\n'
    if current_section['title']:
        sections.append(current_section)
    
    data = {
        'topic': sections[0]['title'] if sections else 'Investigación sin título',
        'content': sections[1:] if len(sections) > 1 else []
    }
    
    # Add references
    references = []
    for section in data['content']:
        references.extend(re.findall(r'\[(\d+)\]\s*(.*)', section['content']))
    data['references'] = [ref[1] for ref in references]
    
    # Process content to convert links to Markdown format and handle subsections
    for section in data['content']:
        section['content'] = re.sub(r'\[(\d+)\]\s*(https?://\S+)', r'[\2](\2)', section['content'])
        section['content'] = re.sub(r'^##\s+(.*)$', r'## \1', section['content'], flags=re.MULTILINE)
        section['content'] = re.sub(r'^###\s+(.*)$', r'### \1', section['content'], flags=re.MULTILINE)
    
    # Add external links (you might want to make this dynamic based on the investigation)
    external_links = [
        {'url': 'https://www.uc.edu.ve', 'text': 'Universidad de Carabobo'},
        {'url': 'https://www.uc.edu.ve/facyt', 'text': 'Facultad de Ciencias y Tecnología (FACYT)'},
    ]
    data['external_links'] = external_links
    
    visualizations = generate_visualizations(data)
    pdf_buffer = generate_pdf(data, visualizations)
    
    return send_file(pdf_buffer, as_attachment=True, download_name=f"{investigation_id}.pdf", mimetype='application/pdf')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=80, debug=True)
