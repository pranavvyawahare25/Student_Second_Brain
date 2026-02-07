import cv2
import numpy as np

class DiagramDetector:
    def __init__(self):
        pass

    def process_image(self, image_path, save_visualization=True, output_path="output_visualization.png"):
        """
        Main pipeline to process an image and detect diagrams.
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Image not found at {image_path}")
            return []

        original_image = image.copy()
        regions = self.detect_regions(image)
        
        # Scene Classification
        diagram_count = sum(1 for r in regions if "diagram" in r["type"])
        connector_count = sum(1 for r in regions if "connector" in r["type"])
        
        scene_type = "text_notes"
        if diagram_count > 0:
             scene_type = "hybrid_notes"
        if diagram_count > 1 and connector_count > 0:
             scene_type = "flowchart"
             
        print(f"Scene Classification: {scene_type}")

        # Format output
        results = []
        for region in regions:
            results.append({
                "type": region["type"],
                "bbox": region["bbox"],
                "shape": region.get("shape", "unknown")
            })

        if save_visualization:
            self.visualize_results(original_image, regions, output_path)
        
        return results

    def detect_regions(self, image):
        """
        Core logic using OpenCV to detect regions.
        """
        # 1. Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Thresholding
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        
        # 3. Remove Horizontal Lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        remove_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        # Subtract lines - getting the mask of lines
        cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        # Make a Clean Binary image with lines removed
        binary_clean = binary.copy()
        for c in cnts:
            cv2.drawContours(binary_clean, [c], -1, (0,0,0), 5) # Draw lines in black (0) to remove them
        
        # 4. Find Contours on Clean Binary
        contours, hierarchy = cv2.findContours(binary_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if hierarchy is None:
            return []
            
        hierarchy = hierarchy[0]
        
        regions = []
        
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            
            # Hierarchy info
            child_idx = hierarchy[i][2]
            
            region_type = "unknown"
            shape_type = "unknown"
            
            # Heuristics
            
            # 1. Small Noise
            if area < 100:
                continue

            # 2. Container/Box Detection
            if (child_idx != -1 and area > 1000) or (area > 3000):
                # Refine Container
                image_area = image.shape[0] * image.shape[1]
                bbox_area = w * h
                if bbox_area > 0.5 * image_area:
                    continue # Ignore page-level wrappers
                
                ar = w / float(h)
                if h / float(w) > 10: 
                     continue # Vertical line
                elif ar > 8:
                     region_type = "text_line"
                else:
                    region_type = "diagram_container"
                    shape_type = self.classify_shape(cnt)
            
            # 3. Text Detection
            elif area < 3000:
                ar = w / float(h)
                if ar > 3: # Relaxed form 5
                     # Check if it looks like an arrow/line
                     shape_type = self.classify_shape(cnt)
                     if "line" in shape_type or "arrow" in shape_type:
                         region_type = "connector"
                     else:
                         region_type = "text_line"
                else:
                    region_type = "text"

            regions.append({
                "type": region_type,
                "bbox": [x, y, x+w, y+h],
                "area": area,
                "cnt": cnt,
                "shape": shape_type
            })
            
        return regions

    def classify_shape(self, cnt):
        """
        Classify the shape of a contour.
        """
        perimeter = cv2.arcLength(cnt, True)
        epsilon = 0.04 * perimeter
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        # If complex, try simpler approx
        if len(approx) > 6:
            approx = cv2.approxPolyDP(cnt, 0.06 * perimeter, True)
            
        vertices = len(approx)
        
        x, y, w, h = cv2.boundingRect(cnt)
        ar = w / float(h)
        area = cv2.contourArea(cnt)
        
        if vertices == 2:
            return "line"
        
        elif vertices == 3:
            return "triangle"
            
        elif vertices >= 4 and vertices <= 8:
            # Check if it fits a rectangle well
            if area > 100:
                extent = area / (w * h)
                if 0.6 <= extent <= 1.0: 
                    if 0.9 <= ar <= 1.1:
                        return "square"
                    else:
                        return "rectangle"
        
        # Check for Circle/Oval/Cylinder
        if vertices > 6:
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            circle_area = np.pi * (radius ** 2)
            if 0.7 <= area / circle_area <= 1.3:
                 return "circle"
        
        # Check for Arrow/Line based on solidity
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = area / float(hull_area)
            if solidity < 0.5:
                return "arrow_or_line"

        return "complex_polygon"


    def visualize_results(self, image, regions, output_name):
        """
        Draw bounding boxes and labels on the image.
        """
        for res in regions:
            x1, y1, x2, y2 = res["bbox"]
            color = (0, 255, 0) 
            if "diagram" in res["type"]:
                color = (0, 255, 0) # Green
            elif "connector" in res["type"]:
                color = (0, 255, 255) # Yellow
            elif "text" in res["type"]:
                color = (0, 0, 255) # Red
            else:
                color = (100, 100, 100) # Gray

            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            label = res["type"]
            if "shape" in res and res["shape"] != "unknown":
                label += f" ({res['shape']})"
                
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        cv2.imwrite(output_name, image)
        print(f"Visualization saved to {output_name}")
