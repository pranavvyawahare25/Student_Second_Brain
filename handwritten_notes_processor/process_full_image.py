import cv2
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from handwritten_notes_processor.diagram_pipeline.diagram_detector import DiagramDetector
from handwritten_notes_processor.text_pipeline.ocr_engine import OCREngine
from handwritten_notes_processor.fusion.graph_builder import GraphBuilder
from handwritten_notes_processor.fusion.region_consolidator import RegionConsolidator
from handwritten_notes_processor.text_pipeline.text_processor import TextProcessor
from handwritten_notes_processor.diagram_pipeline.diagram_processor import DiagramProcessor
from handwritten_notes_processor.graph_pipeline.graph_refiner import GraphRefiner
from handwritten_notes_processor.knowledge_pipeline.schema_generator import SchemaGenerator

def visualize_final_graph(image_path, graphs, output_path):
    image = cv2.imread(image_path)
    
    # Draw Nodes and Edges from all graphs
    for graph_obj in graphs:
        g = graph_obj["graph"]
        nodes = {n["id"]: n for n in g["nodes"]}
        
        # Draw Nodes
        for node in g["nodes"]:
            if "bbox" not in node: continue # Skip if no bbox
            x1, y1, x2, y2 = node["bbox"]
            color = (0, 255, 0) if node["type"] == "container" else (0, 0, 255)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            # Label
            label = node.get("label", "")[:15]
            cv2.putText(image, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Draw Edges
        for edge in g["edges"]:
            src_id, tgt_id = edge["from"], edge["to"]
            if src_id in nodes and tgt_id in nodes:
                n1, n2 = nodes[src_id], nodes[tgt_id]
                if "bbox" not in n1 or "bbox" not in n2: continue
                
                cx1, cy1 = (n1["bbox"][0]+n1["bbox"][2])//2, (n1["bbox"][1]+n1["bbox"][3])//2
                cx2, cy2 = (n2["bbox"][0]+n2["bbox"][2])//2, (n2["bbox"][1]+n2["bbox"][3])//2
                cv2.arrowedLine(image, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2, tipLength=0.05)
                # Draw relation label
                rel = edge.get("relation", "")
                mid_x, mid_y = (cx1+cx2)//2, (cy1+cy2)//2
                cv2.putText(image, rel, (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                
    cv2.imwrite(output_path, image)
    print(f"Final Graph visualization saved to {output_path}")

def main():
    image_path = "/Users/iampranav/Student Second Brain/test2.png"
    output_vis = "output_full_pipeline.png"
    output_consolidated_vis = "output_consolidated.png" 
    output_dir = "output_artifacts" # New output directory for knowledge artifacts
    os.makedirs(output_dir, exist_ok=True)
    
    # ... (previous setup code) ...
    print(f"Processing {image_path}...")
    
    # 1. Diagram Detection
    print("Running Diagram Detection...")
    diagram_detector = DiagramDetector()
    diagram_regions = diagram_detector.process_image(image_path, save_visualization=False)
    
    # 2. OCR
    print("Running OCR...")
    ocr_engine = OCREngine(use_gpu=False) 
    text_regions = ocr_engine.process_image(image_path)
    
    # 4. Region Consolidation (Skip old graph builder)
    print("Consolidating Regions...")
    consolidator = RegionConsolidator()
    consolidated_output = consolidator.consolidate(diagram_regions, text_regions)
    
    # 5. Pipeline Steps 3A & 3B
    print("Running Text & Diagram Pipelines...")
    text_processor = TextProcessor()
    diagram_processor = DiagramProcessor()
    
    final_output = {
        "text_regions": [],
        "graphs": []
    }
    
    source_id = os.path.basename(image_path)
    
    for region in consolidated_output["regions"]:
        if region["type"] == "TEXT_PARAGRAPH":
            text_obj = text_processor.process(region, source_id=source_id)
            final_output["text_regions"].append(text_obj)
        elif region["type"] == "DIAGRAM":
            graph_obj = diagram_processor.process(region, source_id=source_id)
            final_output["graphs"].append(graph_obj)
            
    # Step 3C & 3D: Graph Consolidation & Canonicalization
    print("Refining Graphs (Step 3C/3D)...")
    graph_refiner = GraphRefiner()
    # Use page_level merge to create one canonical graph per page
    refined_graphs = graph_refiner.refine(final_output["graphs"], merge_mode="page_level")
    final_output["graphs"] = refined_graphs
            
    print("Final Output Structure:")
    # print(json.dumps(final_output, indent=2)) # Reduce noise
    
    # --- Step 4 & 5: Knowledge Generation ---
    if final_output["graphs"]:
        print("Generating Knowledge Artifacts...")
        canonical_graph = final_output["graphs"][0]["graph"]
        generator = SchemaGenerator()
        knowledge_output = generator.generate(canonical_graph, source_id)
        
        # Save JSON Artifacts
        with open(os.path.join(output_dir, "text_knowledge.json"), "w") as f:
            json.dump(knowledge_output["text_knowledge"], f, indent=2)
            
        with open(os.path.join(output_dir, "graph_knowledge.json"), "w") as f:
            json.dump(knowledge_output["graph_knowledge"], f, indent=2)
            
        print(f"Final Knowledge Artifacts saved to {output_dir}")
        
        # --- Step 6: Vector Storage ---
        from handwritten_notes_processor.knowledge_pipeline.vector_store import VectorStore
        print("Indexing Text Knowledge...")
        vector_store = VectorStore()
        vector_store.add_documents(knowledge_output["text_knowledge"])
        vector_store.save(output_dir)
    
    # Visualize Consolidated Regions
    visualize_consolidated(image_path, consolidated_output["regions"], output_consolidated_vis)
    
    # Visualize Final Graph (Merged)
    visualize_final_graph(image_path, final_output["graphs"], output_vis)

    # Generate Simplified Output (No BBox, Combined Text)
    simplified_output = []
    
    # 1. Combine all Text Regions into one
    if final_output["text_regions"]:
        combined_text = "\n".join([t["content"] for t in final_output["text_regions"]])
        simplified_output.append({
            "type": "text",
            "content": combined_text,
            "source": source_id
        })
        
    # 2. Add Graphs (Cleaned)
    for g in final_output["graphs"]:
        # Deep copy to avoid modifying original if needed, but here fine
        clean_graph = g.copy()
        if "bbox" in clean_graph: del clean_graph["bbox"]
        
        # Clean nodes inside graph
        if "graph" in clean_graph:
            for node in clean_graph["graph"].get("nodes", []):
                if "bbox" in node: del node["bbox"]
                
        simplified_output.append(clean_graph)

    print("Simplified Output:")
    print(json.dumps(simplified_output, indent=2))
    
    with open("simplified_output.json", "w") as f:
        json.dump(simplified_output, f, indent=2)
    print(f"Simplified output saved to simplified_output.json")
    
def visualize_consolidated(image_path, regions, output_path):
    image = cv2.imread(image_path)
    for region in regions:
        x1, y1, x2, y2 = region["bbox"]
        color = (255, 0, 0) # Blue for Paragraphs
        if region["type"] == "DIAGRAM":
            color = (0, 0, 255) # Red for Diagrams
            
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        cv2.putText(image, region["type"], (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
    cv2.imwrite(output_path, image)
    print(f"Consolidated visualization saved to {output_path}")

def visualize_full_result(image_path, diagram_regions, text_regions, graph, output_path):
    image = cv2.imread(image_path)
    
    # Draw Diagrams (Green)
    for region in diagram_regions:
        x1, y1, x2, y2 = region["bbox"]
        color = (0, 255, 0)
        if "connector" in region["type"]:
            color = (0, 255, 255)
            
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label = region["type"]
        if "shape" in region:
            label += f" ({region['shape']})"
        cv2.putText(image, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Draw Text (Red)
    for region in text_regions:
        x1, y1, x2, y2 = region["bbox"]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 1)
        # Put recognized text
        text = region["text"]
        cv2.putText(image, text, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Draw Graph Edges (Blue Arrows)
    print(f"Drawing {graph.number_of_edges()} edges...")
    for u, v, data in graph.edges(data=True):
        # Get centers of nodes u and v
        if u in graph.nodes and v in graph.nodes:
            node_u = graph.nodes[u]
            node_v = graph.nodes[v]
            
            ux1, uy1, ux2, uy2 = node_u["bbox"]
            vx1, vy1, vx2, vy2 = node_v["bbox"]
            
            u_center = (int((ux1 + ux2) / 2), int((uy1 + uy2) / 2))
            v_center = (int((vx1 + vx2) / 2), int((vy1 + vy2) / 2))
            
            cv2.arrowedLine(image, u_center, v_center, (255, 0, 0), 2, tipLength=0.05)

    cv2.imwrite(output_path, image)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    main()
