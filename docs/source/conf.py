# Configuration file for the Sphinx documentation builder.

project = 'TTBT2 Final Report'
copyright = '2024, TTBT2 Team'
author = 'TTBT2 Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.graphviz',
    'sphinxcontrib.mermaid'
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Mermaid configuration
mermaid_output_format = 'raw'
mermaid_version = '10.9.1'
