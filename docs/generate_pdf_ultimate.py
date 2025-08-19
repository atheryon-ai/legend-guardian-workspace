#!/usr/bin/env python3
"""
Ultimate PDF Generation with Multiple Mermaid Theme Testing
Ensures maximum text visibility in diagrams
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

def extract_mermaid_blocks(markdown_content):
    """Extract Mermaid code blocks from markdown"""
    mermaid_blocks = []
    pattern = r'```mermaid\s*\n(.*?)\n```'
    
    for match in re.finditer(pattern, markdown_content, re.DOTALL):
        mermaid_blocks.append(match.group(1))
    
    return mermaid_blocks

def create_enhanced_mermaid_config():
    """Create enhanced Mermaid configuration for maximum text visibility"""
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
        },
        "gantt": {
            "titleTopMargin": 25,
            "barTopMargin": 50,
            "barHeight": 20,
            "barGap": 4,
            "topPadding": 50,
            "leftPadding": 75,
            "gridLineStartPadding": 35,
            "fontSize": 11,
            "fontFamily": "Arial, Helvetica, sans-serif"
        }
    }
    
    config_file = "docs/mermaid-enhanced-config.json"
    import json
    with open(config_file, 'w') as f:
        json.dump(config_content, f, indent=2)
    
    return config_file

def render_mermaid_with_theme_testing(mermaid_code, output_path, diagram_name):
    """Render Mermaid with multiple theme testing for best text visibility"""
    themes_to_test = ["default", "forest", "neutral", "dark"]
    
    for theme in themes_to_test:
        try:
            # Create temporary file with Mermaid code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(mermaid_code)
                temp_file = f.name
            
            # Create enhanced Mermaid configuration
            config_file = create_enhanced_mermaid_config()
            
            # Test output path for this theme
            theme_output = output_path.replace('.svg', f'_{theme}.svg')
            
            # Render using mmdc with current theme
            cmd = [
                'mmdc', 
                '-i', temp_file, 
                '-o', theme_output,
                '-b', 'white',  # White background
                '-t', theme,     # Current theme
                '-w', '1400',    # Wider width for better text spacing
                '-H', '900',     # Height for better layout
                '-c', config_file  # Enhanced configuration
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.unlink(temp_file)
            os.unlink(config_file)
            
            if result.returncode == 0:
                print(f"✅ Successfully rendered '{diagram_name}' with {theme} theme")
                # Use the first successful theme
                os.rename(theme_output, output_path)
                return True
            else:
                print(f"⚠️  Theme {theme} failed for '{diagram_name}': {result.stderr}")
                # Clean up failed output
                if os.path.exists(theme_output):
                    os.unlink(theme_output)
                
        except Exception as e:
            print(f"❌ Error with theme {theme} for '{diagram_name}': {e}")
            continue
    
    print(f"❌ All themes failed for '{diagram_name}', using fallback")
    return False

def cleanup_old_diagrams(image_dir):
    """Clean up old diagram files with generic names"""
    try:
        for file in os.listdir(image_dir):
            if file.startswith('diagram_') and file.endswith('.svg'):
                old_file = os.path.join(image_dir, file)
                os.unlink(old_file)
                print(f"🗑️  Cleaned up old file: {file}")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def replace_mermaid_with_images(markdown_content, image_dir):
    """Replace Mermaid blocks with image references"""
    # Clean up old diagram files first
    cleanup_old_diagrams(image_dir)
    
    # Define diagram names based on content patterns
    diagram_names = [
        "High-Level System Architecture",
        "Detailed Component Architecture", 
        "Network Architecture & Ports",
        "Authentication & Security",
        "Data Flow Architecture",
        "Deployment Architecture"
    ]
    
    def replace_block(match):
        # Get the current diagram index from the match object
        current_index = len([m for m in re.finditer(r'```mermaid\s*\n(.*?)\n```', markdown_content, re.DOTALL) if m.start() <= match.start()])
        
        mermaid_code = match.group(1)
        
        # Get diagram name (0-indexed)
        diagram_index = current_index - 1
        if diagram_index < len(diagram_names):
            diagram_name = diagram_names[diagram_index]
        else:
            diagram_name = f"Diagram_{diagram_index + 1}"
        
        print(f"🔄 Processing diagram {diagram_index + 1}: {diagram_name}")
        
        # Create descriptive filename
        safe_name = diagram_name.replace(" ", "_").replace("&", "and").replace("-", "_")
        svg_filename = f"{safe_name}.svg"
        
        svg_path = os.path.join(image_dir, svg_filename)
        
        # Render the diagram with theme testing
        if render_mermaid_with_theme_testing(mermaid_code, svg_path, diagram_name):
            print(f"✅ Successfully created '{diagram_name}' as SVG")
            # Use SVG directly for better text visibility in PDF
            return f'\n![{diagram_name}]({svg_path})\n'
        else:
            return f'\n```mermaid\n{mermaid_code}\n```\n'
    
    pattern = r'```mermaid\s*\n(.*?)\n```'
    result = re.sub(pattern, replace_block, markdown_content, flags=re.DOTALL)
    
    return result

def create_ultimate_css():
    """Create ultimate CSS for maximum readability"""
    css_content = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.6;
        color: #000000 !important;
        background-color: white !important;
        margin: 2em;
        font-size: 12pt;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        border-bottom: 3px solid #000000;
        padding-bottom: 0.3em;
        font-weight: bold;
    }
    
    h1 { font-size: 18pt; color: #000000 !important; }
    h2 { font-size: 16pt; color: #000000 !important; }
    h3 { font-size: 14pt; color: #000000 !important; }
    h4 { font-size: 12pt; color: #000000 !important; }
    
    p, li, td, th {
        color: #000000 !important;
        font-size: 11pt;
        font-weight: normal;
    }
    
    code {
        background-color: #f0f0f0;
        color: #000000 !important;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        font-weight: bold;
    }
    
    pre {
        background-color: #f0f0f0;
        border: 2px solid #000000;
        border-radius: 6px;
        padding: 1em;
        overflow-x: auto;
    }
    
    pre code {
        background-color: transparent;
        color: #000000 !important;
        padding: 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
        border: 2px solid #000000;
    }
    
    th, td {
        border: 1px solid #000000;
        padding: 0.75em;
        text-align: left;
        color: #000000 !important;
        font-weight: bold;
    }
    
    th {
        background-color: #e0e0e0;
        color: #000000 !important;
        font-weight: bold;
    }
    
    img {
        max-width: 100%;
        height: auto;
        border: 2px solid #000000;
        border-radius: 6px;
        margin: 1em 0;
        background-color: white;
    }
    
    blockquote {
        border-left: 4px solid #000000;
        margin: 1em 0;
        padding-left: 1em;
        color: #000000 !important;
        background-color: #f0f0f0;
        font-weight: bold;
    }
    
    a {
        color: #000000 !important;
        text-decoration: underline;
        font-weight: bold;
    }
    
    .toc {
        background-color: #f0f0f0;
        border: 2px solid #000000;
        border-radius: 6px;
        padding: 1em;
        margin: 1em 0;
    }
    
    .toc h2 {
        border-bottom: none;
        margin-top: 0;
        color: #000000 !important;
    }
    
    .toc ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .toc li {
        margin: 0.5em 0;
        color: #000000 !important;
    }
    
    .toc a {
        color: #000000 !important;
        text-decoration: underline;
        font-weight: bold;
    }
    """
    
    css_file = "docs/ultimate_print_styles.css"
    with open(css_file, 'w') as f:
        f.write(css_content)
    
    return css_file

def generate_ultimate_pdf():
    """Generate ultimate PDF with maximum text visibility"""
    # Create images directory
    images_dir = Path("docs/images")
    images_dir.mkdir(exist_ok=True)
    
    # Read markdown content
    markdown_file = "docs/architecture.md"
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Replace Mermaid blocks with images
    print("📊 Rendering Mermaid diagrams with theme testing...")
    content_with_images = replace_mermaid_with_images(content, str(images_dir))
    
    # Create ultimate CSS for maximum readability
    print("🎨 Creating ultimate CSS for maximum readability...")
    css_file = create_ultimate_css()
    
    # Write modified markdown
    modified_md = "docs/architecture-ultimate.md"
    with open(modified_md, 'w') as f:
        f.write(content_with_images)
    
    print("📄 Generating ultimate PDF...")
    
    # Generate PDF using pandoc with ultimate CSS
    cmd = [
        'pandoc', modified_md,
        '-o', 'docs/architecture-ultimate.pdf',
        '--pdf-engine=weasyprint',
        '--standalone',
        '--toc',
        '--toc-depth=3',
        '--css', css_file,
        '--metadata', 'title="Legend Guardian Agent - System Architecture"',
        '--metadata', 'author="Legend Guardian Agent Team"',
        '--metadata', 'date=' + os.popen('date').read().strip()
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Ultimate PDF generated successfully: docs/architecture-ultimate.pdf")
        print("📁 Images saved in: docs/images/")
        print("🎨 Ultimate styling applied for maximum readability")
        
        # Show file size
        file_size = os.path.getsize("docs/architecture-ultimate.pdf")
        print(f"📏 File size: {file_size / 1024 / 1024:.1f} MB")
    else:
        print(f"❌ Error generating PDF: {result.stderr}")
    
    # Clean up temporary files
    os.unlink(modified_md)
    os.unlink(css_file)

if __name__ == "__main__":
    generate_ultimate_pdf()
