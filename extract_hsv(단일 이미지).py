import cv2
import numpy as np

# 클릭한 색상을 표시하고 저장하기 위한 변수
selected_color = None

def click_event(event, x, y, flags, param):
    global selected_color
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
        
        # 선택한 범위를 기반으로 마스크 생성
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        result = cv2.bitwise_and(image, image, mask=mask)
        
        # 결과 출력
        cv2.imshow("Mask", mask)
        cv2.imshow("Filtered Image", result)

# 이미지 불러오기
image_path = "이미지_경로.jpg"  # 이미지 경로를 지정하세요
image = cv2.imread(image_path)

# 이미지를 HSV로 변환
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 창 생성 및 마우스 콜백 함수 연결
cv2.imshow("Image", image)
cv2.setMouseCallback("Image", click_event)

# 종료 대기
cv2.waitKey(0)
cv2.destroyAllWindows()
