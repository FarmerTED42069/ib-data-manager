"""
Create architecture diagram for IB Data Manager
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

def create_architecture_diagram():
    """Create a visual representation of the application architecture"""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define colors
    gui_color = '#E8F4FD'
    logic_color = '#FFF7E6'
    data_color = '#E8F6E8'
    external_color = '#FFE6E6'
    
    # Create boxes for different components
    boxes = []
    
    # GUI Layer
    gui_box = FancyBboxPatch((0.5, 7), 9, 2.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=gui_color, 
                            edgecolor='black', 
                            linewidth=2)
    ax.add_patch(gui_box)
    ax.text(5, 8.25, 'GUI Layer (Tkinter)', fontsize=16, weight='bold', ha='center')
    ax.text(5, 7.75, 'main.py', fontsize=12, ha='center')
    ax.text(5, 7.4, '• User Interface\n• Event Handling\n• Data Display', fontsize=10, ha='center')
    
    # Application Logic Layer
    logic_boxes = []
    
    # IB Connector
    ib_box = FancyBboxPatch((0.5, 4.5), 4, 2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=logic_color, 
                           edgecolor='black', 
                           linewidth=1.5)
    ax.add_patch(ib_box)
    ax.text(2.5, 5.7, 'IB Connector', fontsize=14, weight='bold', ha='center')
    ax.text(2.5, 5.3, 'ib_connector.py', fontsize=11, ha='center')
    ax.text(2.5, 4.8, '• API Connection\n• Data Retrieval\n• Order Management', fontsize=9, ha='center')
    
    # Database Manager
    db_box = FancyBboxPatch((5.5, 4.5), 4, 2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=logic_color, 
                           edgecolor='black', 
                           linewidth=1.5)
    ax.add_patch(db_box)
    ax.text(7.5, 5.7, 'Database Manager', fontsize=14, weight='bold', ha='center')
    ax.text(7.5, 5.3, 'database.py', fontsize=11, ha='center')
    ax.text(7.5, 4.8, '• Data Storage\n• Query Operations\n• Export Functions', fontsize=9, ha='center')
    
    # Data Storage Layer
    sqlite_box = FancyBboxPatch((5.5, 2), 4, 2, 
                               boxstyle="round,pad=0.1", 
                               facecolor=data_color, 
                               edgecolor='black', 
                               linewidth=1.5)
    ax.add_patch(sqlite_box)
    ax.text(7.5, 3.2, 'SQLite Database', fontsize=14, weight='bold', ha='center')
    ax.text(7.5, 2.8, 'ib_data.db', fontsize=11, ha='center')
    ax.text(7.5, 2.3, '• Historical Data\n• Real-time Quotes\n• Account Info', fontsize=9, ha='center')
    
    # External Systems
    ib_gateway_box = FancyBboxPatch((0.5, 2), 4, 2, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=external_color, 
                                   edgecolor='black', 
                                   linewidth=1.5)
    ax.add_patch(ib_gateway_box)
    ax.text(2.5, 3.2, 'IB Gateway', fontsize=14, weight='bold', ha='center')
    ax.text(2.5, 2.8, 'Port 4001/4002', fontsize=11, ha='center')
    ax.text(2.5, 2.3, '• Market Data\n• Trading API\n• Account Access', fontsize=9, ha='center')
    
    # Configuration
    config_box = FancyBboxPatch((0.5, 0.2), 4, 1.3, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#F0F0F0', 
                               edgecolor='black', 
                               linewidth=1)
    ax.add_patch(config_box)
    ax.text(2.5, 0.85, 'Configuration', fontsize=12, weight='bold', ha='center')
    ax.text(2.5, 0.5, 'config.py / config.json', fontsize=10, ha='center')
    
    # Add connections
    # GUI to Logic layers
    ax.arrow(2.5, 7, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    ax.arrow(7.5, 7, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # Logic to Data/External layers
    ax.arrow(2.5, 4.5, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    ax.arrow(7.5, 4.5, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # Horizontal connections
    ax.arrow(4.5, 5.5, 0.8, 0, head_width=0.1, head_length=0.05, fc='black', ec='black')
    ax.arrow(5.3, 5.5, -0.8, 0, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # Add title
    ax.text(5, 9.7, 'IB Data Manager Architecture', fontsize=20, weight='bold', ha='center')
    
    # Add data flow labels
    ax.text(3.5, 6.5, 'Events', fontsize=9, ha='center', rotation=90)
    ax.text(6.5, 6.5, 'Data', fontsize=9, ha='center', rotation=90)
    ax.text(3.5, 4.2, 'API Calls', fontsize=9, ha='center', rotation=90)
    ax.text(6.5, 4.2, 'SQL', fontsize=9, ha='center', rotation=90)
    ax.text(5, 5.7, 'Data Exchange', fontsize=9, ha='center')
    
    plt.tight_layout()
    plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create data flow diagram
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Create flow diagram
    steps = [
        (2, 7, "User Request", gui_color),
        (2, 5.5, "IB Connector", logic_color),
        (2, 4, "IB Gateway", external_color),
        (2, 2.5, "Market Data", external_color),
        (8, 2.5, "Database", data_color),
        (8, 4, "Data Processing", logic_color),
        (8, 5.5, "UI Update", gui_color),
        (8, 7, "User Display", gui_color)
    ]
    
    for i, (x, y, text, color) in enumerate(steps):
        box = FancyBboxPatch((x-1, y-0.3), 2, 0.6, 
                            boxstyle="round,pad=0.1", 
                            facecolor=color, 
                            edgecolor='black', 
                            linewidth=1)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=11, ha='center', va='center')
    
    # Add arrows
    arrow_props = dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=1.5)
    
    # Vertical arrows (left side)
    for i in range(3):
        ax.annotate('', xy=(2, steps[i+1][1] + 0.3), xytext=(2, steps[i][1] - 0.3),
                   arrowprops=arrow_props)
    
    # Horizontal arrow (bottom)
    ax.annotate('', xy=(7, 2.5), xytext=(3, 2.5),
               arrowprops=arrow_props)
    
    # Vertical arrows (right side)
    for i in range(4, 7):
        ax.annotate('', xy=(8, steps[i+1][1] - 0.3), xytext=(8, steps[i][1] + 0.3),
                   arrowprops=arrow_props)
    
    # Add title
    ax.text(5, 7.5, 'Data Flow Process', fontsize=16, weight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig('data_flow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Architecture diagrams created successfully!")
    print("- architecture_diagram.png")
    print("- data_flow_diagram.png")

if __name__ == "__main__":
    create_architecture_diagram()
