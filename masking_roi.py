import cv2
import numpy as np
import os

def select_roi_and_mask(image):
    # ROI 선택
    roi = cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    x, y, w, h = map(int, roi)

    # 선택된 ROI로 이미지 자르기
    cropped_image = image[y:y+h, x:x+w]
    cv2.destroyWindow("Select ROI")
    
    # HSV 변환
    hsv_cropped = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

    # HSV 범위 설정
    # lower_bound = np.array([0, 50, 50])  # 기본값: 조정 가능
    # upper_bound = np.array([10, 255, 255])

    lower_black = np.array([0,0,0])
    upper_black = np.array([179,140,100])

    # 마스크 생성
    mask = cv2.inRange(hsv_cropped, lower_black, upper_black)
    result = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)

    # 결과 출력
    cv2.imshow("Cropped ROI", cropped_image)
    cv2.imshow("Mask", mask)
    cv2.imshow("Masked Result", result)
    
    # HSV 범위 조정 기능 추가
    print("마스킹 HSV 범위:")
    print(f"Lower Bound: {lower_black}")
    print(f"Upper Bound: {upper_black}")
    
    return cropped_image, mask, result

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

    # 원본 이미지 출력
    cv2.imshow("Original Image", image)

    # ROI 선택 및 마스킹 작업
    cropped_image, mask, result = select_roi_and_mask(image)

    # 결과 저장 (선택 사항)
    save_cropped_path = os.path.join(image_folder_path, f"cropped_{image_file}")
    save_mask_path = os.path.join(image_folder_path, f"mask_{image_file}")
    cv2.imwrite(save_cropped_path, cropped_image)
    cv2.imwrite(save_mask_path, mask)
    print(f"잘라낸 이미지가 {save_cropped_path}에 저장되었습니다.")
    print(f"마스크 이미지가 {save_mask_path}에 저장되었습니다.")

    # 'q' 키를 누르면 다음 이미지로 넘어감
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

cv2.destroyAllWindows()