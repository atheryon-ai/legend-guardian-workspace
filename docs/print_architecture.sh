#!/bin/bash
# Print Architecture Documentation Script
# Generates PDF with rendered Mermaid diagrams

echo "🔄 Generating PDF with Mermaid diagrams..."
echo "📊 Rendering architecture diagrams..."

# Run the Python script
python generate_pdf.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Your architecture documentation is ready:"
    echo "📄 PDF: docs/architecture-with-diagrams.pdf"
    echo "🖼️  Images: docs/images/"
    echo ""
    echo "🖨️  You can now:"
    echo "   • Open the PDF in any PDF viewer"
    echo "   • Print it directly from the PDF"
    echo "   • Share it with your team"
    echo ""
    echo "📁 File sizes:"
    ls -lh docs/architecture-with-diagrams.pdf
    echo ""
    echo "🔄 To regenerate, just run: ./docs/print_architecture.sh"
else
    echo "❌ Error generating PDF. Please check the error messages above."
    exit 1
fi
