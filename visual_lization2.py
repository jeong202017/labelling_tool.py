import cv2
import json
import numpy as np
import os

def visualize_annotations(image_folder, json_path, output_folder):
    # JSON 파일 로드
    with open(json_path, 'r') as f:
        data = json.load(f)

    # 이미지 ID와 파일 이름 매핑
    image_map = {img['id']: img['file_name'] for img in data['images']}

    # 어노테이션 반복 처리
    for annotation in data['annotations']:
        image_id = annotation['image_id']
        file_name = image_map.get(image_id, None)

        if file_name is None:
            print(f"No matching file for image_id: {image_id}. Skipping...")
            continue

        image_path = os.path.join(image_folder, file_name)

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print(f"Image {file_name} not found. Skipping...")
            continue

        # Bounding Box 유효성 검사
        bbox = annotation.get('bbox', [])
        if len(bbox) != 4:
            print(f"Invalid bbox for annotation ID {annotation['id']}: {bbox}. Skipping...")
            continue

        # Bounding Box 그리기
        x, y, w, h = map(int, bbox)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색 박스

        # Segmentation 그리기
        for segmentation in annotation.get('segmentation', []):
            if len(segmentation) > 0:
                points = np.array(segmentation).reshape(-1, 2).astype(int)
                cv2.polylines(image, [points], isClosed=True, color=(255, 0, 0), thickness=2)  # 파란색 폴리곤

        # 출력 폴더에 저장
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, file_name)
        cv2.imwrite(output_path, image)
        print(f"Saved visualized annotation for {file_name} to {output_path}")

    print("Visualization completed.")

# --- 실행 ---
image_folder = "./apple/ripe_고두"  # 라벨링된 이미지 폴더 경로
json_path = "./json/annotations_2024-12-30_16-49-24.json"  # JSON 파일 경로
output_folder = "./visual"  # 시각화 결과 저장 폴더

visualize_annotations(image_folder, json_path, output_folder)