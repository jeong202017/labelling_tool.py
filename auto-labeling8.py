import cv2
import numpy as np
import json
import os
from datetime import datetime

# 폴더 경로 설정
image_folder_path = "./apple/ripe_고두"
output_folder_path = "./json"

# 오늘 날짜와 시간대로 JSON 파일 이름 설정
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_json_path = os.path.join(output_folder_path, f"annotations_{current_datetime}.json")

# COCO 형식의 annotation 데이터 초기화
coco_data = {
    "images": [],
    "annotations": [],
    "categories": [
        {"id": 1, "name": "godoo"},
        {"id": 2, "name": "yeolgwa"},
        {"id": 3, "name": "tanger"}
    ]
}

image_id = 1
annotation_id = 1

# 폴더 내 모든 이미지 파일 처리
for file_name in os.listdir(image_folder_path):
    if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(image_folder_path, file_name)

        # 이미지 읽기
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not read image: {file_name}")
            continue

        original_image = image.copy()

        # BGR -> HSV 변환
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 검정색 영역 추출
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([179, 140, 100])
        black_mask = cv2.inRange(hsv_image, lower_black, upper_black)

        # 컨투어 찾기
        contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 이미지 정보 추가
        coco_data["images"].append({
            "id": image_id,
            "file_name": file_name,
            "width": image.shape[1],
            "height": image.shape[0]
        })

        for contour in contours:
            # 컨투어 영역이 너무 작으면 무시
            if cv2.contourArea(contour) < 10:
                continue

            # Bounding box 계산
            x, y, w, h = cv2.boundingRect(contour)

            # segmentation 좌표 계산
            segmentation = contour.flatten().tolist()

            # annotation 추가
            coco_data["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 1,  # godoo 카테고리 ID
                "segmentation": [segmentation],
                "area": int(cv2.contourArea(contour)),
                "bbox": [x, y, w, h],
                "iscrowd": 0
            })
            annotation_id += 1

        image_id += 1

# JSON 파일 저장
with open(output_json_path, 'w') as json_file:
    json.dump(coco_data, json_file, indent=4)

print(f"COCO format annotations saved to {output_json_path}")
