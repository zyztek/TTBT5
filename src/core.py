#!/usr/bin/env python3
"""
Core module for the TTBT5 Application.
This module contains the main application logic.
"""

import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from src.config import get_config
from src.logger import get_logger
from src.commands import CommandProcessor
from src.plugin_manager import PluginManager

@dataclass
class ApplicationState:
    """Represents the application state."""
    start_time: datetime
    version: str = "1.0.0"
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        self.features.append("core")

class TTBT5App:
    """Main application class."""
    
    def __init__(self):
        # Initialize logger
        self.logger = get_logger()
        self.logger.info("Initializing TTBT5 Application")
        
        # Initialize config
        self.config = get_config()
        self.logger.info("Configuration loaded")
        
        # Initialize command processor
        self.command_processor = CommandProcessor(self.logger)
        self.register_commands()
        
        # Initialize plugin manager
        self.plugin_manager = PluginManager()
        self.logger.info("Plugin manager initialized")
        
        # Initialize state
        self.state = ApplicationState(
            start_time=datetime.now(),
            version=self.config.get("version", "1.0.0")
        )
        
        self.logger.info("TTBT5 Application initialized successfully")
    
    def register_commands(self):
        """Register available commands."""
        # General commands
        self.command_processor.register_command("status", self.get_status)
        self.command_processor.register_command("help", self.show_help)
        self.command_processor.register_command("config", self.show_config)
        self.command_processor.register_command("info", self.get_info)
        self.command_processor.register_command("load_plugin", self.load_plugin)
        self.command_processor.register_command("exec_hook", self.execute_hook)
        
        # Blockchain commands
        self.command_processor.register_command("mint_nft", self.mint_nft)
        self.command_processor.register_command("transfer_nft", self.transfer_nft)
        self.command_processor.register_command("cross_chain_transfer", self.cross_chain_transfer)
        self.command_processor.register_command("create_dao_proposal", self.create_dao_proposal)
        self.command_processor.register_command("vote_on_proposal", self.vote_on_proposal)
        
        # AI commands
        self.command_processor.register_command("transcribe_audio", self.transcribe_audio)
        self.command_processor.register_command("generate_response", self.generate_response)
        self.command_processor.register_command("process_voice_message", self.process_voice_message)
        self.command_processor.register_command("analyze_voice_sentiment", self.analyze_voice_sentiment)
        self.command_processor.register_command("translate_text", self.translate_text)
        
        # Infrastructure commands
        self.command_processor.register_command("deploy_to_cloud", self.deploy_to_cloud)
        self.command_processor.register_command("scale_deployment", self.scale_deployment)
        self.command_processor.register_command("auto_scale", self.auto_scale)
    
    def get_status(self) -> Dict:
        """Get the current application status."""
        return {
            "status": "running",
            "version": self.state.version,
            "start_time": self.state.start_time.isoformat(),
            "features": self.state.features
        }
    
    def show_help(self):
        """Show help information."""
        help_text = """
TTBT5 Application Help
======================

Available commands:
- status: Show application status
- help: Show this help message
- config: Show current configuration
- load_plugin <path>: Load a plugin from the specified file path
- exec_hook <hook_name> [args...]: Execute a plugin hook by name with optional arguments

For more information, please refer to the documentation.
        """
        print(help_text)
        return help_text
    
    def show_config(self):
        """Show current configuration."""
        config_data = self.config.config
        print("Current Configuration:")
        for key, value in config_data.items():
            print(f"  {key}: {value}")
        return config_data
    
    def get_info(self) -> Dict:
        """Get detailed application information."""
        info = {
            "name": self.config.get("app_name"),
            "version": self.config.get("version"),
            "features": self.state.features,
            "start_time": self.state.start_time.isoformat(),
            "status": "running"
        }
        print("Application Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        return info
    
    def load_plugin(self, plugin_path: str):
        """Load a plugin from the given file path."""
        self.logger.info(f"Loading plugin from {plugin_path}")
        self.plugin_manager.load_plugin(plugin_path)
        self.logger.info(f"Plugin loaded from {plugin_path}")
        return f"Plugin loaded from {plugin_path}"
    
    def execute_hook(self, hook_name: str, *args):
        """Execute a plugin hook by name with optional arguments."""
        self.logger.info(f"Executing hook {hook_name} with args {args}")
        result = self.plugin_manager.execute_hook(hook_name, *args)
        self.logger.info(f"Hook {hook_name} executed with result: {result}")
        return result
    
    def run_command(self, command: str, *args, **kwargs):
        """Run a command."""
        try:
            self.logger.info(f"Executing command: {command}")
            result = self.command_processor.execute_command(command, *args, **kwargs)
            self.logger.info(f"Command {command} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            raise

    # Blockchain commands
    def mint_nft(self, metadata: Dict[str, Any], to_address: str) -> Dict[str, Any]:
        """Mint an NFT using Polygon blockchain."""
        from src.blockchain.polygon_nft import PolygonNFT
        polygon_nft = PolygonNFT(self.config.get("polygon_private_key"))
        return polygon_nft.mint_nft(metadata, to_address)

    def transfer_nft(self, token_id: int, to_address: str) -> Dict[str, Any]:
        """Transfer an NFT to another address."""
        from src.blockchain.polygon_nft import PolygonNFT
        polygon_nft = PolygonNFT(self.config.get("polygon_private_key"))
        return polygon_nft.transfer_nft(token_id, to_address)

    def cross_chain_transfer(self, amount: float, to_chain: str, to_address: str, asset_id: str = "DOT") -> Dict[str, Any]:
        """Transfer assets between chains using Polkadot."""
        from src.blockchain.polkadot_crosschain import PolkadotCrossChain
        polkadot = PolkadotCrossChain(self.config.get("polkadot_private_key"))
        return polkadot.transfer_assets(amount, to_chain, to_address, asset_id)

    def create_dao_proposal(self, title: str, description: str, voting_duration: int) -> Dict[str, Any]:
        """Create a DAO governance proposal."""
        from src.blockchain.dao_governance import DAOGovernance
        dao = DAOGovernance(self.config.get("dao_contract_address"), self.config.get("dao_private_key"))
        return dao.create_proposal(title, description, voting_duration, self.config.get("proposer_address"))

    def vote_on_proposal(self, proposal_id: int, support: bool) -> Dict[str, Any]:
        """Vote on a DAO proposal."""
        from src.blockchain.dao_governance import DAOGovernance
        dao = DAOGovernance(self.config.get("dao_contract_address"), self.config.get("dao_private_key"))
        return dao.vote_on_proposal(proposal_id, self.config.get("voter_address"), support)

    # AI commands
    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> str:
        """Transcribe audio using Whisper."""
        from src.ai.voice_chat import VoiceChat, VoiceChatConfig
        
        # Create config with API keys from application config
        voice_config = VoiceChatConfig(
            openai_api_key=self.config.get("openai_api_key") or self.config.get("whisper_api_key"),
            stt_engine=self.config.get("stt_engine", "whisper")
        )
        
        # Try to load from config file first, then use our config
        voice_chat = VoiceChat(config=voice_config)
        return voice_chat.transcribe_audio(audio_file_path, language)

    def generate_response(self, prompt: str, language: str = "en", stream: bool = False) -> str:
        """Generate a response using selected LLM provider."""
        from src.ai.voice_chat import VoiceChat, VoiceChatConfig
        
        # Create config with API keys from application config
        voice_config = VoiceChatConfig(
            openai_api_key=self.config.get("openai_api_key") or self.config.get("gpt4_api_key"),
            anthropic_api_key=self.config.get("anthropic_api_key"),
            llm_provider=self.config.get("llm_provider", "openai"),
            enable_streaming=stream
        )
        
        # Try to load from config file first, then use our config
        voice_chat = VoiceChat(config=voice_config)
        return voice_chat.generate_response(prompt, language, stream=stream)

    def process_voice_message(self, audio_file_path: str, user_language: str = "en", 
                             enable_nft: bool = False, conversation_id: str = None) -> Dict[str, Any]:
        """Process a complete voice message with optional NFT creation."""
        # Try to use the voice plugin if available
        try:
            from src.plugins.voice_plugin import VoicePlugin
            voice_plugin = VoicePlugin()
            voice_plugin.on_load()
            
            # Update plugin config with app config values
            plugin_config = {
                "api_keys": {
                    "openai": self.config.get("openai_api_key") or self.config.get("whisper_api_key"),
                    "elevenlabs": self.config.get("elevenlabs_api_key", ""),
                    "anthropic": self.config.get("anthropic_api_key", "")
                },
                "enable_blockchain_integration": enable_nft,
                "nft_contract_address": self.config.get("nft_contract_address", ""),
                "polygon_private_key": self.config.get("polygon_private_key", ""),
                "polygon_network": self.config.get("polygon_network", "mumbai")
            }
            voice_plugin.update_config(plugin_config)
            
            # Process audio using the plugin
            result = voice_plugin.process_audio(
                audio_file_path=audio_file_path,
                user_language=user_language,
                enable_nft=enable_nft
            )
            
            # Clean up
            voice_plugin.on_unload()
            return result
            
        except (ImportError, Exception) as e:
            self.logger.warning(f"Could not use voice plugin, falling back to direct VoiceChat: {e}")
            
            # Fallback to direct VoiceChat usage
            from src.ai.voice_chat import VoiceChat, VoiceChatConfig
            
            # Create config with API keys from application config
            voice_config = VoiceChatConfig(
                openai_api_key=self.config.get("openai_api_key") or self.config.get("whisper_api_key"),
                elevenlabs_api_key=self.config.get("elevenlabs_api_key", ""),
                anthropic_api_key=self.config.get("anthropic_api_key", ""),
                enable_blockchain_integration=enable_nft,
                nft_contract_address=self.config.get("nft_contract_address", ""),
                polygon_private_key=self.config.get("polygon_private_key", ""),
                polygon_network=self.config.get("polygon_network", "mumbai")
            )
            
            voice_chat = VoiceChat(config=voice_config)
            return voice_chat.process_voice_message(
                audio_file_path=audio_file_path, 
                user_language=user_language,
                enable_nft=enable_nft,
                conversation_id=conversation_id
            )
            
    def analyze_voice_sentiment(self, audio_file_path: str, language: str = "en") -> Dict[str, float]:
        """Analyze sentiment of voice message."""
        from src.ai.voice_chat import VoiceChat, VoiceChatConfig
        
        # Create config with API keys from application config
        voice_config = VoiceChatConfig(
            openai_api_key=self.config.get("openai_api_key") or self.config.get("whisper_api_key"),
            elevenlabs_api_key=self.config.get("elevenlabs_api_key", ""),
            anthropic_api_key=self.config.get("anthropic_api_key", ""),
            enable_sentiment_analysis=True
        )
        
        voice_chat = VoiceChat(config=voice_config)
        # First transcribe the audio
        transcription = voice_chat.transcribe_audio(audio_file_path, language)
        # Then analyze sentiment
        return voice_chat.analyze_sentiment(transcription)

    def translate_text(self, text: str, source_language: str, target_language: str) -> str:
        """Translate text between languages."""
        from src.ai.multilingual import MultilingualSupport
        multilingual = MultilingualSupport()
        return multilingual.translate_text(text, source_language, target_language)

    # Infrastructure commands
    def deploy_to_cloud(self, application_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Deploy application to all cloud providers."""
        from src.infra.multi_cloud import MultiCloudDeployment
        multi_cloud = MultiCloudDeployment()
        return multi_cloud.deploy_to_all_clouds(application_config)

    def scale_deployment(self, deployment_name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        """Scale a Kubernetes deployment."""
        from src.infra.kubernetes import KubernetesOrchestrator
        k8s = KubernetesOrchestrator()
        return k8s.scale_deployment(deployment_name, replicas, namespace)

    def auto_scale(self) -> Dict[str, Any]:
        """Perform auto-scaling based on demand."""
        from src.infra.auto_scaling import AutoScaler
        auto_scaler = AutoScaler()
        return auto_scaler.auto_scale()

if __name__ == "__main__":
    app = TTBT5App()
    print("TTBT5 Application")
    print("Status:", "Running" if True else "Stopped")
    print("Please provide the TTBT2 requirements to implement the full application")
    print("Available commands: status, help, config, load_plugin, exec_hook")
