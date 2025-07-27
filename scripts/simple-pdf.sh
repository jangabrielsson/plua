#!/bin/bash
# simple-pdf.sh - Quick PDF generation with minimal dependencies

# Simple pandoc command for basic PDF generation
pandoc README.md docs/README.md docs/lua/README.md docs/lua/*.md docs/api/README.md \
    --toc \
    --metadata title="plua Documentation" \
    --metadata author="Jan Gabrielsson" \
    -o plua-docs-simple.pdf

echo "✅ Simple PDF created: plua-docs-simple.pdf"
