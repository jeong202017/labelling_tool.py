import os
import shutil

# 폴더 경로 설정
folder_a = "/home/scps/Desktop/jcw_ws/apple/test"  # 원본 폴더 (비교할 기준)
folder_b = "/home/scps/Desktop/jcw_ws/final_json/image&roi/train"  # 복사될 대상 폴더

# 이미지 확장자 목록
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

# A 폴더의 이미지 파일 리스트 가져오기 (확장자 제외한 파일명만 저장)
a_files = {os.path.splitext(f)[0] for f in os.listdir(folder_a) if os.path.splitext(f)[1].lower() in image_extensions}

# B 폴더의 파일들 중 A에 있는 이미지 파일과 동일한 이름을 가진 파일들 찾기
files_to_copy = [f for f in os.listdir(folder_a) if os.path.splitext(f)[0] in a_files]

# 파일 복사 (B로 이동)
for file in files_to_copy:
    src_path = os.path.join(folder_a, file)
    dest_path = os.path.join(folder_b, file)
    shutil.copy2(src_path, dest_path)  # 메타데이터 유지한 채 복사

print(f"총 {len(files_to_copy)}개의 파일이 {folder_b}로 복사되었습니다.")
