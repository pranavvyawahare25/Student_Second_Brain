import re
import math
import networkx as nx

class GraphRefiner:
    def __init__(self):
        # Common OCR corrections map
        self.corrections = {
            "datal": "Data",
            "folowing": "following",
            "followinge": "following",
            "dandel": "and",
            "dand": "and"
        }
        
        # Semantic Rules (Target Word -> Relation)
        self.semantic_rules = {
            "model": "produces",
            "program": "input_to",
            "learning": "input_to"
        }

    def refine(self, graphs, merge_mode="page_level"):
        """
        Refines a list of graph objects.
        
        Args:
            graphs (list): List of graph dictionaries.
            merge_mode (str): 'page_level' (one graph per page) or 'proximity' (default).
            
        Returns:
            list: Consolidated and refined graph objects.
        """
        if not graphs:
            return []

        # 1. Merge Graphs
        if merge_mode == "page_level":
            # Merge ALL graphs into one canonical graph per page
            # For simplicity, assuming list is from one page source for now
            merged_graphs = [self._merge_graph_list(graphs)]
        else:
            merged_graphs = self._merge_graphs_spatially(graphs)
        
        # 2. Refine each merged graph
        refined_graphs = []
        for g_obj in merged_graphs:
            refined_g = self._refine_single_graph(g_obj)
            # Filter empty graphs
            if refined_g["graph"]["nodes"]:
                refined_graphs.append(refined_g)
            
        return refined_graphs

    def _merge_graphs_spatially(self, graphs):
        # ... (Same as before, simplified for brevity here if needed) ...
        # Can reuse previous logic but strictly better to keep it if user switches mode
        meta_indices = range(len(graphs))
        G = nx.Graph()
        G.add_nodes_from(meta_indices)
        
        for i in range(len(graphs)):
            for j in range(i + 1, len(graphs)):
                if self._are_graphs_close(graphs[i], graphs[j]):
                    G.add_edge(i, j)
                    
        components = list(nx.connected_components(G))
        new_graphs = []
        for comp in components:
            graphs_to_merge = [graphs[i] for i in list(comp)]
            new_graphs.append(self._merge_graph_list(graphs_to_merge))
        return new_graphs

    def _are_graphs_close(self, g1, g2, y_threshold=100, x_threshold=50):
        b1, b2 = g1.get("bbox", [0,0,0,0]), g2.get("bbox", [0,0,0,0])
        # Y overlap or close Y distance
        y_dist = max(0, b2[1] - b1[3]) if b2[1] > b1[1] else max(0, b1[1] - b2[3])
        if y_dist < y_threshold: return True
        return False

    def _merge_graph_list(self, graph_list):
        if not graph_list: return {}
        combined_nodes = []
        combined_edges = []
        min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
        source = graph_list[0].get("source", "unknown")
        
        for g in graph_list:
            inner_g = g.get("graph", {})
            combined_nodes.extend(inner_g.get("nodes", []))
            combined_edges.extend(inner_g.get("edges", []))
            bbox = g.get("bbox", [0,0,0,0])
            if bbox:
                min_x, min_y = min(min_x, bbox[0]), min(min_y, bbox[1])
                max_x, max_y = max(max_x, bbox[2]), max(max_y, bbox[3])
                
        return {
            "type": "graph",
            "graph": {"nodes": combined_nodes, "edges": combined_edges},
            "source": source,
            "bbox": [min_x, min_y, max_x, max_y]
        }

    def _refine_single_graph(self, g_obj):
        graph_data = g_obj.get("graph", {})
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        # 1. Normalize Labels
        for node in nodes:
            node["label"] = self._normalize_label(node.get("label", ""))
            
        # 2. Merge Adjacent Text Nodes (Canonicalization Step 1)
        nodes, text_merge_map = self._merge_adjacent_text_nodes(nodes)
        
        # 3. Deduplicate Nodes (Canonicalization Step 2)
        nodes, dedup_map = self._deduplicate_nodes(nodes)
        
        # Combine maps
        # Final ID -> Dedup ID -> Text Merge ID
        # Wait, text merge happens first. IDs of merged-away nodes should point to survivor.
        # Dedup happens on survivors.
        
        full_map = {}
        # First populate with identity for current nodes
        for n in nodes:
            full_map[n["id"]] = n["id"]
            
        # Add text merge mappings
        # If A->B in text_merge, and B->C in dedup. Then A->C.
        # If A->A in text_merge, and A->C in dedup. Then A->C.
        
        # Let's simplify: 
        # Source ID -> [Text Merge] -> Middle ID -> [Dedup] -> Final ID
        
        # 4. Update Edges
        new_edges = []
        for edge in edges:
            src_id, tgt_id = edge["from"], edge["to"]
            
            # 1. Apply Text Merge Map
            mid_src = text_merge_map.get(src_id, src_id)
            mid_tgt = text_merge_map.get(tgt_id, tgt_id)
            
            # 2. Apply Dedup Map
            final_src = dedup_map.get(mid_src, mid_src)
            final_tgt = dedup_map.get(mid_tgt, mid_tgt)
            
            # Only keep if valid and not self-loop (unless self-loops allowed? usually no for flow)
            # Check if final IDs exist in nodes
            src_exists = any(n["id"] == final_src for n in nodes)
            tgt_exists = any(n["id"] == final_tgt for n in nodes)
            
            if src_exists and tgt_exists and final_src != final_tgt:
                node_src = next(n for n in nodes if n["id"] == final_src)
                node_tgt = next(n for n in nodes if n["id"] == final_tgt)
                
                # Semantic Upgrade
                relation = self._infer_relation(node_src, node_tgt)
                new_edges.append({
                    "from": final_src,
                    "to": final_tgt,
                    "relation": relation
                })
        
        graph_data["nodes"] = nodes
        graph_data["edges"] = new_edges
        return g_obj

    def _merge_adjacent_text_nodes(self, nodes):
        """Merges text nodes that are substantially close horizontally (phrase merging)."""
        if not nodes: return [], {}
        
        # Sort by Y then X
        sorted_nodes = sorted(nodes, key=lambda n: (n.get("bbox", [0,0,0,0])[1], n.get("bbox", [0,0,0,0])[0]))
        
        merged_nodes = []
        skip_indices = set()
        merge_map = {} # old_id -> new_id
        
        for i in range(len(sorted_nodes)):
            if i in skip_indices: continue
            
            current = sorted_nodes[i]
            current_id = current["id"]
            merge_map[current_id] = current_id # Map to self initially
            
            # Try to merge with next node
            for j in range(i + 1, len(sorted_nodes)):
                if j in skip_indices: continue
                next_node = sorted_nodes[j]
                
                if self._should_merge_text(current, next_node):
                    # Merge content
                    next_text = next_node["label"]
                    if next_text:
                        current["label"] = (current["label"] + " " + next_text).strip()
                    
                    # Merge bbox
                    b1, b2 = current["bbox"], next_node["bbox"]
                    current["bbox"] = [
                        min(b1[0], b2[0]), min(b1[1], b2[1]),
                        max(b1[2], b2[2]), max(b1[3], b2[3])
                    ]
                    
                    # Update map
                    merge_map[next_node["id"]] = current_id
                    skip_indices.add(j)
                else:
                    # Break heuristic
                    pass
            
            merged_nodes.append(current)
            
        return merged_nodes, merge_map

    def _should_merge_text(self, n1, n2):
        if n1["type"] != "text_blob" or n2["type"] != "text_blob": return False
        b1, b2 = n1["bbox"], n2["bbox"]
        
        # Check Center-Y Alignment
        cy1 = (b1[1] + b1[3]) / 2
        cy2 = (b2[1] + b2[3]) / 2
        h1 = b1[3] - b1[1]
        h2 = b2[3] - b2[1]
        
        # Allow vertical shift up to full height of the taller node (handle stepped text)
        max_h = max(h1, h2)
        if abs(cy1 - cy2) > max_h * 1.0: return False
        
        # Check horizontal distance (close)
        dist_x = b2[0] - b1[2] # n2 is to the right of n1
        
        # Allow significant overlap for multi-line text (dist_x < 0)
        # But ensure n2 starts somewhat near n1 (not completely to the left, which sort protects against)
        # Limit overlap to width of n1 (don't merge if n2 is far left wrapping?)
        
        width1 = b1[2] - b1[0]
        # dist_x can be negative (overlap). 
        # Lower bound: -width1 * 0.9 (overlap almost entirely)
        # Upper bound: max_h * 1.5 (gap)
        return (-width1 * 0.9) <= dist_x < max_h * 1.5

    def _deduplicate_nodes(self, nodes):
        """Merges nodes with identical normalized labels."""
        unique_nodes = []
        label_map = {} # label -> node_id
        id_map = {} # old_id -> new_id
        
        for node in nodes:
            label = node["label"].lower()
            if not label: continue # Skip empty
            
            if label in label_map:
                # Duplicate found, map to existing
                existing_id = label_map[label]
                id_map[node["id"]] = existing_id
            else:
                # New unique node
                label_map[label] = node["id"]
                id_map[node["id"]] = node["id"]
                unique_nodes.append(node)
                
        return unique_nodes, id_map

    def _normalize_label(self, text):
        if not text: return ""
        text = re.sub(r'^[\d\.\-\•\s]+', '', text) # Leading bullets
        text = text.strip()
        text = re.sub(r'[\.\:\,]+$', '', text) # Trailing punctuation
        
        for pattern, replacement in self.corrections.items():
            regex = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE) # Match whole word
            text = regex.sub(replacement, text)
            
        return text

    def _infer_relation(self, src, tgt):
        # 1. Check heuristics based on Labels
        s_lbl = src.get("label", "").lower()
        t_lbl = tgt.get("label", "").lower()
        
        if "data" in s_lbl and "program" in t_lbl: return "input_to"
        if "learning" in s_lbl and "model" in t_lbl: return "produces"
        if "experience" in s_lbl and "model" in t_lbl: return "improves"
        if "model" in s_lbl and "machine learning" in t_lbl: return "defined_as"
        
        # 2. Fallback to Spatial
        return self._spatial_relation(src, tgt)

    def _spatial_relation(self, src, tgt):
        s_b, t_b = src.get("bbox", [0,0,0,0]), tgt.get("bbox", [0,0,0,0])
        s_c = ((s_b[0]+s_b[2])/2, (s_b[1]+s_b[3])/2)
        t_c = ((t_b[0]+t_b[2])/2, (t_b[1]+t_b[3])/2)
        dx, dy = t_c[0] - s_c[0], t_c[1] - s_c[1]
        
        if abs(dx) > abs(dy):
            return "flows_to" if dx > 0 else "flows_from"
        else:
            return "leads_to" if dy > 0 else "leads_to"

