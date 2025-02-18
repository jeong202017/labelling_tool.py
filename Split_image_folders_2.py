import os
import shutil
import random

def split_images_into_folders(source_folder, dest_folder, split_ratios, folder_names=('train', 'val', 'test')):
    """
    source_folder 안의 파일들을 split_ratios에 따라 folder_names의 하위 폴더로 복사하는 함수
    
    :param source_folder: 원본 이미지가 있는 폴더 경로
    :param dest_folder: 분할된 파일을 저장할 루트 폴더 경로
    :param split_ratios: (train, val, test) 비율 합이 1이 되어야 함
    :param folder_names: 생성할 폴더 이름 (기본값: ('train', 'val', 'test'))
    """
    if sum(split_ratios) != 1.0:
        raise ValueError("Split ratios must sum to 1.0")
    
    # 폴더 생성
    os.makedirs(dest_folder, exist_ok=True)
    for folder in folder_names:
        os.makedirs(os.path.join(dest_folder, folder), exist_ok=True)
    
    # 원본 폴더에서 이미지 파일 리스트 가져오기
    all_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    random.shuffle(all_files)  # 무작위 섞기
    
    # 비율에 따라 나누기
    total_files = len(all_files)
    train_size = int(total_files * split_ratios[0])
    val_size = int(total_files * split_ratios[1])
    
    train_files = all_files[:train_size]
    val_files = all_files[train_size:train_size + val_size]
    test_files = all_files[train_size + val_size:]
    
    # 파일 복사
    for file in train_files:
        shutil.copy(os.path.join(source_folder, file), os.path.join(dest_folder, folder_names[0], file))
    for file in val_files:
        shutil.copy(os.path.join(source_folder, file), os.path.join(dest_folder, folder_names[1], file))
    for file in test_files:
        shutil.copy(os.path.join(source_folder, file), os.path.join(dest_folder, folder_names[2], file))
    
    print("파일 복사 완료!")

# 사용 예제
source_folder = "/home/scps/Desktop/auto_label/jpgs/distance_test"  # 원본 이미지 폴더 경로 입력
#클래스명 godoo(bitter pit) / tanjeo(anthrax) / yeolgwa(crack)
dest_folder = "/home/scps/Desktop/yolo"  # 분할된 데이터가 저장될 폴더
split_ratios = (0.6, 0.2, 0.2)  # Train: 70%, Val: 20%, Test: 10%

split_images_into_folders(source_folder, dest_folder, split_ratios)
