#!/bin/bash
set -e

# Generar documentación HTML
echo "Generando documentación HTML..."
sphinx-build -b html ./docs/source ./docs/build/html

# Generar documentación LaTeX
echo "Generando documentación LaTeX..."
sphinx-build -b latex ./docs/source ./docs/build/latex

# Compilar PDF con pdflatex
echo "Compilando PDF..."
cd docs/build/latex
make
cd ../../../..

# Copiar el PDF generado a la raíz de docs
cp docs/build/latex/ttbt2.pdf docs/ttbt2_final_report.pdf

echo "¡PDF finalizado! El archivo se encuentra en docs/ttbt2_final_report.pdf"
