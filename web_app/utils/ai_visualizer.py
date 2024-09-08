import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import io

def generate_visualizations(data):
    visualizations = []
    
    # Generate a simple graph visualization
    G = nx.Graph()
    for i, section in enumerate(data['content']):
        G.add_node(section['title'])
        if i > 0:
            G.add_edge(data['content'][i-1]['title'], section['title'])
    
    plt.figure(figsize=(10, 8))
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=3000, font_size=8, font_weight='bold')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    visualizations.append(buf)
    
    return visualizations
