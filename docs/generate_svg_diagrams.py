#!/usr/bin/env python3
"""
Simple SVG Diagram Generator
Generates SVG diagrams from Mermaid code in architecture.md
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

def create_mermaid_config():
    """Create Mermaid configuration for better text visibility"""
    config_content = {
        "theme": "default",
        "themeVariables": {
            "fontFamily": "Arial, Helvetica, sans-serif",
            "fontSize": "16px",
            "fontWeight": "bold",
            "primaryColor": "#2c3e50",
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#34495e",
            "lineColor": "#34495e",
            "secondaryColor": "#3498db",
            "tertiaryColor": "#e74c3c",
            "noteBkgColor": "#f8f9fa",
            "noteBorderColor": "#dee2e6",
            "noteTextColor": "#000000",
            "errorBkgColor": "#f8d7da",
            "errorTextColor": "#000000",
            "labelTextColor": "#000000",
            "nodeTextColor": "#000000",
            "edgeLabelBackground": "#ffffff",
            "edgeLabelColor": "#000000"
        },
        "flowchart": {
            "htmlLabels": True,
            "curve": "basis",
            "padding": 20
        },
        "sequence": {
            "diagramMarginX": 50,
            "diagramMarginY": 10,
            "actorMargin": 50,
            "width": 150,
            "height": 65,
            "boxMargin": 10,
            "boxTextMargin": 5,
            "noteMargin": 10,
            "messageMargin": 35
        }
    }
    
    config_file = "docs/mermaid-config.json"
    import json
    with open(config_file, 'w') as f:
        json.dump(config_content, f, indent=2)
    
    return config_file

def render_mermaid_to_svg(mermaid_code, output_path, diagram_name):
    """Render Mermaid code to SVG using mmdc"""
    try:
        # Create temporary file with Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_code)
            temp_file = f.name
        
        # Create Mermaid configuration
        config_file = create_mermaid_config()
        
        # Render using mmdc
        cmd = [
            'mmdc', 
            '-i', temp_file, 
            '-o', output_path,
            '-b', 'white',  # White background
            '-t', 'default', # Default theme
            '-w', '1400',    # Width for better text spacing
            '-H', '900',     # Height for better layout
            '-c', config_file  # Configuration
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        os.unlink(temp_file)
        os.unlink(config_file)
        
        if result.returncode == 0:
            return True
        else:
            print(f"⚠️  Rendering failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error rendering: {e}")
        return False

def cleanup_old_diagrams(image_dir):
    """Clean up old diagram files"""
    try:
        for file in os.listdir(image_dir):
            if file.startswith('diagram_') and file.endswith('.svg'):
                old_file = os.path.join(image_dir, file)
                os.unlink(old_file)
                print(f"🗑️  Cleaned up: {file}")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def generate_svg_diagrams():
    """Generate SVG diagrams from Mermaid code"""
    # Create images directory
    images_dir = Path("docs/images")
    images_dir.mkdir(exist_ok=True)
    
    # Clean up old diagrams
    cleanup_old_diagrams(images_dir)
    
    # Read markdown content
    markdown_file = "docs/architecture.md"
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Define diagram names
    diagram_names = [
        "High-Level System Architecture",
        "Detailed Component Architecture", 
        "Network Architecture & Ports",
        "Authentication & Security",
        "Data Flow Architecture",
        "Deployment Architecture"
    ]
    
    def replace_block(match):
        # Get the current diagram index
        current_index = len([m for m in re.finditer(r'```mermaid\s*\n(.*?)\n```', content, re.DOTALL) if m.start() <= match.start()])
        diagram_index = current_index - 1
        
        mermaid_code = match.group(1)
        
        # Get diagram name
        if diagram_index < len(diagram_names):
            diagram_name = diagram_names[diagram_index]
        else:
            diagram_name = f"Diagram_{diagram_index + 1}"
        
        print(f"🔄 Processing: {diagram_name}")
        
        # Create filename
        safe_name = diagram_name.replace(" ", "_").replace("&", "and").replace("-", "_")
        svg_filename = f"{safe_name}.svg"
        svg_path = os.path.join(images_dir, svg_filename)
        
        # Render diagram
        if render_mermaid_to_svg(mermaid_code, svg_path, diagram_name):
            print(f"✅ Created: {svg_filename}")
            return f'\n![{diagram_name}]({svg_path})\n'
        else:
            print(f"❌ Failed: {diagram_name}")
            return f'\n```mermaid\n{mermaid_code}\n```\n'
    
    # Replace Mermaid blocks with images
    pattern = r'```mermaid\s*\n(.*?)\n```'
    result = re.sub(pattern, replace_block, content, flags=re.DOTALL)
    
    # Write updated markdown
    updated_md = "docs/architecture-with-images.md"
    with open(updated_md, 'w') as f:
        f.write(result)
    
    print(f"\n🎉 SVG diagrams generated successfully!")
    print(f"📁 Images saved in: docs/images/")
    print(f"📄 Updated markdown: {updated_md}")
    print(f"🔄 To regenerate, run: python docs/generate_svg_diagrams.py")

if __name__ == "__main__":
    generate_svg_diagrams()
