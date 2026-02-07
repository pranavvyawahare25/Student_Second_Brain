import argparse
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from video_processor.audio_extraction.extractor import AudioExtractor
from video_processor.audio_extraction.validator import AudioValidator

def process_video(video_path, output_dir="output_audio"):
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return

    print(f"Processing video: {video_path}")
    
    try:
        # 1. Extraction
        extractor = AudioExtractor(output_dir)
        audio_path, manifest_path = extractor.extract_audio(video_path)
        
        # 2. Validation
        validator = AudioValidator()
        props = validator.validate(audio_path)
        
        # 3. Update Manifest with Duration
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
            
        manifest["duration"] = props["duration"]
        manifest["validated"] = True
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        print(f"✅ Processing Complete.")
        print(f"Manifest saved to {manifest_path}")
        
    except Exception as e:
        print(f"❌ Processing Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video to ASR-ready audio.")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--output_dir", default="output_audio", help="Directory to save output")
    
    args = parser.parse_args()
    process_video(args.video_path, args.output_dir)
