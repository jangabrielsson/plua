#!/bin/bash
# create-docs-pdf.sh
# Generate comprehensive PDF documentation from all markdown files in the plua project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/dist"
OUTPUT_FILE="$OUTPUT_DIR/plua-documentation.pdf"

echo -e "${BLUE}📖 plua Documentation PDF Generator${NC}"
echo -e "Project root: $PROJECT_ROOT"
echo -e "Output file: $OUTPUT_FILE"
echo ""

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}❌ Error: pandoc is not installed${NC}"
    echo ""
    echo "Please install pandoc:"
    echo "  macOS:   brew install pandoc"
    echo "  Ubuntu:  sudo apt install pandoc texlive-xetex"
    echo "  Windows: choco install pandoc miktex"
    echo ""
    echo "For LaTeX support, you may also need:"
    echo "  macOS:   brew install --cask mactex"
    echo "  Ubuntu:  sudo apt install texlive-xetex texlive-fonts-recommended"
    exit 1
fi

# Check if xelatex is available for better PDF output
if command -v xelatex &> /dev/null; then
    PDF_ENGINE="--pdf-engine=xelatex"
    echo -e "${GREEN}✓ XeLaTeX found - using for better PDF formatting${NC}"
else
    PDF_ENGINE=""
    echo -e "${YELLOW}⚠ XeLaTeX not found - using default PDF engine${NC}"
    echo "  For better formatting, install: brew install --cask mactex (macOS)"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Change to project root for relative paths
cd "$PROJECT_ROOT"

echo -e "${BLUE}📄 Building documentation PDF...${NC}"

# Define the order of files to include
FILES=(
    "README.md"
    "docs/README.md"
    "docs/lua/README.md"
    "docs/lua/VSCodeintegration.md"
    "docs/lua/HTTPClient.md"
    "docs/lua/TCPSocket.md" 
    "docs/lua/UDPSocket.md"
    "docs/lua/WebSocket.md"
    "docs/lua/Timers.md"
    "docs/lua/Plua.md"
    "docs/lua/Fibaro.md"
    "docs/lua/QuickApp.md"
    "docs/lua/EmulatorQA.md"
    "docs/api/README.md"
    "docs/WEB_REPL_HTML_EXAMPLES.md"
)

# Check which files exist
EXISTING_FILES=()
MISSING_FILES=()

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        EXISTING_FILES+=("$file")
        echo -e "${GREEN}✓${NC} $file"
    else
        MISSING_FILES+=("$file")
        echo -e "${YELLOW}⚠${NC} $file (missing)"
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}⚠ Warning: ${#MISSING_FILES[@]} files not found, continuing with available files${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Running pandoc...${NC}"

# Get version from Python package for metadata
VERSION=$(python -c "from src.plua import __version__; print(__version__)" 2>/dev/null || echo "unknown")

# Run pandoc with comprehensive options
pandoc "${EXISTING_FILES[@]}" \
    --toc \
    --toc-depth=3 \
    $PDF_ENGINE \
    --metadata title="plua Documentation" \
    --metadata author="Jan Gabrielsson" \
    --metadata subject="Python-Lua async runtime documentation" \
    --metadata keywords="Python,Lua,async,runtime,timers,Fibaro,QuickApp" \
    --metadata version="v$VERSION" \
    --metadata date="$(date '+%Y-%m-%d')" \
    --variable geometry:margin=1in \
    --variable fontsize=11pt \
    --variable linkcolor=blue \
    --variable urlcolor=blue \
    --variable toccolor=black \
    --highlight-style=github \
    --standalone \
    -o "$OUTPUT_FILE"

# Check if PDF was created successfully
if [[ -f "$OUTPUT_FILE" ]]; then
    PDF_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo ""
    echo -e "${GREEN}✅ Success! PDF documentation created:${NC}"
    echo -e "   📄 File: $OUTPUT_FILE"
    echo -e "   📊 Size: $PDF_SIZE"
    echo -e "   📖 Pages: $(pdfinfo "$OUTPUT_FILE" 2>/dev/null | grep Pages | awk '{print $2}' || echo 'unknown')"
    echo ""
    
    # Offer to open the PDF
    if command -v open &> /dev/null; then  # macOS
        echo -e "${BLUE}💡 Open PDF? (y/n):${NC} "
        read -r response
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            open "$OUTPUT_FILE"
        fi
    elif command -v xdg-open &> /dev/null; then  # Linux
        echo -e "${BLUE}💡 Open PDF? (y/n):${NC} "
        read -r response  
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            xdg-open "$OUTPUT_FILE"
        fi
    fi
    
    echo -e "${GREEN}🎉 Documentation build complete!${NC}"
    
else
    echo -e "${RED}❌ Error: Failed to create PDF${NC}"
    exit 1
fi
