import os
import shutil
import random

def split_yolo_dataset(source_folder, dest_folder, split_ratios):
    if sum(split_ratios) != 1.0:
        raise ValueError("Split ratios must sum to 1.0")

    random.seed(42)

    # 저장할 폴더 생성
    for folder in ('train', 'val', 'test'):
        os.makedirs(os.path.join(dest_folder, 'images', folder), exist_ok=True)
        os.makedirs(os.path.join(dest_folder, 'labels', folder), exist_ok=True)

    # 이미지 파일 가져오기
    image_extensions = ('.jpg', '.jpeg', '.png')
    all_files = [f for f in os.listdir(source_folder) if f.lower().endswith(image_extensions)]
    random.shuffle(all_files)

    total_files = len(all_files)
    train_size = int(total_files * split_ratios[0])
    val_size = int(total_files * split_ratios[1])

    train_files = all_files[:train_size]
    val_files = all_files[train_size:train_size + val_size]
    test_files = all_files[train_size + val_size:]

    # 파일 복사 함수
    def copy_files(file_list, split_type):
        for file in file_list:
            shutil.copy(os.path.join(source_folder, file), os.path.join(dest_folder, 'images', split_type, file))
            label_file = file.rsplit('.', 1)[0] + '.txt'
            if os.path.exists(os.path.join(source_folder, label_file)):
                shutil.copy(os.path.join(source_folder, label_file), os.path.join(dest_folder, 'labels', split_type, label_file))

    copy_files(train_files, 'train')
    copy_files(val_files, 'val')
    copy_files(test_files, 'test')

    print("YOLO 데이터셋 분할 완료!")

# 실행
source_folder = "/home/scps/Desktop/마크테스트/Yolo_mark/x64/Release/data/img"
dest_folder = "/home/scps/Desktop/yolo"
split_ratios = (0.6, 0.2, 0.2)

split_yolo_dataset(source_folder, dest_folder, split_ratios)
