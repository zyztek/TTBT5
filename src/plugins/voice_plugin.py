"""Voice Plugin for TTBT5.

This plugin integrates advanced voice chat capabilities with blockchain features.
"""

import os
import sys
import time
from typing import Dict, Any, Optional, List

# Add the project root to the Python path when running as a script
if __name__ == "__main__":
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from src.ai.voice_chat import VoiceChat, VoiceChatConfig
from src.blockchain.polygon_nft import PolygonNFT

class VoicePlugin:
    """Voice plugin that integrates voice chat with blockchain features."""
    
    def __init__(self):
        """Initialize the voice plugin."""
        self.name = "voice_plugin"
        self.description = "Advanced voice chat with blockchain integration"
        self.version = "1.0.0"
        self.voice_chat = None
        self.polygon_nft = None
        self.config = {
            "tts_engine": "openai",  # Options: openai, elevenlabs, xtts, kokoro
            "stt_engine": "whisper",  # Options: whisper, faster_whisper
            "llm_provider": "openai",  # Options: openai, ollama, anthropic, xai
            "enable_streaming": True,
            "enable_interruption": True,
            "enable_sentiment_analysis": True,
            "enable_blockchain_integration": True,
            "supported_languages": ["en", "es", "fr", "de", "it"],
            "nft_auto_mint": False,
            "nft_contract_address": "",
            "api_keys": {
                "openai": "",
                "elevenlabs": "",
                "anthropic": ""
            }
        }
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        
    def on_load(self) -> None:
        """Called when the plugin is loaded."""
        print(f"Loading {self.name} plugin v{self.version}")
        
        # Initialize voice chat with config
        voice_config = VoiceChatConfig(
            openai_api_key=self.config["api_keys"].get("openai", ""),
            elevenlabs_api_key=self.config["api_keys"].get("elevenlabs", ""),
            anthropic_api_key=self.config["api_keys"].get("anthropic", ""),
            tts_engine=self.config["tts_engine"],
            stt_engine=self.config["stt_engine"],
            llm_provider=self.config["llm_provider"],
            enable_streaming=self.config["enable_streaming"],
            enable_interruption=self.config["enable_interruption"],
            enable_sentiment_analysis=self.config["enable_sentiment_analysis"],
            enable_blockchain_integration=self.config["enable_blockchain_integration"],
            supported_languages=self.config["supported_languages"],
            nft_contract_address=self.config["nft_contract_address"]
        )
        self.voice_chat = VoiceChat(config=voice_config)
        
        # Initialize blockchain integration if enabled
        if self.config["enable_blockchain_integration"]:
            # Get private key from config or use a placeholder for testing
            private_key = self.config.get("polygon_private_key", "0x0000000000000000000000000000000000000000000000000000000000000000")
            self.polygon_nft = PolygonNFT(private_key=private_key)
            if self.config["nft_contract_address"]:
                self.polygon_nft.connect_to_network()
                print(f"Connected to NFT contract at {self.config['nft_contract_address']}")
        
        return True
    
    def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        print(f"Unloading {self.name} plugin")
        # Clean up resources
        self.voice_chat = None
        self.polygon_nft = None
        return True
    
    def on_start(self) -> None:
        """Called when the plugin is started."""
        print(f"Starting {self.name} plugin")
        return True
    
    def on_stop(self) -> None:
        """Called when the plugin is stopped."""
        print(f"Stopping {self.name} plugin")
        return True
    
    def process_audio(self, audio_file_path: str, user_language: str = "en", 
                     enable_nft: bool = None) -> Dict[str, Any]:
        """Process audio file and generate response."""
        if not self.voice_chat:
            return {"status": "error", "message": "Voice chat not initialized"}
        
        # Use plugin config if enable_nft not specified
        if enable_nft is None:
            enable_nft = self.config["nft_auto_mint"]
        
        # Process voice message
        result = self.voice_chat.process_voice_message(
            audio_file_path=audio_file_path,
            user_language=user_language,
            enable_nft=enable_nft
        )
        
        # Store conversation in history
        conversation_id = result["conversation_id"]
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "timestamp": time.time(),
            "transcription": result["transcription"],
            "response": result["response_text"],
            "sentiment": result.get("sentiment", None)
        })
        
        # Mint NFT if enabled and metadata available
        if enable_nft and self.config["enable_blockchain_integration"] and result.get("nft_metadata"):
            if self.polygon_nft:
                nft_result = self.mint_conversation_nft(conversation_id, result["nft_metadata"])
                result["nft_result"] = nft_result
        
        return result
    
    def mint_conversation_nft(self, conversation_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Mint an NFT for the conversation."""
        if not self.polygon_nft:
            return {"status": "error", "message": "Polygon NFT not initialized"}
        
        print(f"Minting NFT for conversation: {conversation_id}")
        
        # Prepare metadata URI (would typically be uploaded to IPFS)
        metadata_uri = f"ipfs://mock-ipfs-hash-{conversation_id}"
        
        # Mint NFT
        result = self.polygon_nft.mint_nft(
            metadata={
                "token_uri": metadata_uri,
                "token_id": f"voice-{conversation_id}"
            },
            to_address="0xMockUserAddress"  # Would be replaced with actual user address
        )
        
        return result
    
    def get_conversation_history(self, conversation_id: str = None) -> Dict[str, Any]:
        """Get conversation history."""
        if conversation_id:
            if conversation_id in self.conversations:
                return {
                    "status": "success",
                    "conversation_id": conversation_id,
                    "history": self.conversations[conversation_id]
                }
            else:
                return {"status": "error", "message": f"Conversation {conversation_id} not found"}
        else:
            # Return all conversations
            return {
                "status": "success",
                "conversations": self.conversations
            }
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update plugin configuration."""
        # Update config
        for key, value in new_config.items():
            if key in self.config:
                if isinstance(self.config[key], dict) and isinstance(value, dict):
                    # Merge dictionaries for nested configs like api_keys
                    self.config[key].update(value)
                else:
                    self.config[key] = value
        
        # Reinitialize components if needed
        if any(key in new_config for key in ["tts_engine", "stt_engine", "llm_provider", 
                                           "enable_streaming", "enable_sentiment_analysis",
                                           "supported_languages", "api_keys"]):
            # Reinitialize voice chat with updated config
            voice_config = VoiceChatConfig(
                openai_api_key=self.config["api_keys"].get("openai", ""),
                elevenlabs_api_key=self.config["api_keys"].get("elevenlabs", ""),
                anthropic_api_key=self.config["api_keys"].get("anthropic", ""),
                tts_engine=self.config["tts_engine"],
                stt_engine=self.config["stt_engine"],
                llm_provider=self.config["llm_provider"],
                enable_streaming=self.config["enable_streaming"],
                enable_interruption=self.config["enable_interruption"],
                enable_sentiment_analysis=self.config["enable_sentiment_analysis"],
                enable_blockchain_integration=self.config["enable_blockchain_integration"],
                supported_languages=self.config["supported_languages"],
                nft_contract_address=self.config["nft_contract_address"]
            )
            self.voice_chat = VoiceChat(config=voice_config)
        
        # Reinitialize blockchain if needed
        if any(key in new_config for key in ["enable_blockchain_integration", "nft_contract_address", "polygon_private_key"]):
            if self.config["enable_blockchain_integration"]:
                # Get private key from config or use a placeholder for testing
                private_key = self.config.get("polygon_private_key", "0x0000000000000000000000000000000000000000000000000000000000000000")
                self.polygon_nft = PolygonNFT(private_key=private_key)
                if self.config["nft_contract_address"]:
                    self.polygon_nft.connect_to_network()
            else:
                self.polygon_nft = None
        
        return {"status": "success", "config": self.config}


if __name__ == "__main__":
    # Simple test when running the script directly
    print("Initializing Voice Plugin...")
    plugin = VoicePlugin()
    plugin.on_load()
    print("Voice Plugin initialized successfully!")
    print(f"Plugin name: {plugin.name}")
    print(f"Plugin version: {plugin.version}")
    print(f"Plugin description: {plugin.description}")
    print("\nConfiguration:")
    for key, value in plugin.config.items():
        if key == "api_keys":
            print(f"  {key}: [API keys hidden]")
        else:
            print(f"  {key}: {value}")
    print("\nUnloading plugin...")
    plugin.on_unload()
    print("Plugin unloaded successfully!")