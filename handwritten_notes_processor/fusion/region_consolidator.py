import networkx as nx
import math

class RegionConsolidator:
    def __init__(self, x_threshold=50, y_threshold=20):
        self.x_threshold = x_threshold
        self.y_threshold = y_threshold

    def consolidate(self, diagram_regions, text_regions):
        """
        Consolidates raw regions into semantic regions (TEXT_PARAGRAPH, DIAGRAM).
        """
        consolidated_regions = []
        
        # 1. Consolidate Diagram Elements (Shapes, Connectors, Containers)
        # Filter out "text" types from diagram_regions as we use OCR for text
        # But keep them if they are purely structural (though DiagramDetector might be noisy)
        # Let's trust DiagramDetector's non-text elements
        structural_elements = [r for r in diagram_regions if "text" not in r["type"]]
        
        diagram_groups = self._consolidate_diagrams(structural_elements)
        
        # 2. Assign Text to Diagram Groups
        remaining_text = []
        for text in text_regions:
            assigned = False
            for group in diagram_groups:
                if self._regions_intersect_or_close(text, group, threshold=10):
                    # Add to group's elements and expand bbox
                    group["elements"].append(text)
                    self._expand_bbox(group, text["bbox"])
                    assigned = True
                    break
            if not assigned:
                remaining_text.append(text)
        
        consolidated_regions.extend(diagram_groups)
        
        # 3. Consolidate Remaining Text into Paragraphs
        paragraph_regions = self._consolidate_text(remaining_text)
        consolidated_regions.extend(paragraph_regions)
        
        return {"regions": consolidated_regions}

    def _expand_bbox(self, region, new_bbox):
        """Expand region bbox to include new_bbox."""
        b = region["bbox"]
        region["bbox"] = [
            min(b[0], new_bbox[0]),
            min(b[1], new_bbox[1]),
            max(b[2], new_bbox[2]),
            max(b[3], new_bbox[3])
        ]

    def _consolidate_text(self, text_regions):
        """
        Groups vertically aligned and close text lines into paragraphs.
        """
        if not text_regions:
            return []

        # Sort by Y coordinate
        sorted_regions = sorted(text_regions, key=lambda r: r['bbox'][1])
        
        paragraphs = []
        current_paragraph = [sorted_regions[0]]
        
        for i in range(1, len(sorted_regions)):
            prev = current_paragraph[-1]
            curr = sorted_regions[i]
            
            # Check vertical proximity
            prev_y2 = prev['bbox'][3]
            curr_y1 = curr['bbox'][1]
            
            # Check horizontal alignment/overlap
            prev_x1, prev_x2 = prev['bbox'][0], prev['bbox'][2]
            curr_x1, curr_x2 = curr['bbox'][0], curr['bbox'][2]
            
            # Simple overlap check
            x_overlap = max(0, min(prev_x2, curr_x2) - max(prev_x1, curr_x1))
            
            vertical_gap = curr_y1 - prev_y2
            
            # Merge if close vertically (line spacing) AND aligned
            is_close_y = vertical_gap < self.y_threshold
            is_aligned_x = x_overlap > 0 or (abs(curr_x1 - prev_x1) < self.x_threshold)

            if is_close_y and is_aligned_x:
                current_paragraph.append(curr)
            else:
                paragraphs.append(self._merge_text_group(current_paragraph))
                current_paragraph = [curr]
        
        if current_paragraph:
            paragraphs.append(self._merge_text_group(current_paragraph))
            
        return paragraphs

    def _merge_text_group(self, regions):
        """
        Merges a list of text regions into one TEXT_PARAGRAPH.
        """
        x1 = min(r['bbox'][0] for r in regions)
        y1 = min(r['bbox'][1] for r in regions)
        x2 = max(r['bbox'][2] for r in regions)
        y2 = max(r['bbox'][3] for r in regions)
        
        # Sort by Y then X to ensure reading order
        regions.sort(key=lambda r: (r['bbox'][1], r['bbox'][0]))
        
        full_text = " ".join(r['text'] for r in regions)
        
        return {
            "type": "TEXT_PARAGRAPH",
            "bbox": [x1, y1, x2, y2],
            "text": full_text
        }

    def _consolidate_diagrams(self, diagram_regions):
        """
        Groups diagram elements into connected components.
        """
        if not diagram_regions:
            return []
            
        G = nx.Graph()
        for i in range(len(diagram_regions)):
            G.add_node(i)
            
        # Build edges based on intersection or proximity
        for i in range(len(diagram_regions)):
            for j in range(i + 1, len(diagram_regions)):
                if self._regions_intersect_or_close(diagram_regions[i], diagram_regions[j], threshold=30):
                    G.add_edge(i, j)
                    
        # Find connected components
        components = list(nx.connected_components(G))
        
        consolidated = []
        for comp in components:
            indices = list(comp)
            group_regions = [diagram_regions[i] for i in indices]
            consolidated.append(self._merge_diagram_group(group_regions))
            
        return consolidated

    def _regions_intersect_or_close(self, r1, r2, threshold=0):
        """
        Checks if two bboxes intersect or are within threshold distance.
        """
        b1 = r1['bbox']
        b2 = r2['bbox']
        
        expanded_b1 = [b1[0]-threshold, b1[1]-threshold, b1[2]+threshold, b1[3]+threshold]
        
        x_overlap = max(0, min(expanded_b1[2], b2[2]) - max(expanded_b1[0], b2[0]))
        y_overlap = max(0, min(expanded_b1[3], b2[3]) - max(expanded_b1[1], b2[1]))
        
        return x_overlap > 0 and y_overlap > 0

    def _merge_diagram_group(self, regions):
        x1 = min(r['bbox'][0] for r in regions)
        y1 = min(r['bbox'][1] for r in regions)
        x2 = max(r['bbox'][2] for r in regions)
        y2 = max(r['bbox'][3] for r in regions)
        
        return {
            "type": "DIAGRAM",
            "bbox": [x1, y1, x2, y2],
            "elements": regions
        }
