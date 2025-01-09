import cv2
import json
import numpy as np
import os


def visualize_and_annotate_black_regions(image_folder, json_path, output_folder):
    # JSON 파일 로드
    with open(json_path, 'r') as f:
        data = json.load(f)

    # 이미지 ID와 파일 이름 매핑
    image_map = {img['id']: img['file_name'] for img in data['images']}

    # 어노테이션 리스트에 새로운 데이터를 추가하기 위해 초기화
    new_annotations = []

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

        # HSV 변환 및 검정색 영역 검출
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([179, 255, 50])
        mask = cv2.inRange(hsv, lower_black, upper_black)

        # 검출된 영역에서 컨투어 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 50:  # 너무 작은 영역은 무시
                continue

            # Bounding Box 계산
            x, y, w, h = cv2.boundingRect(contour)
            bbox = [x, y, w, h]

            # Segmentation 좌표 생성
            segmentation = contour.flatten().tolist()

            # 새로운 어노테이션 추가
            new_annotation = {
                "id": len(new_annotations) + 1,
                "image_id": image_id,
                "category_id": 1,  # 검정색 영역을 위한 임의의 카테고리 ID
                "segmentation": [segmentation],
                "area": float(cv2.contourArea(contour)),
                "bbox": bbox,
                "iscrowd": 0
            }
            new_annotations.append(new_annotation)

            # Bounding Box와 Segmentation 시각화
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 초록색 박스
            cv2.polylines(image, [np.array(segmentation).reshape(-1, 2)], isClosed=True, color=(255, 0, 0), thickness=2)  # 파란색 폴리곤

        # 출력 폴더에 저장
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, file_name)
        cv2.imwrite(output_path, image)
        print(f"Saved visualized annotation for {file_name} to {output_path}")

    # 기존 JSON 데이터에 새로운 어노테이션 추가
    data['annotations'].extend(new_annotations)

    # 업데이트된 JSON 파일 저장
    updated_json_path = os.path.join(output_folder, "updated_annotations.json")
    with open(updated_json_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Updated JSON file saved to {updated_json_path}")


# --- 실행 ---
image_folder = "./apple/ripe_고두"  # 라벨링된 이미지 폴더 경로
json_path = "./json/annotations_2024-12-30_16-49-24.json"  # JSON 파일 경로
output_folder = "./visual2"  # 시각화 결과 저장 폴더

visualize_and_annotate_black_regions(image_folder, json_path, output_folder)