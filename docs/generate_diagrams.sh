#!/bin/bash
# Generate SVG Diagrams Script
# Creates SVG diagrams from Mermaid code in architecture.md

echo "🔄 Generating SVG diagrams from Mermaid code..."
echo "📊 Processing architecture diagrams..."

# Run the Python script
python generate_svg_diagrams.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Your SVG diagrams are ready:"
    echo "📁 Images: docs/images/"
    echo "📄 Updated markdown: docs/architecture-with-images.md"
    echo ""
    echo "🖼️  Generated diagrams:"
    ls -la docs/images/*.svg
    echo ""
    echo "🔄 To regenerate, run: ./docs/generate_diagrams.sh"
else
    echo "❌ Error generating diagrams. Please check the error messages above."
    exit 1
fi
