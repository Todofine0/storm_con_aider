import os
import json
import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ['flask', 'reportlab', 'matplotlib', 'networkx', 'pillow']

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found. Installing...")
        install_package(package)

from flask import Flask, render_template, send_file
from utils.pdf_generator import generate_pdf
from utils.ai_visualizer import generate_visualizations

app = Flask(__name__)

STORM_OUTPUT_DIR = '/home/ubuntu/storm/archivos_de_salida/'

@app.route('/')
def index():
    investigations = []
    for filename in os.listdir(STORM_OUTPUT_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(STORM_OUTPUT_DIR, filename), 'r') as f:
                data = json.load(f)
                investigations.append({
                    'id': filename[:-5],  # Remove .json extension
                    'title': data.get('topic', 'Untitled Investigation')
                })
    return render_template('index.html', investigations=investigations)

@app.route('/view/<investigation_id>')
def view_investigation(investigation_id):
    filename = f"{investigation_id}.json"
    filepath = os.path.join(STORM_OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        return "Investigation not found", 404
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return render_template('view.html', investigation=data)

@app.route('/download/<investigation_id>')
def download_pdf(investigation_id):
    filename = f"{investigation_id}.json"
    filepath = os.path.join(STORM_OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        return "Investigation not found", 404
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    visualizations = generate_visualizations(data)
    pdf_path = generate_pdf(data, visualizations)
    
    return send_file(pdf_path, as_attachment=True, download_name=f"{investigation_id}.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
