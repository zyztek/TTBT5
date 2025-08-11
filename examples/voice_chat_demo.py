#!/usr/bin/env python3
"""
Voice Chat Demo for TTBT5

This script demonstrates the voice chat capabilities of TTBT5 with blockchain integration.
It shows how to use the VoiceChat class directly or through the VoicePlugin.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.voice_chat import VoiceChat, VoiceChatConfig
from src.plugins.voice_plugin import VoicePlugin
from src.core import TTBT5App


def demo_direct_voice_chat(audio_file, language="en", enable_nft=False):
    """Demonstrate using VoiceChat class directly."""
    print("\n=== Direct VoiceChat Demo ===")
    
    # Create a configuration
    config = VoiceChatConfig(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        elevenlabs_api_key=os.environ.get("ELEVENLABS_API_KEY", ""),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        stt_engine="whisper",
        tts_engine="elevenlabs",
        llm_provider="openai",
        enable_streaming=True,
        enable_sentiment_analysis=True,
        enable_blockchain_integration=enable_nft,
        nft_contract_address=os.environ.get("NFT_CONTRACT_ADDRESS", ""),
        polygon_private_key=os.environ.get("POLYGON_PRIVATE_KEY", ""),
        polygon_network=os.environ.get("POLYGON_NETWORK", "mumbai")
    )
    
    # Create VoiceChat instance
    voice_chat = VoiceChat(config=config)
    
    # Process the voice message
    print(f"Processing audio file: {audio_file}")
    result = voice_chat.process_voice_message(
        audio_file_path=audio_file,
        user_language=language,
        enable_nft=enable_nft
    )
    
    # Display results
    print(f"Transcription: {result['transcription']}")
    print(f"Response: {result['response']}")
    
    if 'sentiment_scores' in result:
        print("\nSentiment Analysis:")
        for emotion, score in result['sentiment_scores'].items():
            print(f"  {emotion}: {score:.2f}")
    
    if enable_nft and 'nft_metadata' in result:
        print("\nNFT Metadata:")
        for key, value in result['nft_metadata'].items():
            print(f"  {key}: {value}")
    
    return result


def demo_voice_plugin(audio_file, language="en", enable_nft=False):
    """Demonstrate using the VoicePlugin."""
    print("\n=== VoicePlugin Demo ===")
    
    # Create and initialize the plugin
    voice_plugin = VoicePlugin()
    voice_plugin.on_load()
    
    # Configure the plugin
    plugin_config = {
        "api_keys": {
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "elevenlabs": os.environ.get("ELEVENLABS_API_KEY", ""),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY", "")
        },
        "enable_blockchain_integration": enable_nft,
        "nft_contract_address": os.environ.get("NFT_CONTRACT_ADDRESS", "")
    }
    voice_plugin.update_config(plugin_config)
    
    # Process audio
    print(f"Processing audio file: {audio_file}")
    result = voice_plugin.process_audio(
        audio_file_path=audio_file,
        user_language=language,
        enable_nft=enable_nft
    )
    
    # Display results
    print(f"Transcription: {result['transcription']}")
    print(f"Response: {result['response']}")
    
    if 'sentiment_scores' in result:
        print("\nSentiment Analysis:")
        for emotion, score in result['sentiment_scores'].items():
            print(f"  {emotion}: {score:.2f}")
    
    if enable_nft and 'nft_data' in result:
        print("\nNFT Data:")
        for key, value in result['nft_data'].items():
            print(f"  {key}: {value}")
    
    # Clean up
    voice_plugin.on_unload()
    
    return result


def demo_app_integration(audio_file, language="en", enable_nft=False):
    """Demonstrate using the TTBT5App integration."""
    print("\n=== TTBT5App Integration Demo ===")
    
    # Create the app
    app = TTBT5App()
    
    # Process voice message through the app
    print(f"Processing audio file: {audio_file}")
    result = app.process_voice_message(
        audio_file_path=audio_file,
        user_language=language,
        enable_nft=enable_nft
    )
    
    # Display results
    print(f"Transcription: {result['transcription']}")
    print(f"Response: {result['response']}")
    
    if 'sentiment_scores' in result:
        print("\nSentiment Analysis:")
        for emotion, score in result['sentiment_scores'].items():
            print(f"  {emotion}: {score:.2f}")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="TTBT5 Voice Chat Demo")
    parser.add_argument("--audio", "-a", required=True, help="Path to audio file")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--nft", "-n", action="store_true", help="Enable NFT creation")
    parser.add_argument("--mode", "-m", choices=["direct", "plugin", "app", "all"], 
                        default="all", help="Demo mode")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file '{args.audio}' not found")
        return 1
    
    if args.mode in ["direct", "all"]:
        demo_direct_voice_chat(args.audio, args.language, args.nft)
    
    if args.mode in ["plugin", "all"]:
        demo_voice_plugin(args.audio, args.language, args.nft)
    
    if args.mode in ["app", "all"]:
        demo_app_integration(args.audio, args.language, args.nft)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())