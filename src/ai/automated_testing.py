"""
Automated Testing Module for TTBT5.
Handles automated testing and validation of AI features.
"""

import json
import unittest
from typing import Dict, Any, List
from src.ai.voice_chat import VoiceChat
from src.ai.multilingual import MultilingualSupport

class AutomatedTesting:
    """Handles automated testing and validation of AI features."""
    
    def __init__(self):
        """Initialize the automated testing manager."""
        self.test_results = []
        self.voice_chat = VoiceChat()
        self.multilingual = MultilingualSupport()
        
    def run_voice_chat_tests(self):
        """Run automated tests for voice chat functionality."""
        print("Running voice chat tests...")
        
        # Test 1: Audio transcription
        print("Test 1: Audio transcription")
        try:
            transcription = self.voice_chat.transcribe_audio("/tmp/sample_audio.mp3", "en")
            test_result = {
                "test": "Audio transcription",
                "status": "passed",
                "details": f"Transcription: {transcription}"
            }
        except Exception as e:
            test_result = {
                "test": "Audio transcription",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        # Test 2: Response generation
        print("Test 2: Response generation")
        try:
            response = self.voice_chat.generate_response("Hello, how are you?", "en")
            test_result = {
                "test": "Response generation",
                "status": "passed",
                "details": f"Response: {response}"
            }
        except Exception as e:
            test_result = {
                "test": "Response generation",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        # Test 3: Speech synthesis
        print("Test 3: Speech synthesis")
        try:
            audio_path = self.voice_chat.synthesize_speech("Hello, how are you?", "en")
            test_result = {
                "test": "Speech synthesis",
                "status": "passed",
                "details": f"Audio saved to: {audio_path}"
            }
        except Exception as e:
            test_result = {
                "test": "Speech synthesis",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        # Test 4: Complete voice message processing
        print("Test 4: Complete voice message processing")
        try:
            result = self.voice_chat.process_voice_message("/tmp/sample_audio.mp3", "en")
            test_result = {
                "test": "Complete voice message processing",
                "status": "passed",
                "details": f"Result: {result}"
            }
        except Exception as e:
            test_result = {
                "test": "Complete voice message processing",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        return [r for r in self.test_results if r["test"].startswith("Audio transcription") or 
                r["test"].startswith("Response generation") or 
                r["test"].startswith("Speech synthesis") or 
                r["test"].startswith("Complete voice message processing")]
    
    def run_multilingual_tests(self):
        """Run automated tests for multilingual support."""
        print("Running multilingual tests...")
        
        # Test 1: Language support
        print("Test 1: Language support")
        try:
            languages = self.multilingual.get_supported_languages()
            test_result = {
                "test": "Language support",
                "status": "passed",
                "details": f"Supported languages: {languages}"
            }
        except Exception as e:
            test_result = {
                "test": "Language support",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        # Test 2: Text translation
        print("Test 2: Text translation")
        try:
            translated = self.multilingual.translate_text("Welcome to TTBT5", "en", "es")
            test_result = {
                "test": "Text translation",
                "status": "passed",
                "details": f"Translated text: {translated}"
            }
        except Exception as e:
            test_result = {
                "test": "Text translation",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        # Test 3: Text localization
        print("Test 3: Text localization")
        try:
            localized = self.multilingual.localize_text("welcome", "fr")
            test_result = {
                "test": "Text localization",
                "status": "passed",
                "details": f"Localized text: {localized}"
            }
        except Exception as e:
            test_result = {
                "test": "Text localization",
                "status": "failed",
                "details": f"Error: {str(e)}"
            }
        self.test_results.append(test_result)
        
        return [r for r in self.test_results if r["test"].startswith("Language support") or 
                r["test"].startswith("Text translation") or 
                r["test"].startswith("Text localization")]
    
    def run_all_tests(self):
        """Run all automated tests."""
        print("Running all automated tests...")
        
        # Run voice chat tests
        voice_tests = self.run_voice_chat_tests()
        
        # Run multilingual tests
        multilingual_tests = self.run_multilingual_tests()
        
        # Combine all test results
        all_tests = voice_tests + multilingual_tests
        
        # Calculate summary
        passed = len([t for t in all_tests if t["status"] == "passed"])
        failed = len([t for t in all_tests if t["status"] == "failed"])
        
        summary = {
            "total_tests": len(all_tests),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(all_tests)) * 100 if all_tests else 0
        }
        
        return {
            "test_results": all_tests,
            "summary": summary
        }
    
    def generate_test_report(self):
        """Generate a detailed test report."""
        test_data = self.run_all_tests()
        
        report = f"""
TTBT5 AI Features - Automated Test Report
=========================================

Summary:
- Total Tests: {test_data['summary']['total_tests']}
- Passed: {test_data['summary']['passed']}
- Failed: {test_data['summary']['failed']}
- Success Rate: {test_data['summary']['success_rate']:.2f}%

Detailed Results:
"""
        
        for result in test_data["test_results"]:
            status_symbol = "✓" if result["status"] == "passed" else "✗"
            report += f"\n{status_symbol} {result['test']}: {result['status']}\n"
            report += f"  Details: {result['details']}\n"
        
        return report

# Example usage (for testing)
if __name__ == "__main__":
    # Create automated testing manager
    tester = AutomatedTesting()
    
    # Run all tests and generate report
    report = tester.generate_test_report()
    print(report)
    
    # Save report to file
    with open("/tmp/ai_test_report.txt", "w") as f:
        f.write(report)
    
    print("Test report saved to /tmp/ai_test_report.txt")
