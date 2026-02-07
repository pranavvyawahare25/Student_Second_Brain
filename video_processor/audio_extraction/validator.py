import subprocess
import json
import os

class AudioValidator:
    def validate(self, audio_path):
        """
        Validates that the audio file meets ASR requirements:
        - 16kHz
        - Mono
        - Duration matches (checked via metadata if available, but here we check properties)
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"Validating audio properties for {audio_path}...")
        
        # ffprobe command to get JSON metadata
        command = [
            "ffprobe", 
            "-v", "quiet", 
            "-print_format", "json", 
            "-show_streams", 
            "-show_format", 
            audio_path
        ]

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            metadata = json.loads(result.stdout)
            
            if not metadata["streams"]:
                raise ValueError("No streams found in audio file.")
                
            stream = metadata["streams"][0]
            
            # Checks
            sample_rate = int(stream.get("sample_rate", 0))
            channels = int(stream.get("channels", 0))
            codec = stream.get("codec_name", "")
            
            errors = []
            if sample_rate != 16000:
                errors.append(f"Sample rate is {sample_rate}, expected 16000")
            if channels != 1:
                errors.append(f"Channels is {channels}, expected 1")
            if "pcm_s16le" not in codec and "mp3" not in codec:
                 # Warn if neither PCM nor MP3, but strictly fail only if essential properties missed?
                 # Since we switched to MP3, we expect 'mp3' or 'mp3float'
                 if "mp3" not in codec:
                    print(f"Warning: Unexpected codec {codec}, expected mp3 or pcm_s16le")

            if errors:
                raise ValueError(f"Audio validation failed: {', '.join(errors)}")
            
            duration = float(metadata["format"].get("duration", 0))
            print(f"✅ Audio Valid: 16kHz, Mono, Duration: {duration}s")
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels
            }

        except subprocess.CalledProcessError as e:
            print(f"FFprobe Error: {e.stderr.decode()}")
            raise e
        except FileNotFoundError:
             raise FileNotFoundError("ffprobe not found. Please install ffmpeg.")
