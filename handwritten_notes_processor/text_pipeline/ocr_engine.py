import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

class OCREngine:
    def __init__(self, use_gpu=False):
        print("Initializing OCR Engine (Azure Form Recognizer)...")
        # Hardcoded for prototype, ideally move to env vars
        # Use Environment Variables for Security
        self.endpoint = os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT")
        self.key = os.environ.get("AZURE_FORM_RECOGNIZER_KEY")
        
        if not self.endpoint or not self.key:
            # Fallback for local testing if env vars not set (but don't commit this!)
            # In production/public repo, always use env vars.
            print("Warning: Azure credentials not found in environment variables.")
            self.endpoint = "https://eastus.api.cognitive.microsoft.com/" # Placeholder
            self.key = "" # Placeholderg1bKgr8MY96mmc18Q8bJQQJ99CBACYeBjFXJ3w3AAALACOGCqep"
        
        self.document_analysis_client = DocumentAnalysisClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )
        print("OCR Engine Initialized.")

    def process_image(self, image_path):
        """
        Full OCR pipeline using Azure Form Recognizer (prebuilt-layout).
        Returns list of regions with bbox and text.
        """
        print(f"Sending {image_path} to Azure Form Recognizer...")
        
        with open(image_path, "rb") as f:
            poller = self.document_analysis_client.begin_analyze_document(
                "prebuilt-layout", document=f
            )
        
        result = poller.result()
        
        output = []
        # Azure returns pages. We assume single image = 1 page usually.
        for page in result.pages:
            for line in page.lines:
                # line.content is text
                # line.polygon is list of points [x,y, x,y, ...] or objects
                # Azure SDK returns list of Point objects usually
                
                # Extract bbox from polygon
                # polygon is a list of 4 points (top-left, top-right, bottom-right, bottom-left)
                # Each point has x, y attributes
                
                x_coords = [p.x for p in line.polygon]
                y_coords = [p.y for p in line.polygon]
                
                x1, y1 = int(min(x_coords)), int(min(y_coords))
                x2, y2 = int(max(x_coords)), int(max(y_coords))
                
                output.append({
                    "bbox": [x1, y1, x2, y2],
                    "text": line.content,
                    "confidence": 1.0, # Azure doesn't always give line confidence in layout model, assume high
                    "type": "text_content"
                })
            
        print(f"Azure Form Recognizer found {len(output)} text lines.")
        return output

