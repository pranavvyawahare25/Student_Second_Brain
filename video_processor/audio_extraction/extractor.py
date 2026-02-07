import subprocess
import json
import os
import sys

class AudioExtractor:
    def __init__(self, output_dir="output_audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_audio(self, video_path):
        """
        Extracts ASR-ready audio from video using FFmpeg.
        Specs: MP3, 16kHz, Mono, High Quality.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_audio = os.path.join(self.output_dir, f"{base_name}.mp3")
        manifest_path = os.path.join(self.output_dir, f"{base_name}_manifest.json")

        print(f"Extracting audio from {video_path} to {output_audio}...")

        # FFmpeg command
        # -y: Overwrite output files
        # -map 0:a:0: Select first audio stream
        # -ac 1: Mono
        # -ar 16000: 16kHz
        # -vn: No video
        # -acodec libmp3lame: MP3 codec
        # -q:a 0: Best variable bitrate quality (to minimize loss for ASR)
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-map", "0:a:0",
            "-ac", "1",
            "-ar", "16000",
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "0",
            output_audio
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Audio extracted successfully: {output_audio}")
            
            # Create partial manifest (duration validation happens next)
            manifest = {
                "video_id": base_name,
                "audio_file": os.path.basename(output_audio),
                "source_video": os.path.basename(video_path),
                "sample_rate": 16000,
                "channels": 1,
                "format": "mp3"
            }
            
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
                
            return output_audio, manifest_path

        except subprocess.CalledProcessError as e:
            print(f"FFmpeg Error: {e.stderr.decode()}")
            raise e
