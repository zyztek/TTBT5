"""Voice Chat Module for TTBT5.
Handles voice recognition and synthesis using Whisper and GPT-4.
Includes real-time streaming capabilities and blockchain integration.
"""

import os
import time
import json
import tempfile
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass

@dataclass
class VoiceChatConfig:
    """Configuration for voice chat."""
    # API keys
    openai_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # For backward compatibility
    whisper_api_key: Optional[str] = None
    gpt4_api_key: Optional[str] = None
    
    # Engine selections
    tts_engine: str = "openai"  # Options: openai, elevenlabs, xtts, kokoro
    stt_engine: str = "whisper"  # Options: whisper, faster_whisper
    llm_provider: str = "openai"  # Options: openai, ollama, anthropic, xai
    
    # Feature flags
    enable_streaming: bool = True
    enable_interruption: bool = True
    enable_sentiment_analysis: bool = True
    enable_blockchain_integration: bool = False
    
    # Blockchain settings
    nft_contract_address: Optional[str] = None
    polygon_private_key: Optional[str] = None
    polygon_network: str = "mumbai"
    
    # Other settings
    supported_languages: List[str] = None
    conversation_history_limit: int = 100
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en", "es", "fr", "de", "it"]
        
        # For backward compatibility
        if self.whisper_api_key and not self.openai_api_key:
            self.openai_api_key = self.whisper_api_key
        if self.gpt4_api_key and not self.openai_api_key:
            self.openai_api_key = self.gpt4_api_key
    
    @classmethod
    def from_file(cls, config_path: str = None) -> 'VoiceChatConfig':
        """Load configuration from a JSON file."""
        if not config_path:
            # Try default locations
            possible_paths = [
                os.path.join(os.getcwd(), "config", "voice_chat_config.json"),
                os.path.join(os.getcwd(), "voice_chat_config.json"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if not config_path or not os.path.exists(config_path):
            print("No configuration file found, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Extract API keys
            api_keys = config_data.get("api_keys", {})
            voice_chat_config = config_data.get("voice_chat", {})
            blockchain_config = config_data.get("blockchain", {})
            
            # Create config with values from file
            return cls(
                openai_api_key=api_keys.get("openai"),
                elevenlabs_api_key=api_keys.get("elevenlabs"),
                anthropic_api_key=api_keys.get("anthropic"),
                tts_engine=voice_chat_config.get("tts_engine", "openai"),
                stt_engine=voice_chat_config.get("stt_engine", "whisper"),
                llm_provider=voice_chat_config.get("llm_provider", "openai"),
                enable_streaming=voice_chat_config.get("enable_streaming", True),
                enable_sentiment_analysis=voice_chat_config.get("enable_sentiment_analysis", True),
                enable_blockchain_integration=voice_chat_config.get("enable_blockchain_integration", False),
                supported_languages=voice_chat_config.get("supported_languages", ["en", "es", "fr", "de", "it"]),
                conversation_history_limit=voice_chat_config.get("conversation_history_limit", 100),
                nft_contract_address=blockchain_config.get("nft_contract_address"),
                polygon_private_key=blockchain_config.get("polygon_private_key"),
                polygon_network=blockchain_config.get("polygon_network", "mumbai")
            )
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return cls()

class VoiceChat:
    """Handles voice chat functionality with Whisper and GPT-4.
    Includes real-time streaming and blockchain integration.
    """
    
    def __init__(self, config: Optional[VoiceChatConfig] = None, config_path: Optional[str] = None):
        """
        Initialize the voice chat manager.
        
        Args:
            config: Configuration for voice chat
            config_path: Path to configuration file
        """
        # Load config from file if provided, otherwise use provided config or defaults
        if config_path:
            self.config = VoiceChatConfig.from_file(config_path)
        elif config:
            self.config = config
        else:
            # Try to load from default location
            self.config = VoiceChatConfig.from_file()
            
        self.conversation_history: List[Dict[str, Any]] = []
        self.streaming_callback: Optional[Callable[[str], None]] = None
        self.sentiment_scores: Dict[str, float] = {}
        self.nft_metadata: Dict[str, Any] = {}
        
    def register_streaming_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback for streaming responses."""
        self.streaming_callback = callback
        
    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> str:
        """Transcribe audio to text using Whisper or other STT engines.
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (default: 'en')
            
        Returns:
            Transcribed text
            
        Raises:
            FileNotFoundError: If the audio file does not exist
            ValueError: If the language is not supported
            Exception: For other transcription errors
        """
        try:
            # Validate inputs
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
                
            if language not in self.config.supported_languages:
                raise ValueError(f"Language '{language}' is not supported. Supported languages: {self.config.supported_languages}")
            
            print(f"Transcribing audio file: {audio_file_path} in language: {language}")
            
            # TODO: Implement actual transcription based on selected engine
            if self.config.stt_engine == "whisper":
                # OpenAI Whisper API implementation
                transcription = f"This is a sample transcription from Whisper in {language}."
            elif self.config.stt_engine == "faster_whisper":
                # Local Faster Whisper implementation
                transcription = f"This is a sample transcription from Faster Whisper in {language}."
            else:
                transcription = f"This is a sample transcription in {language}."
                
            return transcription
        except (FileNotFoundError, ValueError) as e:
            # Re-raise specific exceptions for handling by caller
            raise
        except Exception as e:
            # Log and re-raise general exceptions
            print(f"Error transcribing audio: {e}")
            raise Exception(f"Failed to transcribe audio: {e}")
    
    def generate_response(self, prompt: str, language: str = "en", stream: bool = False) -> Union[str, None]:
        """Generate a response using selected LLM provider.
        
        Args:
            prompt: The user's input prompt
            language: Language code (default: 'en')
            stream: Whether to stream the response (default: False)
            
        Returns:
            Generated response text or None if streaming
            
        Raises:
            ValueError: If the language is not supported or prompt is invalid
            Exception: For other generation errors
        """
        try:
            # Validate inputs
            if not prompt or not prompt.strip():
                raise ValueError("Prompt cannot be empty")
                
            if language not in self.config.supported_languages:
                raise ValueError(f"Language '{language}' is not supported. Supported languages: {self.config.supported_languages}")
            
            # Check if API key is available
            if self.config.llm_provider == "openai" and not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required but not provided")
            elif self.config.llm_provider == "anthropic" and not self.config.anthropic_api_key:
                raise ValueError("Anthropic API key is required but not provided")
            
            print(f"Generating response for prompt: {prompt} in language: {language}")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # TODO: Implement actual response generation based on selected provider
            if self.config.llm_provider == "openai":
                # OpenAI GPT-4 implementation
                if stream and self.streaming_callback:
                    # Simulate streaming response
                    response = "This is a sample response from GPT-4 with streaming capability."
                    for word in response.split():
                        self.streaming_callback(word + " ")
                        time.sleep(0.1)  # Simulate delay
                    
                    # Add to conversation history
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return None  # Response already delivered via callback
                else:
                    response = "This is a sample response from GPT-4."
            elif self.config.llm_provider == "ollama":
                response = "This is a sample response from Ollama."
            elif self.config.llm_provider == "anthropic":
                response = "This is a sample response from Anthropic Claude."
            elif self.config.llm_provider == "xai":
                response = "This is a sample response from xAI."
            else:
                response = "This is a sample response from the default LLM provider."
                
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
        except ValueError as e:
            # Re-raise specific exceptions for handling by caller
            raise
        except Exception as e:
            # Log and re-raise general exceptions
            print(f"Error generating response: {e}")
            raise Exception(f"Failed to generate response: {e}")
        
        return response
    
    def synthesize_speech(self, text: str, language: str = "en") -> str:
        """Synthesize speech from text using selected TTS engine.
        
        Args:
            text: The text to synthesize
            language: Language code (default: 'en')
            
        Returns:
            Path to the generated audio file
            
        Raises:
            ValueError: If the language is not supported or text is invalid
            Exception: For other synthesis errors
        """
        try:
            # Validate inputs
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
                
            if language not in self.config.supported_languages:
                raise ValueError(f"Language '{language}' is not supported. Supported languages: {self.config.supported_languages}")
            
            # Check if API key is available
            if self.config.tts_engine == "openai" and not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required but not provided")
            elif self.config.tts_engine == "elevenlabs" and not self.config.elevenlabs_api_key:
                raise ValueError("ElevenLabs API key is required but not provided")
            
            print(f"Synthesizing speech for text: {text} in language: {language}")
            
            # Create a temporary file for the audio
            temp_dir = tempfile.gettempdir()
            audio_file_path = os.path.join(temp_dir, f"response_{int(time.time())}.mp3")
            
            # TODO: Implement actual speech synthesis based on selected engine
            if self.config.tts_engine == "openai":
                # OpenAI TTS implementation
                print("Using OpenAI TTS")
            elif self.config.tts_engine == "elevenlabs":
                # ElevenLabs implementation
                print("Using ElevenLabs TTS")
            elif self.config.tts_engine == "xtts":
                # XTTS implementation
                print("Using XTTS (local)")
            elif self.config.tts_engine == "kokoro":
                # Kokoro implementation
                print("Using Kokoro TTS")
            else:
                print("Using default TTS engine")
                
            # Verify the file was created (in a real implementation)
            # This is a placeholder for actual file creation verification
            with open(audio_file_path, 'w') as f:
                f.write("Placeholder for audio data")
                
            return audio_file_path
        except ValueError as e:
            # Re-raise specific exceptions for handling by caller
            raise
        except Exception as e:
            # Log and re-raise general exceptions
            print(f"Error synthesizing speech: {e}")
            raise Exception(f"Failed to synthesize speech: {e}")
    
    def multilingual_support(self, text: str, source_language: str, target_language: str) -> str:
        """Translate text between languages.
        
        Args:
            text: The text to translate
            source_language: Source language code
            target_language: Target language code
            
        Returns:
            Translated text
            
        Raises:
            ValueError: If languages are not supported or text is invalid
            Exception: For other translation errors
        """
        try:
            # Validate inputs
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
                
            if source_language not in self.config.supported_languages:
                raise ValueError(f"Source language '{source_language}' is not supported. Supported languages: {self.config.supported_languages}")
                
            if target_language not in self.config.supported_languages:
                raise ValueError(f"Target language '{target_language}' is not supported. Supported languages: {self.config.supported_languages}")
                
            if source_language == target_language:
                return text  # No translation needed
            
            print(f"Translating text from {source_language} to {target_language}: {text}")
            
            # TODO: Implement actual translation
            # This would typically use a translation API
            translated_text = f"Translated text: {text}"  # Mock translation
            return translated_text
        except ValueError as e:
            # Re-raise specific exceptions for handling by caller
            raise
        except Exception as e:
            # Log and re-raise general exceptions
            print(f"Error translating text: {e}")
            raise Exception(f"Failed to translate text: {e}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with sentiment scores (positive, negative, neutral)
            
        Raises:
            ValueError: If text is invalid or sentiment analysis is disabled
            Exception: For other sentiment analysis errors
        """
        try:
            # Check if sentiment analysis is enabled
            if not self.config.enable_sentiment_analysis:
                raise ValueError("Sentiment analysis is disabled in configuration")
                
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
                
            print(f"Analyzing sentiment for text: {text}")
            
            # TODO: Implement actual sentiment analysis
            # This would typically use a sentiment analysis API or library
            sentiment = {"positive": 0.7, "negative": 0.1, "neutral": 0.2}
            self.sentiment_scores = sentiment
            return sentiment
        except ValueError as e:
            # Re-raise specific exceptions for handling by caller
            raise
        except Exception as e:
            # Log and re-raise general exceptions
            print(f"Error analyzing sentiment: {e}")
            raise Exception(f"Failed to analyze sentiment: {e}")
    
    def create_voice_nft_metadata(self, conversation_id: str) -> Dict[str, Any]:
        """Create metadata for voice NFT.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary containing NFT metadata
            
        Raises:
            ValueError: If conversation_id is invalid or blockchain integration is disabled
            Exception: For other metadata creation errors
        """
        try:
            # Validate inputs
            if not conversation_id or not conversation_id.strip():
                raise ValueError("Conversation ID cannot be empty")
                
            # Check if blockchain integration is enabled
            if not self.config.enable_blockchain_integration:
                raise ValueError("Blockchain integration is disabled in configuration")
                
            print(f"Creating NFT metadata for conversation: {conversation_id}")
            
            # Create metadata for NFT
            metadata = {
                "name": f"TTBT5 Voice Conversation #{conversation_id}",
                "description": "A voice conversation with TTBT5 AI",
                "conversation_id": conversation_id,
                "timestamp": time.time(),
                "language": self.config.supported_languages[0] if self.config.supported_languages else "en",
                "sentiment_scores": getattr(self, 'sentiment_scores', None),
                "conversation_summary": "Sample conversation summary",
                "audio_hash": f"hash_{int(time.time())}"
            }
            
            self.nft_metadata = metadata
            return metadata
        except ValueError as e:
            # Re-raise specific exceptions for handling by caller
            raise
        except Exception as e:
            # Log and re-raise general exceptions
            print(f"Error creating NFT metadata: {e}")
            raise Exception(f"Failed to create NFT metadata: {e}")
    
    def process_voice_message(self, audio_file_path: str, user_language: str = "en", 
                             enable_nft: bool = False, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a complete voice message: transcribe, respond, synthesize."""
        print(f"Processing voice message from: {audio_file_path}")
        
        # Generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = f"conv_{int(time.time())}"
        
        # Step 1: Transcribe audio to text
        transcription = self.transcribe_audio(audio_file_path, user_language)
        print(f"Transcription: {transcription}")
        
        # Step 2: Analyze sentiment if enabled
        if self.config.enable_sentiment_analysis:
            sentiment = self.analyze_sentiment(transcription)
            print(f"Sentiment: {sentiment}")
        
        # Step 3: Generate response using selected LLM
        response_text = self.generate_response(
            transcription, 
            user_language, 
            stream=self.config.enable_streaming
        )
        if response_text:  # If not streamed
            print(f"Response: {response_text}")
        
        # Step 4: Translate response if needed
        if user_language != "en" and response_text:
            response_text = self.multilingual_support(response_text, "en", user_language)
            print(f"Translated response: {response_text}")
        
        # Step 5: Synthesize speech from response
        response_audio_path = self.synthesize_speech(response_text or "Streamed response", user_language)
        print(f"Response audio saved to: {response_audio_path}")
        
        # Step 6: Create NFT metadata if enabled
        nft_metadata = None
        if enable_nft and self.config.enable_blockchain_integration:
            nft_metadata = self.create_voice_nft_metadata(conversation_id)
            print(f"NFT metadata created: {nft_metadata}")
        
        return {
            "conversation_id": conversation_id,
            "transcription": transcription,
            "response_text": response_text or "Streamed response",
            "response_audio": response_audio_path,
            "sentiment": self.sentiment_scores if self.config.enable_sentiment_analysis else None,
            "nft_metadata": nft_metadata,
            "status": "success"
        }

# Example usage (for testing)
if __name__ == "__main__":
    # Mock API keys (never hardcode real API keys)
    openai_api_key = "openai-api-key"
    elevenlabs_api_key = "elevenlabs-api-key"
    
    # Create voice chat manager with config
    config = VoiceChatConfig(
        openai_api_key=openai_api_key,
        elevenlabs_api_key=elevenlabs_api_key,
        enable_sentiment_analysis=True
    )
    voice_chat = VoiceChat(config=config)
    
    # Process a voice message (mock audio file)
    result = voice_chat.process_voice_message("/tmp/sample_audio.mp3", "en")
    print(f"Voice chat result: {result}")
