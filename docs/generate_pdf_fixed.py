#!/usr/bin/env python3
"""
Generate PDF from Markdown with rendered Mermaid diagrams and proper text colors
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

def render_mermaid_to_svg(mermaid_code, output_path):
    """Render Mermaid code to SVG using mmdc with proper styling"""
    try:
        # Create temporary file with Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_code)
            temp_file = f.name
        
        # Render using mmdc with better styling
        cmd = [
            'mmdc', 
            '-i', temp_file, 
            '-o', output_path,
            '-b', 'white',  # White background
            '-t', 'default'  # Default theme for better contrast
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error rendering Mermaid: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error rendering Mermaid: {e}")
        return False

def replace_mermaid_with_images(markdown_content, image_dir):
    """Replace Mermaid blocks with image references"""
    def replace_block(match):
        mermaid_code = match.group(1)
        # Generate filename based on content hash
        filename = f"diagram_{hash(mermaid_code) % 10000}.svg"
        image_path = os.path.join(image_dir, filename)
        
        # Render the diagram
        if render_mermaid_to_svg(mermaid_code, image_path):
            return f'\n![Architecture Diagram]({image_path})\n'
        else:
            return f'\n```mermaid\n{mermaid_code}\n```\n'
    
    pattern = r'```mermaid\s*\n(.*?)\n```'
    return re.sub(pattern, replace_block, markdown_content, flags=re.DOTALL)

def create_custom_css():
    """Create custom CSS for better PDF styling"""
    css_content = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.6;
        color: #333333 !important;
        background-color: white !important;
        margin: 2em;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3em;
    }
    
    h1 { font-size: 2.2em; color: #2c3e50 !important; }
    h2 { font-size: 1.8em; color: #34495e !important; }
    h3 { font-size: 1.5em; color: #34495e !important; }
    h4 { font-size: 1.3em; color: #34495e !important; }
    
    p, li, td, th {
        color: #333333 !important;
        font-size: 1em;
    }
    
    code {
        background-color: #f8f9fa;
        color: #e83e8c !important;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    }
    
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 1em;
        overflow-x: auto;
    }
    
    pre code {
        background-color: transparent;
        color: #333333 !important;
        padding: 0;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    
    th, td {
        border: 1px solid #dee2e6;
        padding: 0.75em;
        text-align: left;
        color: #333333 !important;
    }
    
    th {
        background-color: #f8f9fa;
        color: #495057 !important;
        font-weight: 600;
    }
    
    img {
        max-width: 100%;
        height: auto;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        margin: 1em 0;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 1em 0;
        padding-left: 1em;
        color: #6c757d !important;
        background-color: #f8f9fa;
    }
    
    a {
        color: #3498db !important;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    .toc {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 1em;
        margin: 1em 0;
    }
    
    .toc h2 {
        border-bottom: none;
        margin-top: 0;
    }
    
    .toc ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .toc li {
        margin: 0.5em 0;
    }
    
    .toc a {
        color: #495057 !important;
        text-decoration: none;
    }
    
    .toc a:hover {
        color: #3498db !important;
        text-decoration: underline;
    }
    """
    
    css_file = "docs/print_styles.css"
    with open(css_file, 'w') as f:
        f.write(css_content)
    
    return css_file

def generate_pdf_with_diagrams():
    """Generate PDF with rendered Mermaid diagrams and proper styling"""
    # Create images directory
    images_dir = Path("docs/images")
    images_dir.mkdir(exist_ok=True)
    
    # Read markdown content
    markdown_file = "docs/architecture.md"
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    # Replace Mermaid blocks with images
    print("📊 Rendering Mermaid diagrams...")
    content_with_images = replace_mermaid_with_images(content, str(images_dir))
    
    # Create custom CSS for better styling
    print("🎨 Creating custom CSS for better styling...")
    css_file = create_custom_css()
    
    # Write modified markdown
    modified_md = "docs/architecture-with-images.md"
    with open(modified_md, 'w') as f:
        f.write(content_with_images)
    
    print("📄 Generating PDF with proper styling...")
    
    # Generate PDF using pandoc with custom CSS
    cmd = [
        'pandoc', modified_md,
        '-o', 'docs/architecture-printable.pdf',
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
        print("✅ PDF generated successfully: docs/architecture-printable.pdf")
        print("📁 Images saved in: docs/images/")
        print("🎨 Custom styling applied for better readability")
        
        # Show file size
        file_size = os.path.getsize("docs/architecture-printable.pdf")
        print(f"📏 File size: {file_size / 1024 / 1024:.1f} MB")
    else:
        print(f"❌ Error generating PDF: {result.stderr}")
    
    # Clean up temporary files
    os.unlink(modified_md)
    os.unlink(css_file)

if __name__ == "__main__":
    generate_pdf_with_diagrams()
