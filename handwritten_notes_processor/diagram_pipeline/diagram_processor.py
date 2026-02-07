import math
import uuid

class DiagramProcessor:
    def __init__(self):
        pass

    def process(self, region, source_id="unknown_source"):
        """
        Process a DIAGRAM region to identify nodes and edges.
        
        Args:
            region (dict): Consolidated DIAGRAM region with 'elements'.
            source_id (str): Source identifier.
            
        Returns:
            dict: Graph representation {"type": "graph", "graph": {...}, "source": ...}
        """
        elements = region.get("elements", [])
        
        # 1. Identify Nodes (Containers & Text)
        nodes = self._identify_nodes(elements)
        
        # 2. Identify Edges (Connectors)
        edges = self._identify_edges(elements, nodes)
        
        # 3. Build Graph Structure
        graph_data = {
            "nodes": nodes,
            "edges": edges
        }
        
        return {
            "type": "graph",
            "graph": graph_data,
            "source": source_id,
            "bbox": region.get("bbox", [])
        }

    def _identify_nodes(self, elements):
        nodes = []
        
        # Separate containers and text
        containers = [e for e in elements if "container" in e.get("type", "")]
        text_elements = [e for e in elements if "text" in e.get("type", "") or e.get("type") == "text_content"]
        
        # 1. Create nodes from Containers
        for container in containers:
            # Check if container already has a 'text_content' from consolidation? 
            # If not, we might need to find text inside it again, but consolidation likely handled it.
            # Consolidator might have put text *inside* the container dict as 'elements' or handled it via logic.
            # Let's check the structure from previous steps. 
            # In consolidation: group["elements"].append(text) So text is a sibling in elements list.
            
            # Find text strictly inside this container
            label = ""
            contained_text = []
            
            c_bbox = container["bbox"]
            for t in text_elements:
                t_center = self._get_center(t["bbox"])
                if c_bbox[0] < t_center[0] < c_bbox[2] and c_bbox[1] < t_center[1] < c_bbox[3]:
                    contained_text.append(t)
            
            # Sort text by Y then X
            contained_text.sort(key=lambda x: (x["bbox"][1], x["bbox"][0]))
            label = " ".join([t.get("text", "") for t in contained_text])
            
            node = {
                "id": container.get("id", str(uuid.uuid4())[:8]),
                "label": label,
                "type": "container",
                "bbox": container["bbox"]
            }
            nodes.append(node)
            
        # 2. Create nodes from Standalone Text (blobs not in containers)
        # Mark text used in containers to avoid duplicates
        used_text_ids = set()
        for n in nodes:
            # Re-find text used for this node to mark as used? 
            # Simpler: just loop text again and check overlap with created nodes
            pass 
            
        # Actually, let's filter out text that fell into containers
        for t in text_elements:
            is_contained = False
            t_center = self._get_center(t["bbox"])
            for n in nodes:
                n_bbox = n["bbox"]
                if n_bbox[0] < t_center[0] < n_bbox[2] and n_bbox[1] < t_center[1] < n_bbox[3]:
                    is_contained = True
                    break
            
            if not is_contained:
                # Standalone text node
                nodes.append({
                    "id": f"text_{str(uuid.uuid4())[:8]}",
                    "label": t.get("text", ""),
                    "type": "text_blob",
                    "bbox": t["bbox"]
                })
                
        return nodes

    def _identify_edges(self, elements, nodes):
        edges = []
        connectors = [e for e in elements if "connector" in e.get("type", "")]
        
        if len(nodes) < 2:
            return []

        for connector in connectors:
            c_bbox = connector["bbox"]
            c_center = self._get_center(c_bbox)
            
            # Heuristic: Connect the two closest nodes to the connector center
            # Better heuristic: Check endpoint proximity if we had it. 
            # Since we only have bbox, we stick to center distance or bbox expansion intersection.
            
            distances = []
            for node in nodes:
                n_center = self._get_center(node["bbox"])
                dist = math.hypot(c_center[0] - n_center[0], c_center[1] - n_center[1])
                distances.append((dist, node))
            
            distances.sort(key=lambda x: x[0])
            
            if len(distances) >= 2:
                # Top 2 closest nodes
                node_a = distances[0][1]
                node_b = distances[1][1]
                
                # Determine direction?
                # If we have arrow information in shape classification, use it.
                # Currently 'shape' might be 'arrow', 'line', etc.
                # Without precise arrow head location, direction is hard.
                # We'll default to "connected" or try left->right / top->bottom assumption
                
                # Simple logic: Top-to-Bottom or Left-to-Right
                a_center = self._get_center(node_a["bbox"])
                b_center = self._get_center(node_b["bbox"])
                
                relation = "connected_to"
                
                # Assign Source/Target based on reading order (usually source is top/left)
                # This is a weak assumption for cycles but okay for trees
                if a_center[1] < b_center[1]: # A is above B
                    source, target = node_a, node_b
                elif a_center[0] < b_center[0]: # A is left of B
                    source, target = node_a, node_b
                else:
                    source, target = node_b, node_a # Swap
                
                edges.append({
                    "from": source["id"],
                    "to": target["id"],
                    "relation": relation,
                    "connector_id": connector.get("id", "unknown")
                })
                
        return edges

    def _get_center(self, bbox):
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
