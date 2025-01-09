import cv2
import numpy as np
import os

# ROI 선택 함수
def select_roi(image):
    # ROI 선택
    roi = cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    x, y, w, h = map(int, roi)
    cropped_image = image[y:y+h, x:x+w]  # ROI로 이미지 자르기
    cv2.destroyWindow("Select ROI")
    return cropped_image

# 색상 정보 추출 함수
def extract_hsv_info(cropped_image):
    # BGR에서 HSV로 변환
    hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

    # HSV 평균값 계산
    mean_hue = np.mean(hsv_image[:, :, 0])  # Hue
    mean_saturation = np.mean(hsv_image[:, :, 1])  # Saturation
    mean_value = np.mean(hsv_image[:, :, 2])  # Value

    # 결과 출력
    print(f"Mean HSV: Hue={mean_hue:.2f}, Saturation={mean_saturation:.2f}, Value={mean_value:.2f}")
    return hsv_image

# 폴더 내 모든 이미지 처리
image_folder_path = "./apple/ripe_고두"  # 이미지가 저장된 폴더 경로
image_files = [f for f in os.listdir(image_folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

for image_file in image_files:
    image_path = os.path.join(image_folder_path, image_file)
    print(f"처리 중: {image_path}")
    image = cv2.imread(image_path)

    if image is None:
        print(f"이미지 {image_path}를 불러오지 못했습니다.")
        continue

    # 원본 이미지 출력
    cv2.imshow("Original Image", image)

    # ROI 선택 및 이미지 자르기
    cropped_image = select_roi(image)

    if cropped_image.size == 0:
        print("ROI를 선택하지 않았습니다. 다음 이미지로 넘어갑니다.")
        continue

    # 자른 이미지 출력
    cv2.imshow("Cropped Image", cropped_image)

    # HSV 정보 추출
    hsv_image = extract_hsv_info(cropped_image)

    # 결과 저장 (선택 사항)
    save_path = os.path.join(image_folder_path, f"cropped_{image_file}")
    cv2.imwrite(save_path, cropped_image)
    print(f"잘라낸 이미지가 {save_path}에 저장되었습니다.")

    # 'q' 키를 누르면 다음 이미지로 넘어감
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

cv2.destroyAllWindows()