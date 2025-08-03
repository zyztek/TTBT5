"""
Multilingual Support Module for TTBT5.
Handles translation and localization for 5 languages.
"""

import json
from typing import Dict, Any

class MultilingualSupport:
    """Handles multilingual support for the TTBT5 application."""
    
    def __init__(self):
        """Initialize the multilingual support manager."""
        self.supported_languages: Dict[str, str] = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian"
        }
        self.translations = self._load_translations()
        
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translations from a JSON file or database."""
        # TODO: Implement actual translation loading
        # This would typically load from a file or database
        # For now, we'll use mock translations
        return {
            "en": {
                "welcome": "Welcome to TTBT5",
                "status": "Status",
                "help": "Help",
                "config": "Configuration",
                "info": "Information"
            },
            "es": {
                "welcome": "Bienvenido a TTBT5",
                "status": "Estado",
                "help": "Ayuda",
                "config": "Configuración",
                "info": "Información"
            },
            "fr": {
                "welcome": "Bienvenue à TTBT5",
                "status": "Statut",
                "help": "Aide",
                "config": "Configuration",
                "info": "Information"
            },
            "de": {
                "welcome": "Willkommen bei TTBT5",
                "status": "Status",
                "help": "Hilfe",
                "config": "Konfiguration",
                "info": "Information"
            },
            "it": {
                "welcome": "Benvenuto in TTBT5",
                "status": "Stato",
                "help": "Aiuto",
                "config": "Configurazione",
                "info": "Informazioni"
            }
        }
    
    def translate_text(self, text: str, source_language: str, target_language: str) -> str:
        """Translate text from source language to target language."""
        print(f"Translating text from {source_language} to {target_language}: {text}")
        # TODO: Implement actual translation
        # This would typically use a translation API or library
        # For now, we'll use mock translations
        
        # Find the key for the text in the source language
        key = None
        for k, v in self.translations.get(source_language, {}).items():
            if v == text:
                key = k
                break
        
        # If we found the key, get the translation in the target language
        if key and key in self.translations.get(target_language, {}):
            translated_text = self.translations[target_language][key]
        else:
            # Fallback to the original text
            translated_text = text
            
        return translated_text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get a list of supported languages."""
        return self.supported_languages
    
    def get_language_name(self, language_code: str) -> str:
        """Get the full name of a language by its code."""
        return self.supported_languages.get(language_code, "Unknown")
    
    def localize_text(self, key: str, language: str) -> str:
        """Get localized text for a specific key and language."""
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        elif key in self.translations["en"]:
            # Fallback to English
            return self.translations["en"][key]
        else:
            # Fallback to the key itself
            return key
    
    def add_translation(self, key: str, translations: Dict[str, str]) -> None:
        """Add a new translation for a key."""
        for language, text in translations.items():
            if language in self.translations:
                self.translations[language][key] = text
            else:
                self.translations[language] = {key: text}

# Example usage (for testing)
if __name__ == "__main__":
    # Create multilingual support manager
    multilingual = MultilingualSupport()
    
    # Get supported languages
    languages = multilingual.get_supported_languages()
    print(f"Supported languages: {languages}")
    
    # Translate text
    translated = multilingual.translate_text("Welcome to TTBT5", "en", "es")
    print(f"Translated text: {translated}")
    
    # Localize text
    localized = multilingual.localize_text("welcome", "fr")
    print(f"Localized text: {localized}")
    
    # Add a new translation
    multilingual.add_translation("goodbye", {
        "en": "Goodbye",
        "es": "Adiós",
        "fr": "Au revoir",
        "de": "Auf Wiedersehen",
        "it": "Arrivederci"
    })
    
    # Use the new translation
    localized_goodbye = multilingual.localize_text("goodbye", "it")
    print(f"Localized goodbye: {localized_goodbye}")
