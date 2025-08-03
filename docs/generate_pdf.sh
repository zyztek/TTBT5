#!/bin/bash

# Script para generar el PDF de documentación de TTBT2
# Requiere Sphinx y LaTeX instalados

set -e

echo "Generando documentación PDF para TTBT2..."

# Directorio de trabajo
DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$DOCS_DIR/source"
BUILD_DIR="$DOCS_DIR/build"
PDF_DIR="$BUILD_DIR/pdf"

# Crear directorios si no existen
mkdir -p "$PDF_DIR"

# Verificar dependencias
echo "Verificando dependencias..."

if ! command -v sphinx-build &> /dev/null; then
    echo "Error: sphinx-build no encontrado. Por favor instale Sphinx:"
    echo "pip install sphinx"
    exit 1
fi

if ! command -v pdflatex &> /dev/null; then
    echo "Error: pdflatex no encontrado. Por favor instale LaTeX:"
    echo "Ubuntu/Debian: sudo apt-get install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended"
    echo "macOS: brew install --cask mactex"
    exit 1
fi

# Generar documentación en LaTeX
echo "Generando documentación en LaTeX..."
sphinx-build -b latex "$SOURCE_DIR" "$PDF_DIR"

# Compilar PDF usando LaTeX
echo "Compilando PDF..."
cd "$PDF_DIR"

# El proceso de compilación puede requerir múltiples pasos para resolver referencias
pdflatex -interaction=nonstopmode ttbt2.tex || true
pdflatex -interaction=nonstopmode ttbt2.tex || true

# Verificar que el PDF se generó correctamente
if [ -f "ttbt2.pdf" ]; then
    echo "PDF generado exitosamente: $PDF_DIR/ttbt2.pdf"
    
    # Copiar el PDF al directorio raíz de documentos
    cp ttbt2.pdf "$DOCS_DIR/ttbt2_final_documentation.pdf"
    echo "PDF copiado a: $DOCS_DIR/ttbt2_final_documentation.pdf"
else
    echo "Error: No se pudo generar el PDF"
    exit 1
fi

echo "Proceso completado exitosamente!"
