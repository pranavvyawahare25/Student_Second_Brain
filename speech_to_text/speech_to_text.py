"""
Saaras Speech Translation Script
Converts audio from testaudio.mp3 to English text using Sarvam AI's Saaras model
"""

import os
import json
import requests
from sarvamai import SarvamAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def translate_audio(audio_file_path):
    """
    Translate audio file to English text using Saaras API
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Translation response from the API
    """
    # Get API key from environment variable
    api_key = os.getenv("SARVAM_API_KEY")
    
    if not api_key:
        raise ValueError("SARVAM_API_KEY not found in environment variables. Please check your .env file.")
    
    # Initialize Sarvam AI client
    client = SarvamAI(api_subscription_key=api_key)
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    print(f"Submitting async translation job for {audio_file_path}...")
    
    filename = os.path.basename(audio_file_path)
    print(f"Starting Bulk Job workflow for {filename}...")
    
    # 1. Initialise Job
    # 1. Initialise Job
    print("1. Initializing job...")
    init_resp = client.speech_to_text_translate_job.initialise(
        job_parameters={
            "model": "saaras:v2.5"
        }
    )
    # Correct attribute is job_id
    job_id = init_resp.job_id
    print(f"   Job ID: {job_id}")
    
    # 2. Get Upload Links
    print("2. Getting upload links...")
    upload_resp = client.speech_to_text_translate_job.get_upload_links(
        job_id=job_id,
        files=[filename]
    )
    
    print(f"   Upload config received. Uploading {filename}...")
    
    target_url = None
    if hasattr(upload_resp, 'upload_urls'):
        upload_details = upload_resp.upload_urls.get(filename)
        if upload_details:
            # Check if it has file_url attribute or is a dict
            if hasattr(upload_details, 'file_url'):
                target_url = upload_details.file_url
            elif isinstance(upload_details, dict):
                target_url = upload_details.get('file_url')
    
    if not target_url:
        print(f"DEBUG: upload_resp: {upload_resp}")
        raise Exception("Could not parse upload URL from response.")

    with open(audio_file_path, "rb") as f:
        # Use requests to put the file
        headers = {
            "x-ms-blob-type": "BlockBlob",
            "Content-Type": "audio/mpeg"
        }
        requests.put(target_url, data=f, headers=headers)
        print("   Upload complete.")

    # 4. Start Job
    print("3. Starting job...")
    client.speech_to_text_translate_job.start(job_id=job_id)
    
    # 5. Poll for Completion
    print("4. Polling for completion...")
    import time
    while True:
        job_handle = client.speech_to_text_translate_job.get_job(job_id)
        
        # Get actual status object
        status_resp = job_handle.get_status()
        print(f"DEBUG: status_resp attributes: {dir(status_resp)}")
        
        # Assume 'status' or 'job_state' is the field
        if hasattr(status_resp, 'status'):
            status = status_resp.status
        elif hasattr(status_resp, 'job_state'):
            status = status_resp.job_state
        else:
            status = "unknown"
        
        print(f"Current Status: {status}...", end="\r")
        
        # Check for success/failure
        # Status strings might be "Succeeded", "Failed", "Running" etc.
        # Normalize to lower for check
        status_lower = str(status).lower()
        
        if status_lower == "succeeded" or status_lower == "completed":
            print("\nJob completed successfully!")
            
            # Download results
            # The output file will be saved in the same directory as input or we can specify
            # Let's specify the directory of the input file
            output_dir = os.path.dirname(audio_file_path) or "."
            print(f"Downloading results to {output_dir}...")
            job_handle.download_outputs(output_dir=output_dir)
            
            # The file is typically named <filename>.json
            expected_output_file = os.path.join(output_dir, os.path.basename(audio_file_path) + ".json")
            
            if os.path.exists(expected_output_file):
                with open(expected_output_file, "r") as f:
                    data = json.load(f)
                return data
            else:
                 # Fallback: maybe it didn't download where we expected?
                 # Try to list files or return the manifest just in case
                 print(f"Warning: Expected output file {expected_output_file} not found.")
                 return job_handle.get_file_results()

        elif status_lower == "failed":
            raise Exception(f"Job failed: {status_resp}")
        else:
            time.sleep(2) 

    return None

import argparse

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio using Sarvam AI.")
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    args = parser.parse_args()
    
    try:
        # Translate the audio
        response = translate_audio(args.audio_file)
        
        print("\n" + "="*50)
        print("TRANSLATION RESULTS")
        print("="*50)
        
        transcript_text = "N/A"
        if isinstance(response, dict):
            # Check for transcript key
            if "transcript" in response:
                transcript_text = response["transcript"]
            elif "successful" in response:
                 # valid manifest but maybe we fell back
                 print("Received manifest but not transcript content.")
                 transcript_text = "Check detailed JSON output."
        
        print(f"Transcript (English snippet):\n{transcript_text[:500]}...")
        print("="*50)
        
        output_json = os.path.splitext(args.audio_file)[0] + "_transcript.json"
        with open(output_json, "w") as f:
            if isinstance(response, dict):
                json.dump(response, f, indent=2)
            else:
                f.write(response.json())
        print(f"Transcript saved to {output_json}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()