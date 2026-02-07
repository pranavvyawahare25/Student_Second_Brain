# Handwritten Notes Processor: Architecture & Walkthrough

This document provides a detailed "walkaround" of the `handwritten_notes_processor` module, explaining the purpose of each file and directory, and the reasoning behind the architectural decisions.

## 🎯 Core Philosophy
The system is designed as a **Multimodal Pipeline** that treats diagrams and text as separate but interacting entities.
- **Why?** Diagrams (shapes, arrows) require computer vision (OpenCV/YOLO). Text requires OCR (Azure Form Recognizer). Treating them separately allows us to use the best tool for each job, then "fuse" them later based on spatial proximity.

---

## 📂 Directory Structure

### 1. `handwritten_notes_processor/` (Root Package)
The main package containing all logic.

#### Key Files:
- **`process_full_image.py`**
  - **What**: The main entry point and orchestrator script.
  - **Why**: It ties everything together. It loads an image, calls the Text Pipeline, calls the Diagram Pipeline, fuses the results, refines the graph, and saves the final JSON/Image artifacts.
- **`verify_with_image.py`**
  - **What**: A lightweight script to test just the diagram detection on a local image.
  - **Why**: Faster feedback loop during development than running the full Azure OCR pipeline.
- **`requirements.txt`**
  - **What**: Python dependencies.
  - **Why**: Ensures reproducibility (azure-ai-formrecognizer, opencv-python, networkx, faiss-cpu).

---

### 2. `text_pipeline/` (OCR)
Handles extraction of raw text from images.

- **`ocr_engine.py`**
  - **What**: Wraps Azure Form Recognizer's `DocumentAnalysisClient`.
  - **Why**: Azure provides superior handwritten text recognition compared to open-source alternatives like Tesseract, especially for complex layouts. It returns bounding boxes (`bbox`) which are crucial for later fusion.
- **`text_processor.py`**
  - **What**: Cleans and normalizes the raw text strings (e.g., fixing spacing, capitalization).
  - **Why**: OCR often returns noisy text (e.g., "M achine Learning"). We need a dedicated step to clean this before it enters our knowledge graph.

### 3. `diagram_pipeline/` (Vision)
Handles detection of shapes and arrows.

- **`diagram_detector.py`**
  - **What**: Uses OpenCV (Computer Vision) to detect shapes (rectangles, circles) and lines/arrows.
  - **Why**: We need to know *where* the boxes and arrows are to understand the flow of the diagram.
  - **How it works**:
    - `cv2.Canny`: Detects edges.
    - `cv2.findContours`: Finds the outlines of shapes.
    - `approxPolyDP`: Simplifies contours to determine if they are rectangles, triangles, or circles.
- **`diagram_processor.py`**
  - **What**: Converts raw detections (e.g., "contour at [x,y]") into semantic objects (e.g., "Node A connected to Node B").
  - **Why**: Raw visual data isn't useful for a knowledge graph. We need to bridge the gap between "pixels" and "graph concepts".

### 4. `fusion/` (The "Brain" of Hybrid Processing)
Combines the output of Text and Diagram pipelines.

- **`graph_builder.py`**
  - **What**: The core logic that says "Text A is inside Box B, so Text A labels Box B".
  - **Why**: Diagrams have structure (arrows), Text has meaning. Fusion gives structure to meaning.
  - **Logic**:
    - **Spatial containment**: If text bbox is inside a shape bbox -> It's a Label.
    - **Proximity**: If text is near an arrow -> It's an edge label.
- **`region_consolidator.py`**
  - **What**: Groups fragmented elements into larger "Semantic Regions" (e.g., `TEXT_PARAGRAPH`, `DIAGRAM`).
  - **Why**: Handwritten notes are messy. A paragraph might be detected as 5 separate lines. This module merges them back into a single coherent block based on vertical proximity.

### 5. `graph_pipeline/` (Refinement)
Polishes the raw graph into a clean Knowledge Graph.

- **`graph_refiner.py`**
  - **What**: Cleans up the graph structure.
  - **Why**: The initial graph from Fusion might have duplicate nodes (e.g., "Data" appearing twice) or broken edges.
  - **Key Features**:
    - **Canonicalization**: Merges "Data" and "data" into a single node.
    - **Semantic Inference**: Infers edge types based on layout (e.g., if Node A is above Node B, the relation might be `leads_to`).

### 6. `knowledge_pipeline/` (Storage Schema)
Prepares data for final storage (Vector DB & Graph DB).

- **`schema_generator.py`**
  - **What**: Converts the internal Python graph objects into the specific JSON schemas required by our databases.
  - **Why**: Decouples our internal logic from the external database requirements. If the DB schema changes, we only update this file.
  - **Outputs**:
    - `text_knowledge` (for Vector Search/RAG).
    - `graph_knowledge` (for Property Graph/Cypher queries).

---

## 🔄 The Data Flow (Pipeline Execution)

1.  **Input**: Image of handwritten notes.
2.  **Parallel Processing**:
    - `text_pipeline` -> Extracts Text + BBoxes.
    - `diagram_pipeline` -> Extracts Shapes + Arrows.
3.  **`fusion/graph_builder.py`**:
    - Matches Text to Shapes.
    - Matches Shapes to other Shapes (via Arrows).
4.  **`fusion/region_consolidator.py`**:
    - Groups remaining text into Paragraphs.
5.  **`graph_pipeline/graph_refiner.py`**:
    - Merges duplicates, infers semantics.
6.  **`knowledge_pipeline`**:
    - Formats for Vector/Graph DBs.
7.  **Output**: `simplified_output.json`, `knowledge_graph.json`, `vector_store/`.
