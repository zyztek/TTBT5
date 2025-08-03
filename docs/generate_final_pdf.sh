#!/bin/bash
set -e

# Install required packages
pip install sphinx sphinx-rtd-theme graphviz weasyprint

# Generate DOT diagrams from the root directory
dot -Tpng docs/architecture.dot -o docs/source/architecture.png
dot -Tpng docs/multi_cloud.dot -o docs/source/multi_cloud.png

# Generate HTML documentation
sphinx-build -b html ./docs/source ./docs/build/html

# Convert to PDF using weasyprint
weasyprint ./docs/build/html/index.html docs/ttbt2_final_report.pdf

echo "PDF generado exitosamente en docs/ttbt2_final_report.pdf"
