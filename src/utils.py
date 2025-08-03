#!/usr/bin/env python3
"""
Utility module for the TTBT5 Application.
This module provides utility functions for the application.
"""

import os
import json
from typing import Any, Dict, List, Union

def format_output(data: Any, format_type: str = "json") -> str:
    """Format output in a specific format."""
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "text":
        return str(data)
    else:
        return str(data)

def get_file_content(file_path: str) -> str:
    """Get the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

def write_file_content(file_path: str, content: str) -> bool:
    """Write content to a file."""
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def parse_input(input_str: str) -> Any:
    """Parse input string to appropriate data type."""
    # Try to parse as JSON
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        # If it's not valid JSON, return as is
        return input_str
    except Exception:
        return input_str
