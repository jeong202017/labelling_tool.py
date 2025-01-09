import cv2
import numpy as np
import os

# 클릭한 색상을 표시하고 저장하기 위한 변수
selected_color = None

def click_event(event, x, y, flags, param):
    global selected_color, hsv_image
    if event == cv2.EVENT_LBUTTONDOWN:  # 왼쪽 버튼 클릭 시
        # 클릭한 위치의 픽셀 값(BGR)
        bgr_color = image[y, x]

        # BGR을 HSV로 변환
        hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]

        # HSV 값 출력
        print(f"Clicked HSV: {hsv_color}")

        # 클릭한 색상의 범위 설정
        hue, sat, val = hsv_color
        lower_bound = np.array([max(hue - 10, 0), max(sat - 40, 0), max(val - 40, 0)])
        upper_bound = np.array([min(hue + 10, 179), min(sat + 40, 255), min(val + 40, 255)])
        print(f"Lower Bound: {lower_bound}, Upper Bound: {upper_bound}")

        selected_color = (lower_bound, upper_bound)

        # 마스크 생성 및 결과 출력
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        result = cv2.bitwise_and(image, image, mask=mask)

        # 결과 표시
        cv2.imshow("Mask", mask)
        cv2.imshow("Filtered Image", result)

# 폴더 경로 설정
image_folder_path = "./apple/ripe_고두"  # 이미지가 저장된 폴더 경로
image_files = [f for f in os.listdir(image_folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

# 폴더 내 모든 이미지 처리
for image_file in image_files:
    image_path = os.path.join(image_folder_path, image_file)
    print(f"처리 중: {image_path}")
    image = cv2.imread(image_path)

    if image is None:
        print(f"이미지 {image_path}를 불러오지 못했습니다.")
        continue

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 창 생성 및 마우스 콜백 함수 설정
    cv2.imshow("Image", image)
    cv2.setMouseCallback("Image", click_event)

    # 'q' 키를 누르면 다음 이미지로 넘어감
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

cv2.destroyAllWindows()