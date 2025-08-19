#!/bin/bash
# Print Architecture Documentation Script
# Generates PDF with rendered Mermaid diagrams and proper text colors

echo "🔄 Generating PDF with Mermaid diagrams..."
echo "📊 Rendering architecture diagrams..."
echo "🎨 Applying custom styling for better readability..."

# Run the improved Python script
python generate_pdf_fixed.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Your architecture documentation is ready:"
    echo "📄 PDF: docs/architecture-printable.pdf"
    echo "🖼️  Images: docs/images/"
    echo ""
    echo "🎨 Features:"
    echo "   • High contrast text colors for readability"
    echo "   • Professional styling and typography"
    echo "   • Rendered Mermaid diagrams as images"
    echo "   • Table of contents with navigation"
    echo ""
    echo "🖨️  You can now:"
    echo "   • Open the PDF in any PDF viewer"
    echo "   • Print it directly from the PDF"
    echo "   • Share it with your team"
    echo ""
    echo "📁 File sizes:"
    ls -lh docs/architecture-printable.pdf
    echo ""
    echo "🔄 To regenerate, just run: ./docs/print_architecture.sh"
else
    echo "❌ Error generating PDF. Please check the error messages above."
    exit 1
fi
