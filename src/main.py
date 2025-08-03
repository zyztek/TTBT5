#!/usr/bin/env python3
"""
Main entry point for the TTBT5 Application.
This serves as the main entry point for the application.
"""

import sys
from src.core import TTBT5App

def main():
    """Main function to run the application."""
    try:
        app = TTBT5App()
        print("TTBT5 Application")
        print("Status: Running")
        
        # If command line arguments are provided, treat them as commands
        if len(sys.argv) > 1:
            command = sys.argv[1]
            args = sys.argv[2:] if len(sys.argv) > 2 else []
            
            # Execute the command
            app.run_command(command, *args)
        else:
            print("Application started successfully.")
            print("Available commands: status, help, config, info")
            print("Use 'ttbt5 <command>' to run a specific command.")
        
        return 0
    except Exception as e:
        print(f"Error running application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
