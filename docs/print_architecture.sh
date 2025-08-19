#!/bin/bash
# Print Architecture Documentation Script
# Generates PDF with rendered Mermaid diagrams and proper text colors

echo "🔄 Generating Ultimate PDF with Mermaid diagrams..."
echo "📊 Rendering architecture diagrams with theme testing..."
echo "🎨 Applying ultimate styling for maximum readability..."

# Run the ultimate Python script
python generate_pdf_ultimate.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Your architecture documentation is ready:"
    echo "📄 PDF: docs/architecture-ultimate.pdf"
    echo "🖼️  Images: docs/images/"
    echo ""
    echo "🎨 Ultimate Features:"
    echo "   • Maximum text contrast (pure black on white)"
    echo "   • Mermaid diagrams with optimal text visibility"
    echo "   • Theme testing for best diagram rendering"
    echo "   • Professional styling and typography"
    echo "   • Table of contents with navigation"
    echo ""
    echo "🖨️  You can now:"
    echo "   • Open the PDF in any PDF viewer"
    echo "   • Print it directly from the PDF"
    echo "   • Share it with your team"
    echo ""
    echo "📁 File sizes:"
    ls -lh docs/architecture-ultimate.pdf
    echo ""
    echo "🔄 To regenerate, just run: ./docs/print_architecture.sh"
else
    echo "❌ Error generating PDF. Please check the error messages above."
    exit 1
fi
