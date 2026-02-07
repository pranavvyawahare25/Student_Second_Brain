import re

class TextProcessor:
    def __init__(self):
        pass

    def process(self, region, source_id="unknown_source"):
        """
        Processes a TEXT_PARAGRAPH region to produce a structured text object.
        
        Args:
            region (dict): A region dictionary with 'type', 'bbox', and 'text'.
            source_id (str): Identifier for the source image/page.
            
        Returns:
            dict: Structured text object.
        """
        if region.get("type") != "TEXT_PARAGRAPH":
            # Fallback or strict check? For now, let's process whatever text field it has
            pass
            
        raw_text = region.get("text", "")
        normalized_text = self._normalize_text(raw_text)
        
        return {
            "type": "text",
            "content": normalized_text,
            "source": source_id,
            "bbox": region.get("bbox", [])
        }

    def _normalize_text(self, text):
        """
        Normalizes text by removing excessive whitespace and fixing common OCR issues.
        """
        if not text:
            return ""
            
        # 1. Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # 2. Strip leading/trailing whitespace
        text = text.strip()
        
        # 3. Add more normalization if specific OCR artifacts are known
        # e.g., fixing hyphenation at line breaks could be added here if we had line-level info
        
        return text
