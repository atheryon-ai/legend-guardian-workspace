#!/usr/bin/env python3
"""
Generate PDF from Markdown with rendered Mermaid diagrams
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path


def extract_mermaid_blocks(markdown_content):
    """Extract Mermaid code blocks from markdown"""
    mermaid_blocks = []
    pattern = r"```mermaid\s*\n(.*?)\n```"

    for match in re.finditer(pattern, markdown_content, re.DOTALL):
        mermaid_blocks.append(match.group(1))

    return mermaid_blocks


def render_mermaid_to_svg(mermaid_code, output_path):
    """Render Mermaid code to SVG using mmdc"""
    try:
        # Create temporary file with Mermaid code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_code)
            temp_file = f.name

        # Render using mmdc - output format is determined by file extension
        cmd = ["mmdc", "-i", temp_file, "-o", output_path]
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
            return f"\n![Architecture Diagram]({image_path})\n"
        else:
            return f"\n```mermaid\n{mermaid_code}\n```\n"

    pattern = r"```mermaid\s*\n(.*?)\n```"
    return re.sub(pattern, replace_block, markdown_content, flags=re.DOTALL)


def generate_pdf_with_diagrams():
    """Generate PDF with rendered Mermaid diagrams"""
    # Create images directory
    images_dir = Path("docs/images")
    images_dir.mkdir(exist_ok=True)

    # Read markdown content
    markdown_file = "docs/architecture.md"
    with open(markdown_file, "r") as f:
        content = f.read()

    # Replace Mermaid blocks with images
    print("Rendering Mermaid diagrams...")
    content_with_images = replace_mermaid_with_images(content, str(images_dir))

    # Write modified markdown
    modified_md = "docs/architecture-with-images.md"
    with open(modified_md, "w") as f:
        f.write(content_with_images)

    print("Generating PDF...")

    # Generate PDF using pandoc
    cmd = [
        "pandoc",
        modified_md,
        "-o",
        "docs/architecture-with-diagrams.pdf",
        "--pdf-engine=weasyprint",
        "--standalone",
        "--toc",
        "--toc-depth=3",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ PDF generated successfully: docs/architecture-with-diagrams.pdf")
        print("📁 Images saved in: docs/images/")
    else:
        print(f"❌ Error generating PDF: {result.stderr}")

    # Clean up temporary file
    os.unlink(modified_md)


if __name__ == "__main__":
    generate_pdf_with_diagrams()
