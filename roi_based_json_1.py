import os
import json
import cv2
import numpy as np
from datetime import datetime

# 경로 설정
image_folder = "/home/scps/Desktop/jcw_ws/json_train"
output_folder = "/mnt/data"

# 기존 annotation 파일 로드
annotation_file = os.path.join(image_folder, "annotations_2025-02-14_21-27-37.json")

with open(annotation_file, "r") as f:
    coco_data = json.load(f)

# 기존 데이터에서 이미지 ID 확인
existing_image_ids = {img["file_name"]: img["id"] for img in coco_data["images"]}
existing_annotations = coco_data["annotations"]
next_annotation_id = max([ann["id"] for ann in existing_annotations]) + 1 if existing_annotations else 0
next_image_id = max([img["id"] for img in coco_data["images"]]) + 1 if existing_image_ids else 1

# prev_roi 파일 목록 가져오기
roi_files = [f for f in os.listdir(image_folder) if f.startswith("prev_roi_") and f.endswith(".json")]

for roi_file in roi_files:
    roi_path = os.path.join(image_folder, roi_file)

    # 이미지 파일명 추출
    image_file = roi_file.replace("prev_roi_", "").replace(".json", "")
    image_path = os.path.join(image_folder, image_file)

    if not os.path.exists(image_path):
        print(f"이미지 {image_file}가 존재하지 않습니다. 스킵합니다.")
        continue

    # ROI 정보 로드
    with open(roi_path, "r") as f:
        roi_data = json.load(f)
    roi = roi_data.get("roi", [])

    if len(roi) != 4:
        print(f"ROI 정보가 올바르지 않습니다: {roi}")
        continue

    x, y, w, h = roi

    # 이미지 읽기
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지 {image_file}를 불러올 수 없습니다. 스킵합니다.")
        continue

    height, width, _ = image.shape

    # 이미지 정보 추가
    if image_file not in existing_image_ids:
        image_id = next_image_id
        coco_data["images"].append({"id": image_id, "width": width, "height": height, "file_name": image_file})
        existing_image_ids[image_file] = image_id
        next_image_id += 1
    else:
        image_id = existing_image_ids[image_file]

    # ROI 영역 처리
    roi_image = image[y:y+h, x:x+w]
    roi_rgb = cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB)

    # 블랙 마스크 생성
    lower_black = np.array([0, 0, 0], dtype=np.uint8)
    upper_black = np.array([75, 100, 125], dtype=np.uint8)
    mask_black = cv2.inRange(roi_rgb, lower_black, upper_black)

    # 컨투어 추출
    contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 기존 annotation 정보 확인
    file_category = image_file.split('_')[1]  # ex) ripe, semi, unripe
    category_map = {"godoo": 1, "tanjeo": 2, "yeolgwa": 3}
    category_id = category_map.get(file_category, None)
    if category_id is None:
        print(f"파일 {image_file}의 카테고리를 찾을 수 없습니다. 스킵합니다.")
        continue

    for contour in contours:
        if cv2.contourArea(contour) < 50:
            continue

        contour = contour + np.array([x, y])  # ROI 좌표를 전체 이미지 좌표로 변환
        bx, by, bw, bh = cv2.boundingRect(contour)
        bbox = [bx, by, bw, bh]
        segmentation = contour.flatten().tolist()

        annotation = {
            "id": next_annotation_id,
            "iscrowd": 0,
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": [segmentation],
            "bbox": bbox,
            "area": float(cv2.contourArea(contour))
        }
        existing_annotations.append(annotation)
        next_annotation_id += 1

# 최종 annotation JSON 저장
coco_data["annotations"] = existing_annotations
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_json_path = os.path.join(output_folder, f"annotations_{timestamp}.json")

with open(output_json_path, "w") as f:
    json.dump(coco_data, f, indent=4)

print(f"최종 annotation 파일이 저장되었습니다: {output_json_path}")