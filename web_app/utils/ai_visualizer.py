import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import io
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid GUI issues

def generate_visualizations(data):
    visualizations = []
    
    # Generate a simple graph visualization
    G = nx.Graph()
    for i, section in enumerate(data['content']):
        G.add_node(section['title'])
        if i > 0:
            G.add_edge(data['content'][i-1]['title'], section['title'])
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)  # Use spring layout for better spacing
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=8, font_weight='bold', font_family='sans-serif')
    
    # Adjust labels to prevent overlap
    labels = nx.get_node_attributes(G, 'name')
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold', font_family='sans-serif')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close()  # Close the figure to free up memory
    buf.seek(0)
    visualizations.append(buf)
    
    return visualizations
