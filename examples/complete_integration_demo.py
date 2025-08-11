import os
import sys
import time
from pathlib import Path

# Add parent directory to path to import TTBT5
sys.path.append(str(Path(__file__).parent.parent))

from TTBT5 import TTBT5
from TTBT5.utils import load_audio, save_audio

def main():
    # Initialize TTBT5 model
    model = TTBT5()
    
    # Load source audio file
    source_path = "path/to/source.wav"
    source_audio = load_audio(source_path)
    
    # Process the audio
    print("Processing audio...")
    start_time = time.time()
    
    converted_audio = model.convert(
        source_audio,
        source_sr=44100,
        target_sr=44100
    )
    
    print(f"Processing completed in {time.time() - start_time:.2f} seconds")
    
    # Save the converted audio
    output_path = "path/to/output.wav"
    save_audio(output_path, converted_audio, sr=44100)
    print(f"Converted audio saved to: {output_path}")

if __name__ == "__main__":
    main()
