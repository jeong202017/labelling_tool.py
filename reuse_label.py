import cv2
import json
import numpy as np
import os
from datetime import datetime

def roi_annotation(image_folder, output_folder):
    data = {"info": {"description": "my-project-name"}, "images": [], "annotations": [], "categories": []}

    category_map = {"godoo": 1, "tanjeo": 2, "yeolgwa": 3}
    for name, cat_id in category_map.items():
        data["categories"].append({"id": cat_id, "name": name})

    annotations = []
    image_id = 1
    annotation_id = 0
    
    def select_roi(image, prev_roi=None):
        cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
        if prev_roi is not None:
            x, y, w, h = prev_roi
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow("Select ROI", image)
            key = cv2.waitKey(0)
            if key == ord('f'):
                cv2.destroyWindow("Select ROI")
                return prev_roi
        roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select ROI")
        return roi 
    
    for root, _, files in os.walk(image_folder):
        for file_name in files:
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            image_path = os.path.join(root, file_name)
            parts = file_name.split('_')
            if len(parts) < 3:
                print(f"Invalid file naming convention for {file_name}. Skipping...")
                continue

            file_category = parts[1]
            file_category_id = category_map.get(file_category, None)
            if file_category_id is None:
                print(f"Category {file_category} not recognized for {file_name}. Skipping...")
                continue

            image = cv2.imread(image_path)
            if image is None:
                print(f"Image {file_name} not found. Skipping ...")
                continue

            height, width, _ = image.shape
            data["images"].append({"id": image_id, "width": width, "height": height, "file_name": file_name})
            
            prev_roi = None
            if os.path.exists(os.path.join(output_folder, f"prev_roi_{file_name}.json")):
                with open(os.path.join(output_folder, f"prev_roi_{file_name}.json"), 'r') as f:
                    prev_roi = json.load(f)["roi"]

            roi = select_roi(image, prev_roi)
            if roi == (0, 0, 0, 0):
                print(f"No ROI selected for {file_name}. Skipping ...")
                continue

            x, y, w, h = map(int, roi)
            roi_image = image[y:y+h, x:x+w]
            roi_rgb = cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB)
            lower_black = np.array([0, 0, 0], dtype=np.uint8)
            upper_black = np.array([75, 100, 125], dtype=np.uint8)
            mask_black = cv2.inRange(roi_rgb, lower_black, upper_black)
            contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 50:
                    continue
                contour = contour + np.array([x, y])
                bx, by, bw, bh = cv2.boundingRect(contour)
                bbox = [bx, by, bw, bh]
                segmentation = contour.flatten().tolist()

                annotation = {
                    "id": annotation_id,
                    "iscrowd": 0,
                    "image_id": image_id,
                    "category_id": file_category_id,
                    "segmentation": [segmentation],
                    "bbox": bbox,
                    "area": float(cv2.contourArea(contour))
                }
                annotations.append(annotation)
                annotation_id += 1
                cv2.rectangle(image, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
                cv2.polylines(image, [np.array(segmentation).reshape(-1, 2)], isClosed=True, color=(255, 0, 0), thickness=2)

            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, file_name)
            print(file_name + "현재 파일이름")
            cv2.imwrite(output_path, image)
            
            with open(os.path.join(output_folder, f"prev_roi_{file_name}.json"), 'w') as f:
                json.dump({"roi": [x, y, w, h]}, f, indent=4)
            
            print(f"Saved visualized annotation for {file_name} to {output_path}")
            print("Press 'q' to exit")
            if cv2.waitKey(0) & 0xFF == ord('q'):
                data["annotations"] = annotations
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                json_output_path = os.path.join(output_folder, f"annotations_{current_time}.json")
                with open(json_output_path, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Progress saved to {json_output_path}")
                return
            
            image_id += 1

    data["annotations"] = annotations
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_output_path = os.path.join(output_folder, f"annotations_{current_time}.json")
    with open(json_output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Final JSON file saved to {json_output_path}")

# 실행 예시
image_folder = "/home/scps/Desktop/jcw_ws/apple/train"
output_folder = "/home/scps/Desktop/jcw_ws/json_train"
roi_annotation(image_folder, output_folder)
