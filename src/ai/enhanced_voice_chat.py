import os
import json
import time
import queue
import threading
import sounddevice as sd
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path

class EnhancedVoiceChat:
    def __init__(self, config_path: str = "config/voice_config.json"):
        self.config = self._load_config(config_path)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None
        
    def _load_config(self, config_path: str) -> Dict[Any, Any]:
        """Load voice chat configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_config(config_path)
            
    def _create_default_config(self, config_path: str) -> Dict[Any, Any]:
        """Create default configuration if none exists"""
        default_config = {
            "sample_rate": 44100,
            "channels": 1,
            "chunk_size": 1024,
            "threshold": 0.01,
            "silence_limit": 2
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

    def start_recording(self):
        """Start audio recording"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.config["sample_rate"],
            channels=self.config["channels"],
            callback=self._audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _audio_callback(self, indata: np.ndarray, frames: int, 
                       time_info: Dict, status: sd.CallbackFlags):
        """Callback function for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def process_audio(self):
        """Process recorded audio from queue"""
        while self.is_recording:
            try:
                audio_chunk = self.audio_queue.get(timeout=1)
                # Implement audio processing logic here
                # For example: VAD, noise reduction, etc.
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")

    def run(self):
        """Main method to run voice chat"""
        try:
            self.start_recording()
            processing_thread = threading.Thread(target=self.process_audio)
            processing_thread.start()
            
            # Keep running until interrupted
            while True:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Stopping voice chat...")
        finally:
            self.stop_recording()
            
if __name__ == "__main__":
    voice_chat = EnhancedVoiceChat()
    voice_chat.run()
