import os
import shutil
import random
import json

# 원본 데이터셋 폴더 경로
dataset_dir = "/mnt/data/dataset"  # 이미지와 JSON 파일이 함께 있는 폴더

# 데이터를 나눌 비율 설정
split_ratio = {"train": 0.7, "val": 0.2, "test": 0.1}

# 대상 폴더 경로
output_dir = "/mnt/data/split_dataset"
os.makedirs(output_dir, exist_ok=True)
for split in split_ratio.keys():
    os.makedirs(os.path.join(output_dir, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, split, "annotations"), exist_ok=True)

# 파일 리스트 가져오기
image_files = [f for f in os.listdir(dataset_dir) if f.endswith(".jpg")]
json_files = [f for f in os.listdir(dataset_dir) if f.endswith(".json")]

# JSON 파일과 이미지 파일 매칭
matched_files = []
for img_file in image_files:
    json_file = f"prev_roi_{img_file}.json"
    if json_file in json_files:
        matched_files.append((img_file, json_file))

# 데이터 섞기
random.shuffle(matched_files)

# 데이터 분할
total_files = len(matched_files)
train_count = int(total_files * split_ratio["train"])
val_count = int(total_files * split_ratio["val"])

train_files = matched_files[:train_count]
val_files = matched_files[train_count:train_count + val_count]
test_files = matched_files[train_count + val_count:]

# 파일 이동 함수
def move_files(file_list, split_name):
    for img, json in file_list:
        shutil.move(os.path.join(dataset_dir, img), os.path.join(output_dir, split_name, "images", img))
        shutil.move(os.path.join(dataset_dir, json), os.path.join(output_dir, split_name, "annotations", json))

# 데이터 이동
move_files(train_files, "train")
move_files(val_files, "val")
move_files(test_files, "test")

print("데이터 분할 완료!")