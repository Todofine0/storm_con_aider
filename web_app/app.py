import os
import json
import sys
import subprocess
import logging

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
    for filename in os.listdir(STORM_OUTPUT_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(STORM_OUTPUT_DIR, filename)
            logging.debug(f"Processing file: {filepath}")
            with open(filepath, 'r') as f:
                data = json.load(f)
                investigations.append({
                    'id': filename[:-5],  # Remove .json extension
                    'title': data.get('topic', 'Untitled Investigation')
                })
    logging.debug(f"Found {len(investigations)} investigations")
    return render_template('index.html', investigations=investigations)

@app.route('/view/<investigation_id>')
def view_investigation(investigation_id):
    filename = f"{investigation_id}.json"
    filepath = os.path.join(STORM_OUTPUT_DIR, filename)
    
    logging.debug(f"Attempting to view investigation: {filepath}")
    if not os.path.exists(filepath):
        logging.error(f"Investigation not found: {filepath}")
        abort(404)
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    data['id'] = investigation_id
    return render_template('view.html', investigation=data)

@app.route('/download/<investigation_id>')
def download_pdf(investigation_id):
    filename = f"{investigation_id}.json"
    filepath = os.path.join(STORM_OUTPUT_DIR, filename)
    
    logging.debug(f"Attempting to download PDF for investigation: {filepath}")
    if not os.path.exists(filepath):
        logging.error(f"Investigation not found: {filepath}")
        abort(404)
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    visualizations = generate_visualizations(data)
    pdf_buffer = generate_pdf(data, visualizations)
    
    return send_file(pdf_buffer, as_attachment=True, download_name=f"{investigation_id}.pdf", mimetype='application/pdf')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=80, debug=True)
