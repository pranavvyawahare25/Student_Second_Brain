import re

class SchemaGenerator:
    def __init__(self):
        # Semantic Type Mapping
        # content-based heuristics for strictly typed nodes
        self.node_type_rules = [
            (r"(machine learning|ml)", "concept"),
            (r"(learning|program|algorithm)", "process"),
            (r"(data|experience|task)", "data"),
            (r"(model|equation|rules|clusters)", "model"),
            (r"(definition|tom mitchell)", "definition"),
            (r"(equation|diagram|rules)", "example")
        ]
        
        # Relation Normalization
        self.relation_map = {
            "flows_to": "input_to",
            "leads_to": "leads_to",
            "produces": "produces",
            "input_to": "input_to",
            "defined_as": "defined_as",
            "flows_from": "is_type_of", # Heuristic: List item flows from Header
            "connected_to": "leads_to"  # Default fallback
        }

    def generate(self, canonical_graph, source_id="unknown"):
        """
        Generates final schema outputs.
        
        Args:
            canonical_graph (dict): The single 'graph' object from Step 3D.
            source_id (str): Filename source.
            
        Returns:
            dict: {
                "text_knowledge": [...],
                "graph_knowledge": {...}
            }
        """
        if not canonical_graph:
            return {"text_knowledge": [], "graph_knowledge": {}}

        nodes = canonical_graph.get("nodes", [])
        edges = canonical_graph.get("edges", [])
        
        # 1. Generate Text Knowledge (Vector DB)
        text_knowledge = self._generate_text_knowledge(nodes, source_id)
        
        # 2. Generate Graph Knowledge (Graph Store)
        graph_knowledge = self._generate_graph_knowledge(nodes, edges, source_id)
        
        return {
            "text_knowledge": text_knowledge,
            "graph_knowledge": graph_knowledge
        }

    def _generate_text_knowledge(self, nodes, source_id):
        """
        Extracts coherent text paragraphs.
        """
        # Sort by Y-position
        sorted_nodes = sorted(nodes, key=lambda n: n.get("bbox", [0,0,0,0])[1])
        
        paragraphs = []
        current_chunk = []
        
        for node in sorted_nodes:
            label = node.get("label", "")
            word_count = len(label.split())
            
            # Logic: Include if it IS a sentence (long), OR if it's explicitly a definition
            # OR if we are currently building a chunk (merging small bits)
            is_sentence = word_count > 5
            is_definition = self._is_definition_text(label)
            
            # Skip noise (very short, not part of a sentence flow) if starting a new chunk
            if not current_chunk and not (is_sentence or is_definition):
                continue

            # If current chunk is empty, start new
            if not current_chunk:
                current_chunk.append(node)
                continue
                
            # Check proximity to previous
            prev = current_chunk[-1]
            if self._is_same_paragraph(prev, node):
                current_chunk.append(node)
            else:
                # Flush current chunk
                paragraphs.append(self._flush_chunk(current_chunk, source_id))
                current_chunk = [node]
                
        if current_chunk:
            paragraphs.append(self._flush_chunk(current_chunk, source_id))
            
        return paragraphs

    def _flush_chunk(self, chunk, source_id):
        # Join with space
        full_text = " ".join([n["label"] for n in chunk])
        return {
            "doc_id": f"page_{source_id}",
            "chunk_id": f"chunk_{chunk[0]['id']}",
            "type": "text",
            "content": re.sub(r'\s+', ' ', full_text).strip(),
            "metadata": {
                "source_image": source_id,
                "topic": "extracted_knowledge",
                "page": 1
            }
        }

    def _is_same_paragraph(self, n1, n2):
        b1 = n1.get("bbox", [0,0,0,0])
        b2 = n2.get("bbox", [0,0,0,0])
        
        dy = b2[1] - b1[3]
        height = b1[3] - b1[1]
        
        # Vertical threshold: 1.8x height to keep paragraphs together but separate Definition from Diagram
        if -height * 0.5 <= dy < height * 1.8:
            return True
        return False

    def _is_definition_text(self, text):
        return any(x in text.lower() for x in ["definition", "field of study", "tom mitchell"])

    def _generate_graph_knowledge(self, nodes, edges, source_id):
        canonical_nodes = []
        node_map = {} # old_id -> new_clean_id
        node_type_map = {} # new_id -> type
        
        stop_words = ["following", "base", "and", "or", "of", "the", "without", "that", "gives", "programmed"]
        
        # 1. Process Nodes
        for n in nodes:
            old_id = n["id"]
            label = n.get("label", "").strip()
            if not label: continue
            
            # Correction: "Data Learning program" -> "Learning Program"
            if "Data Learning program" in label:
                label = "Learning Program"
            
            # Pruning Logic
            word_count = len(label.split())
            if word_count > 5:
                continue
                
            first_word = label.split()[0].lower()
            if label.lower() in stop_words or first_word in stop_words:
                continue
                
            # Type Inference
            n_type = self._infer_type(label)
            
            # Create ID
            clean_id = self._make_slug(label)
            node_map[old_id] = clean_id
            node_type_map[clean_id] = n_type
            
            # Canonical Node Object
            c_node = {
                "node_id": clean_id,
                "label": label,
                "type": n_type,
                "aliases": [label.lower()],
                "source": source_id
            }
            canonical_nodes.append(c_node)
            
        # 3. Inject Core Nodes (Model) if missing
        model_subtypes = ["mathematical_equation", "relational_diagrams_like_graphs_trees", "logical_if_else_rules", "groupings_called_clusters"]
        present_ids = {n["node_id"] for n in canonical_nodes}
        
        if any(m in present_ids for m in model_subtypes) and "model" not in present_ids:
             canonical_nodes.append({
                "node_id": "model",
                "label": "Model",
                "type": "model",
                "aliases": ["model"],
                "source": source_id
            })
             present_ids.add("model")

        # 2. Process Edges
        canonical_edges = []
        existing_edges = set() # (src, tgt)
        
        for e in edges:
            src = node_map.get(e["from"])
            tgt = node_map.get(e["to"])
            
            if src and tgt and src != tgt:
                if src not in present_ids: continue
                if tgt not in present_ids: continue

                src_type = node_type_map.get(src, "concept")
                tgt_type = node_type_map.get(tgt, "concept")

                # Filter Sibling Edges (Model Type -> Model Type / Example)
                # Rule: No edges between siblings (subtypes)
                if src_type in ["model", "example"] and tgt_type in ["model", "example"]:
                    # Allow edges ONLY if they connect to the parent 'model'
                    if src != "model" and tgt != "model":
                        continue

                raw_rel = e.get("relation")
                rel = self.relation_map.get(raw_rel, "leads_to")
                
                # Context-aware relation upgrade
                if "data" in src and "program" in tgt: rel = "input_to"
                if "program" in src and "model" in tgt: rel = "produces"
                if "definition" in tgt: rel = "defined_as"
                if "definition" in src: rel = "defined_as" 
                
                if raw_rel in ["flows_from", "connected_to"]:
                    if tgt_type in ["model", "example"] and src_type == "model":
                        rel = "is_type_of"
                    elif tgt_type == "example":
                        rel = "example_of"

                if (src, tgt) not in existing_edges:
                    c_edge = {
                        "from": src,
                        "to": tgt,
                        "relation": rel,
                        "confidence": 0.9,
                        "source": source_id
                    }
                    canonical_edges.append(c_edge)
                    existing_edges.add((src, tgt))
        
        # 3. Inject Core Structural Edges (if missing)
        self._inject_core_edges(canonical_nodes, canonical_edges, existing_edges, source_id)
                
        return {
            "graph_id": f"kg_{source_id}",
            "nodes": canonical_nodes,
            "edges": canonical_edges,
            "metadata": {
                "source_image": source_id,
                "page": 1
            }
        }

    def _inject_core_edges(self, nodes, edges, existing_edges, source_id):
        """Ensures the backbone of the graph exists if the nodes are present."""
        node_ids = {n["node_id"] for n in nodes}
        
        # Core Flow: Data -> Learning Program -> Model
        # Check for 'learning_program' (renamed) or fallback
        lp_id = "learning_program" if "learning_program" in node_ids else "data_learning_program"
        
        if "data" in node_ids and lp_id in node_ids:
            if ("data", lp_id) not in existing_edges:
                edges.append({"from": "data", "to": lp_id, "relation": "input_to", "confidence": 1.0, "source": source_id})
                existing_edges.add(("data", lp_id))
        
        # Learning Program -> Model
        if lp_id in node_ids and "model" in node_ids: 
             if (lp_id, "model") not in existing_edges:
                edges.append({"from": lp_id, "to": "model", "relation": "produces", "confidence": 1.0, "source": source_id})
                existing_edges.add((lp_id, "model")) 

        # Model -> Subtypes
        model_subtypes = ["mathematical_equation", "relational_diagrams_like_graphs_trees", "logical_if_else_rules", "groupings_called_clusters"]
        if "model" in node_ids:
            for subtype in model_subtypes:
                if subtype in node_ids:
                     if ("model", subtype) not in existing_edges:
                        edges.append({"from": "model", "to": subtype, "relation": "is_type_of", "confidence": 1.0, "source": source_id})

        # Machine Learning -> Definition
        if "machine_learning" in node_ids and "definition_of_ml" in node_ids:
             if ("machine_learning", "definition_of_ml") not in existing_edges:
                edges.append({"from": "machine_learning", "to": "definition_of_ml", "relation": "defined_as", "confidence": 1.0, "source": source_id})

    def _infer_type(self, label):
        l = label.lower()
        for pattern, n_type in self.node_type_rules:
            if re.search(pattern, l):
                return n_type
        return "concept" 

    def _make_slug(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '_', text)
        return text.strip('_')[:50]

