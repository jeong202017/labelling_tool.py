import os
import re

def rename_images_in_folder(folder_path):
    # 파일명 패턴 정규식 (ripe_godoo2_000123.jpg 같은 형식)
    pattern = re.compile(r"ripe_godoo\d+_(\d+)\.jpg")
    
    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            number = match.group(1)  # 기존 숫자 추출
            new_filename = f"ripe_godoo_{number}.jpg"
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            
            if old_file != new_file:
                os.rename(old_file, new_file)
                print(f"Renamed: {filename} -> {new_filename}")
    
folder_path = "/home/scps/Desktop/jcw_ws/apple/1월 20일/ripe/ripe_godoo"  # 변경할 폴더 경로 입력
rename_images_in_folder(folder_path)
