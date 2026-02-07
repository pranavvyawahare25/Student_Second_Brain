import networkx as nx
import math
import json

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, diagram_regions, text_regions):
        """
        Fuses diagram and text regions into a graph structure.
        """
        self.graph = nx.DiGraph()
        
        # 1. Add Nodes (Diagram Containers)
        containers = [r for r in diagram_regions if "container" in r["type"]]
        connectors = [r for r in diagram_regions if "connector" in r["type"]]
        
        # Helper to get center
        def get_center(bbox):
            return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)

        # Assign IDs to containers
        for i, container in enumerate(containers):
            container["id"] = f"box_{i}"
            container["text_content"] = ""
            self.graph.add_node(container["id"], type="box", bbox=container["bbox"], label="")

        # 2. Assign Text to Containers or Create Text Nodes
        used_text_indices = set()
        
        # First pass: Assign text strictly inside or overlapping containers
        for i, text in enumerate(text_regions):
            tx1, ty1, tx2, ty2 = text["bbox"]
            t_center = get_center(text["bbox"])
            
            best_container = None
            min_dist = float('inf')
            
            for container in containers:
                cx1, cy1, cx2, cy2 = container["bbox"]
                
                # Check strict inclusion of center
                if cx1 < t_center[0] < cx2 and cy1 < t_center[1] < cy2:
                    best_container = container
                    break # Found the container it's inside
                
                # Check overlap? For now, stick to center inclusion or very close proximity
            
            if best_container:
                best_container["text_content"] += text["text"] + " "
                used_text_indices.add(i)

        # Update container labels
        for container in containers:
             self.graph.nodes[container["id"]]["label"] = container["text_content"].strip()

        # Second pass: Create nodes for standalone text
        for i, text in enumerate(text_regions):
            if i not in used_text_indices:
                node_id = f"text_{i}"
                self.graph.add_node(node_id, type="text_block", bbox=text["bbox"], label=text["text"])

        # 3. Process Connectors (Edges)
        # Link any two nodes (box or text_block) that are closest to the connector endpoints
        all_nodes = []
        for node_id, data in self.graph.nodes(data=True):
            all_nodes.append({"id": node_id, "bbox": data["bbox"]})

        if len(all_nodes) < 2:
            return self.graph

        for connector in connectors:
            cx1, cy1, cx2, cy2 = connector["bbox"]
            # Connector endpoints (approximate as top-left and bottom-right for now, 
            # ideally we need line endpoints from the detector)
            # Since bbox doesn't give direction, we try to find the two closest nodes to the connector's center 
            # OR check which nodes intersect/touch the connector.
            
            # Simple interaction model: Find two closest unique nodes to the connector center
            c_center = get_center(connector["bbox"])
            
            distances = []
            for node in all_nodes:
                nx1, ny1, nx2, ny2 = node["bbox"]
                n_center = get_center(node["bbox"])
                
                # Euclidean distance between centers
                dist = math.hypot(c_center[0] - n_center[0], c_center[1] - n_center[1])
                distances.append((dist, node["id"]))
            
            distances.sort(key=lambda x: x[0])
            
            if len(distances) >= 2:
                u, v = distances[0][1], distances[1][1]
                # Avoid self-loops if possible, though sometimes valid. 
                # Ideally check if they are "opposite" sides of the connector.
                self.graph.add_edge(v, u, type="connection") # Direction ambiguous

        return self.graph

    def export_json(self):
        """
        Export graph to JSON format.
        """
        data = nx.node_link_data(self.graph)
        return json.dumps(data, indent=2)
