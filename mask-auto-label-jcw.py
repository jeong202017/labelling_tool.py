import cv2
import numpy as np
import json
import os

def extract_black_regions(image_path):
    """이미지에서 검정색 영역의 좌표를 추출"""
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 검정색 범위 설정
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    
    # 윤곽선 추출
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    segmentations = []
    for contour in contours:
        if cv2.contourArea(contour) > 10:  # 작은 영역 제거
            segmentation = contour.flatten().tolist()
            segmentations.append(segmentation)
    return segmentations

def update_json_with_segmentation(json_path, image_id, segmentations, category_id=1):
    """JSON 파일에 segmentation 추가"""
    with open(json_path, 'r') as f:
        data = json.load(f)

    for segmentation in segmentations:
        annotation = {
            "id": len(data["annotations"]) + 1,
            "iscrowd": 0,
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": [segmentation],
            "bbox": [
                min(segmentation[::2]),  # x_min
                min(segmentation[1::2]),  # y_min
                max(segmentation[::2]) - min(segmentation[::2]),  # width
                max(segmentation[1::2]) - min(segmentation[1::2])   # height
            ],
            "area": cv2.contourArea(np.array(segmentation).reshape(-1, 2))  # 면적
        }
        data["annotations"].append(annotation)

    # 업데이트된 JSON 저장
    updated_json_path = os.path.splitext(json_path)[0] + "_updated.json"
    with open(updated_json_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Updated JSON saved to {updated_json_path}")

# --- 실행 ---
def process_folder(image_folder, json_path):
    """폴더 내 모든 이미지를 처리하고 JSON 업데이트"""
    files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
    for idx, file_name in enumerate(files, start=1):
        image_path = os.path.join(image_folder, file_name)
        print(f"Processing {image_path}...")

        # 검정색 영역 추출
        segmentations = extract_black_regions(image_path)

        # JSON 업데이트 (파일 인덱스를 이미지 ID로 사용)
        update_json_with_segmentation(json_path, idx, segmentations)

# --- 폴더 지정 ---
image_folder = "/home/scps/Desktop/jcw_ws/apple/test"  # 이미지 파일이 있는 폴더 경로
json_path = "./test.json"  # JSON 파일 경로

process_folder(image_folder, json_path)

