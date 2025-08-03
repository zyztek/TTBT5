# Test file for TTBT5 Application
# Basic tests for the TTBT5 application

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core import TTBT5App

class TestTTBT5App(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = TTBT5App()
    
    def test_app_initialization(self):
        """Test that the application initializes correctly."""
        self.assertIsInstance(self.app, TTBT5App)
        self.assertIsNotNone(self.app.logger)
        self.assertIsNotNone(self.app.config)
        self.assertIsNotNone(self.app.command_processor)
    
    def test_get_status(self):
        """Test the get_status method."""
        status = self.app.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("version", status)
        self.assertIn("start_time", status)
        self.assertIn("features", status)
        self.assertEqual(status["status"], "running")
    
    def test_get_info(self):
        """Test the get_info method."""
        info = self.app.get_info()
        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("features", info)
        self.assertIn("start_time", info)
        self.assertIn("status", info)
        self.assertEqual(info["status"], "running")
    
    def test_show_config(self):
        """Test the show_config method."""
        # This test just ensures the method runs without error
        # and returns a dictionary
        config = self.app.show_config()
        self.assertIsInstance(config, dict)

if __name__ == '__main__':
    unittest.main()
