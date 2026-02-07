from paddleocr import PaddleOCR
import cv2
import sys

def main():
    image_path = "test.png"
    print(f"Reading {image_path}...")
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to read image")
        return

    # Crop a small section
    crop = img[0:500, 0:500]
    crop_path = "test_crop.png"
    cv2.imwrite(crop_path, crop)
    print(f"Saved crop to {crop_path}")

    print(f"Initializing PaddleOCR...")
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
        print("Running OCR on crop...")
        result = ocr.ocr(crop_path)
        print("OCR Finished.")
        print(f"Result Type: {type(result)}")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
