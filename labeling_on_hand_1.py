import cv2
import json
import numpy as np
import os
from datetime import datetime

def roi_annotation (image_folder, output_folder):
    data = {"info":[], "images":[], "annotations":[],"categories": []}

    # Initialize list for new annotations #무슨 용도임??
    annotations = []
    image_id = 1
    annotation_id = 0
    category_id = 0

    # Function to select ROI
    def select_roi(image): #왜 함수안에 함수를 넣었을까?
        print("엔터나 스페이스바 입력")
        roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select ROI")
        return roi

    for root, _, files in os.walk(image_folder):
        for file_name in files:
            if not file_name.lower().endswith(('.png','.jpg','.jpeg')):
                continue

            image_path = os.path.join(root, file_name)

            #
            parts = file_name.split('_')
            if len(parts) < 3:
                print(f"Invalid file naming convention for {file_name}. Skipping...")
                continue

            category_map = {"godoo":1,"tanjeo":2,"tanger":2,"yeolgwa":3}
            file_category = parts[2]
            file_category_id = category_map.get(file_category,None)

            if file_category_id is None:
                print(f"Category {file_category} not recognied for {file_name}. Skipping...")
                continue
            
            #
            image = cv2.imread(image_path)
            if image is None:
                print(f"Image {file_name} not found. Skipping ...")
                continue

            # select ROI
            roi = select_roi(image)
            if roi == (0, 0, 0, 0):
                print(f"No ROI selected for {file_name}. Skipping ...")
                continue

            x, y, w, h = map(int, roi)
            roi_image = image[y:y+h, x:x+w]

            #
            height, width, _ = image.shape
            data["images"].append({"id": image_id, "width":width, "height":height, "file_name": file_name})

            #
            hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
            lower_black = np.array([0,0,0])
            upper_black = np.array([179, 255, 50])
            mask = cv2.inRange(hsv, lower_black, upper_black)

            #
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 50:
                    continue

                #
                contour = contour + [x, y]

                #
                bx, by, bw, bh = cv2.boundingRect(contour)
                bbox = [bx, by, bw, bh]
                segmentation = contour.flatten().tolist()

                #
                annotation = {
                    "id" : annotation_id,
                    "iscrowd" : 0, # 이거 뭐노?
                    "image_id" : image_id,
                    "category_id" : file_category_id,
                    "segmentation" : [segmentation],
                    "bbox" : bbox,
                    "area" : float(cv2.contourArea(contour))
                }
                annotations.append(annotation)
                annotation_id += 1

                #시각화
                # cv2.rectangle(image, (bx, by), (bx + bw, by+bh), (0, 255, 0), 2)
                # cv2.polylines(image, [np.array(segmentation).reshape(-1,2)], isClosed = True, color = (255, 0, 0), thickness = 2)

            category = {
                "id" : category_id, # 여기서 우짜노
                "name" : "godoo" # ㄹㅇㅋㅋ
            }
        
        # 시각화 이미지 저장
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder,file_name)
        cv2.imwrite(output_path, image)
        print(f"Saved visualized annotation for {file_name} to {output_path}")

        #
        print("q를 누르면 종료됨")
        if cv2.waitKey(0) & 0xFF == ord('q'):
            #
            data["annotations"] = annotations
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            json_output_path = os.path.join(output_folder, f"annotations_{current_time}.json")

            with open(json_output_path, 'w') as f:
                json_output_path = os.path.join(output_folder, f"annotations_{current_time}.json")

                with open(json_output_path, 'w') as f:
                    json.dump(data, f, indent = 4)

                print(f"Progress saved to {json_output_path}")
                return
            
            image_id += 1

    #
    data["annotations"] = annotations
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_output_path = os.path.join(output_folder, f"annotations_{current_time}.json")

    with open(json_output_path, 'w') as f:
        json.dump(data, f, indent = 4)

    print(f"Final JSON file saved to {json_output_path}")

#
image_folder = "/home/scps/Desktop/jcw_ws/apple/sample/ripe"
output_folder = "/home/scps/Desktop/jcw_ws/json4"

roi_annotation(image_folder, output_folder)
