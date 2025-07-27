# plua Documentation Scripts

This directory contains scripts for generating PDF documentation from the project's markdown files.

## 📄 PDF Generation Scripts

### `create-docs-pdf.sh` - Comprehensive PDF Generator

A full-featured script that creates a professional PDF with:
- Table of contents with 3 levels
- Proper metadata (title, author, version, date)
- Syntax highlighting for code blocks
- Professional formatting with XeLaTeX (if available)
- Error checking and user feedback

**Usage:**
```bash
./scripts/create-docs-pdf.sh
```

**Output:** `dist/plua-documentation.pdf`

### `simple-pdf.sh` - Quick PDF Generator

A minimal script for basic PDF generation:
```bash
./scripts/simple-pdf.sh
```

**Output:** `plua-docs-simple.pdf` (in current directory)

## 📋 Requirements

### Install Pandoc

**macOS:**
```bash
brew install pandoc

# For better formatting (optional but recommended):
brew install --cask mactex
```

**Ubuntu/Debian:**
```bash
sudo apt install pandoc texlive-xetex texlive-fonts-recommended
```

**Windows:**
```bash
# Using Chocolatey
choco install pandoc miktex

# Or download from: https://pandoc.org/installing.html
```

**Other platforms:** See [pandoc installation guide](https://pandoc.org/installing.html)

## 📖 Generated Documentation Structure

The PDF includes all documentation in this order:

1. **Main README.md** - Project overview, installation, quick start
2. **docs/README.md** - Documentation index and navigation
3. **docs/lua/README.md** - Lua API overview and modules
4. **Lua API Documentation:**
   - VSCode Integration (`VSCodeintegration.md`)
   - HTTP Client (`HTTPClient.md`)
   - TCP/UDP Sockets (`TCPSocket.md`, `UDPSocket.md`)
   - WebSockets (`WebSocket.md`)
   - Timers (`Timers.md`)
   - PLUA utilities (`Plua.md`)
   - Fibaro API (`Fibaro.md`)
   - QuickApp API (`QuickApp.md`)
   - Emulator documentation (`EmulatorQA.md`)
5. **docs/api/README.md** - REST API documentation
6. **docs/WEB_REPL_HTML_EXAMPLES.md** - Web interface examples

## 🔧 Customization

### Modify File Order

Edit the `FILES` array in `create-docs-pdf.sh`:

```bash
FILES=(
    "README.md"
    "docs/README.md"
    # Add or remove files as needed
    "your-custom-doc.md"
)
```

### Custom Pandoc Options

The comprehensive script uses these pandoc options:
- `--toc --toc-depth=3` - Table of contents with 3 levels
- `--pdf-engine=xelatex` - Better PDF formatting (if available)
- `--highlight-style=github` - GitHub-style syntax highlighting
- `--variable geometry:margin=1in` - 1-inch margins
- Rich metadata for document properties

### Quick Customization

For simple customization, edit `simple-pdf.sh` with your preferred files and options.

## 🚀 Usage Examples

```bash
# Generate comprehensive documentation
./scripts/create-docs-pdf.sh

# Quick PDF for sharing
./scripts/simple-pdf.sh

# Custom pandoc command (example)
pandoc README.md docs/lua/*.md --toc -o my-custom-docs.pdf
```

## 🐛 Troubleshooting

### "pandoc: command not found"
Install pandoc using the instructions above.

### "xelatex: command not found" 
Install a LaTeX distribution:
- macOS: `brew install --cask mactex`
- Ubuntu: `sudo apt install texlive-xetex`
- Windows: Install MiKTeX from the website

### PDF generation fails
1. Check that all referenced markdown files exist
2. Ensure pandoc is properly installed
3. Try the simple script first: `./scripts/simple-pdf.sh`
4. Check for markdown syntax errors in source files

### Large images or formatting issues
- Images referenced with relative paths should work
- For the logo image, ensure `docs/Plua.png` exists
- Complex HTML in markdown may not render perfectly in PDF

## 💡 Tips

- **Preview first**: Test with `simple-pdf.sh` before running the full script
- **Check links**: Internal links between docs work best with relative paths
- **Image paths**: Use relative paths from the project root
- **File size**: The generated PDF typically ranges from 1-5 MB depending on content
- **Version info**: The comprehensive script automatically includes version from `src.plua.__version__`
