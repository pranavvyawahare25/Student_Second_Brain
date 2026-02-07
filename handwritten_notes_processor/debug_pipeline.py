import cv2
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from handwritten_notes_processor.diagram_pipeline.diagram_detector import DiagramDetector
from handwritten_notes_processor.text_pipeline.ocr_engine import OCREngine
from handwritten_notes_processor.fusion.graph_builder import GraphBuilder

def main():
    image_path = "test.png"
    output_vis = "debug_crop_vis.png"
    
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.")
        return
    
    print(f"Processing {image_path}...")
    
    # 1. Diagram Detection
    print("--- Diagram Detection ---")
    diagram_detector = DiagramDetector()
    diagram_regions = diagram_detector.process_image(image_path, save_visualization=False)
    print(f"Found {len(diagram_regions)} diagram elements:")
    for i, r in enumerate(diagram_regions):
        print(f"  [{i}] Type: {r['type']}, BBox: {r['bbox']}, Shape: {r.get('shape')}")
    
    # 2. OCR
    print("\n--- OCR (Azure) ---")
    try:
        ocr_engine = OCREngine()
        text_regions = ocr_engine.process_image(image_path)
        print(f"Found {len(text_regions)} text regions:")
        for i, r in enumerate(text_regions):
            print(f"  [{i}] Text: '{r['text']}', BBox: {r['bbox']}")
    except Exception as e:
        print(f"OCR Failed: {e}")
        text_regions = []

    # 3. Fusion
    print("\n--- Graph Builder ---")
    graph_builder = GraphBuilder()
    graph = graph_builder.build_graph(diagram_regions, text_regions)
    print("Nodes:", graph.nodes(data=True))
    print("Edges:", graph.edges(data=True))
    
    # Visualize
    visualize_debug(image_path, diagram_regions, text_regions, output_vis)

def visualize_debug(image_path, diagram_regions, text_regions, output_path):
    image = cv2.imread(image_path)
    
    # Draw Diagrams (Green)
    for i, region in enumerate(diagram_regions):
        x1, y1, x2, y2 = region["bbox"]
        color = (0, 255, 0)
        if "connector" in region["type"]:
            color = (0, 255, 255)
        elif "container" in region["type"]:
            color = (255, 0, 0) # Blue for containers
            
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label = f"{i}:{region['type']}"
        cv2.putText(image, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    # Draw Text (Red)
    for i, region in enumerate(text_regions):
        x1, y1, x2, y2 = region["bbox"]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.putText(image, "TXT", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    cv2.imwrite(output_path, image)
    print(f"\nVisualization saved to {output_path}")

if __name__ == "__main__":
    main()
