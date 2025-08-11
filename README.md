# TTBT5 Application

This is a Python application based on the TTBT2 comprehensive plan, featuring advanced AI voice chat capabilities with blockchain integration.

## Project Structure

```
ttbt5/
├── app.py                # Main application file
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── src/                  # Source code directory
│   ├── __init__.py       # Package initializer
│   ├── __main__.py       # Package entry point
│   ├── core.py           # Core application logic
│   ├── main.py           # Main entry point
│   ├── ai/               # AI components
│   │   ├── voice_chat.py # Voice chat with sentiment analysis
│   │   └── multilingual.py # Multilingual support
│   ├── blockchain/       # Blockchain components
│   │   ├── polygon_nft.py # NFT minting on Polygon
│   │   ├── dao_governance.py # DAO governance
│   │   └── polkadot_crosschain.py # Cross-chain transfers
│   ├── infra/            # Infrastructure components
│   │   ├── kubernetes.py # Kubernetes orchestration
│   │   └── auto_scaling.py # Auto-scaling logic
│   └── plugins/          # Plugin system
│       ├── voice_plugin.py # Voice chat plugin with NFT integration
│       └── ar_plugin.py # Augmented reality plugin
├── tests/                # Test files
└── docs/                 # Documentation
```

## Getting Started

### Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install the application as a package (optional):
   ```
   pip install -e .
   ```

### Running the Application

You can run the application in several ways:

1. Direct execution:
   ```
   python app.py
   ```

2. Using the package module:
   ```
   python -m src
   ```

3. Using the installed console script (if installed as package):
   ```
   ttbt5
   ```

## Development

### Running Tests

To run the tests:
```
python -m unittest tests/test_app.py
```

## Features

### AI Voice Chat

The application includes advanced voice chat capabilities:

- Real-time speech-to-text using multiple engines (Whisper, Google, etc.)
- Text-to-speech with various providers (ElevenLabs, OpenAI, etc.)
- Sentiment analysis of conversations
- Multilingual support for 5+ languages
- Streaming responses for natural conversations

### Blockchain Integration

- NFT minting of voice conversations on Polygon
- DAO governance for community decision-making
- Cross-chain asset transfers via Polkadot

### Plugin System

The application features a flexible plugin system that allows extending functionality:

- Voice Plugin: Integrates voice chat with blockchain for NFT creation
- AR Plugin: Augmented reality features (in development)

### Infrastructure

- Kubernetes deployment and orchestration
- Auto-scaling based on demand
- Multi-cloud deployment support

## Requirements

This application requires Python 3.6 or higher.
