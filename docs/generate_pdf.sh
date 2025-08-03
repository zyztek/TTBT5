#!/bin/bash
set -e

# Install required packages
pip install sphinx sphinx-rtd-theme graphviz

# Generate DOT diagrams
dot -Tpng docs/architecture.dot -o docs/architecture.png
dot -Tpng docs/multi_cloud.dot -o docs/multi_cloud.png

# Create docs/source directory if it doesn't exist
mkdir -p docs/source

# Move markdown file to source directory
cp docs/ttbt2_final_report.md docs/source/index.md

# Create basic conf.py for Sphinx
cat > docs/source/conf.py << EOF
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinxcontrib.mermaid'
]

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
EOF

# Generate HTML documentation
sphinx-build -b html ./docs/source ./docs/html

# Convert to PDF using weasyprint (more reliable than pandoc for this)
pip install weasyprint
weasyprint ./docs/html/index.html docs/ttbt2_final_report.pdf

