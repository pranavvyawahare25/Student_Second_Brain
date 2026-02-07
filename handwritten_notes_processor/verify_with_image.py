import sys
import os
import json

# Add the project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from handwritten_notes_processor.diagram_pipeline.diagram_detector import DiagramDetector

def verify():
    image_path = "/Users/iampranav/Student Second Brain/test.png"
    output_path = "output_visualization.png"
    
    print(f"Processing {image_path}...")
    
    detector = DiagramDetector()
    results = detector.process_image(image_path, save_visualization=True, output_path=output_path)
    
    diagram_elements = [r for r in results if "diagram" in r["region_type"] or "connector" in r["region_type"]]
    print(f"Found {len(diagram_elements)} diagram/connector elements.")
    print(json.dumps(diagram_elements, indent=2))

if __name__ == "__main__":
    verify()
