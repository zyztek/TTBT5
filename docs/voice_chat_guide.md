# Voice Chat Feature Guide

## Overview

The Voice Chat feature in TTBT5 provides advanced voice interaction capabilities with blockchain integration. It allows users to have natural conversations with AI, analyze sentiment, and even mint NFTs from their conversations.

## Key Components

### VoiceChat Class

The core `VoiceChat` class in `src/ai/voice_chat.py` handles:

- Speech-to-text transcription using multiple engines
- Text generation using various LLM providers
- Text-to-speech synthesis
- Sentiment analysis
- NFT metadata generation

### VoicePlugin

The `VoicePlugin` in `src/plugins/voice_plugin.py` integrates voice chat with the plugin system and adds:

- Blockchain integration for minting conversation NFTs
- Configuration management
- Conversation history tracking

## Usage Examples

### Basic Voice Processing

```python
from src.ai.voice_chat import VoiceChat, VoiceChatConfig

# Create configuration
config = VoiceChatConfig(
    openai_api_key="your_openai_key",
    elevenlabs_api_key="your_elevenlabs_key",
    anthropic_api_key="your_anthropic_key",
    stt_engine="whisper",
    tts_engine="elevenlabs",
    llm_provider="openai",
    nft_contract_address="your_contract_address",
    polygon_private_key="your_polygon_key",
    polygon_network="mumbai"
)

# Initialize voice chat
voice_chat = VoiceChat(config=config)

# Or load from config file
voice_chat = VoiceChat(config_path="path/to/voice_chat_config.json")

# Process a voice message
result = voice_chat.process_voice_message(
    audio_file_path="path/to/audio.mp3",
    user_language="en"
)

print(f"Transcription: {result['transcription']}")
print(f"Response: {result['response']}")
```

### Using the Voice Plugin

```python
from src.plugins.voice_plugin import VoicePlugin

# Create and initialize plugin
plugin = VoicePlugin()
plugin.on_load()

# Configure the plugin
plugin.update_config({
    "api_keys": {
        "openai": "your_openai_key",
        "elevenlabs": "your_elevenlabs_key",
        "anthropic": "your_anthropic_key"
    },
    "enable_blockchain_integration": True,
    "nft_contract_address": "your_contract_address",
    "polygon_private_key": "your_polygon_key",
    "polygon_network": "mumbai"
})

# Process audio
result = plugin.process_audio(
    audio_file_path="path/to/audio.mp3",
    user_language="en",
    enable_nft=True
)

# Clean up
plugin.on_unload()
```

### Using the TTBT5App

```python
from src.core import TTBT5App

# Create app
app = TTBT5App()

# Process voice message
result = app.process_voice_message(
    audio_file_path="path/to/audio.mp3",
    user_language="en",
    enable_nft=True
)
```

## Command Line Usage

You can also use the voice chat features from the command line:

```bash
# Transcribe audio
python -m src transcribe_audio path/to/audio.mp3 en

# Process complete voice message
python -m src process_voice_message path/to/audio.mp3 en

# Analyze voice sentiment
python -m src analyze_voice_sentiment path/to/audio.mp3 en
```

## Blockchain Integration

The voice chat system can integrate with blockchain to mint NFTs from conversations:

1. Enable blockchain integration in the configuration
2. Process a voice message with `enable_nft=True`
3. The system will generate NFT metadata including:
   - Conversation transcript
   - Sentiment analysis
   - Timestamp and unique identifiers
4. The NFT is minted on the Polygon blockchain

## Supported Engines

### Speech-to-Text (STT)
- Whisper (OpenAI)
- Google Speech Recognition
- Azure Speech Services

### Large Language Models (LLM)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models via Ollama

### Text-to-Speech (TTS)
- ElevenLabs
- OpenAI TTS
- Google Text-to-Speech
- Local TTS engines

## Configuration Options

The `VoiceChatConfig` class supports numerous configuration options:

- API keys for various services (OpenAI, ElevenLabs, Anthropic)
- Engine selection for STT, LLM, and TTS
- Streaming options
- Sentiment analysis toggle
- Blockchain integration settings (NFT contract address, Polygon private key, network)
- Conversation history limit
- Supported languages

You can set these options directly in code or load them from a configuration file using `VoiceChatConfig.from_file()` or by passing a `config_path` to the `VoiceChat` constructor.

See the `VoiceChatConfig` class in `src/ai/voice_chat.py` for all available options and the `config/voice_chat_config.json` file for an example configuration.