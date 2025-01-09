import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import json
import os
from datetime import datetime
import numpy as np

class ImageLabelingApp:
    def __init__(self, root, image_folder, json_folder):
        self.root = root
        self.image_folder = image_folder
        self.json_folder = json_folder
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
        self.current_index = 0
        self.category_map = {"godoo": 1, "yeolgwa": 2, "tanger": 3}
        self.json_path = self.generate_json_filename()
        self.json_data = self.load_or_create_json()
        self.current_segmentation = []  # 탐지된 폴리곤 좌표 저장

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        # 자동 탐지 버튼
        self.auto_detect_button = tk.Button(self.button_frame, text="Auto Detect", command=self.auto_detect)
        self.auto_detect_button.pack(side=tk.LEFT, padx=10, pady=10)

        # 저장 및 다음 이미지 버튼
        self.save_next_button = tk.Button(self.button_frame, text="Save and Next", command=self.save_and_next_image)
        self.save_next_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.load_image()

    def generate_json_filename(self):
        """현재 시간을 기반으로 JSON 파일 이름 생성"""
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        json_filename = f"annotations_{current_time}.json"
        return os.path.join(self.json_folder, json_filename)

    def load_or_create_json(self):
        """JSON 파일을 로드하거나 없으면 새로 생성"""
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                print(f"Loaded existing JSON: {self.json_path}")
                return json.load(f)
        else:
            print(f"No JSON found. Creating new JSON: {self.json_path}")
            new_json = {
                "images": [],
                "annotations": [],
                "categories": [
                    {"id": 1, "name": "godoo"},
                    {"id": 2, "name": "yeolgwa"},
                    {"id": 3, "name": "tanger"}
                ]
            }
            self.save_json(new_json)
            return new_json

    def save_json(self, data=None):
        """JSON 파일 저장"""
        if data is None:
            data = self.json_data
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_image(self):
        """이미지 로드 및 초기화"""
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Info", "All images have been labeled.")
            return

        self.current_segmentation = []
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        self.cv_image = cv2.imread(image_path)

        self.original_width = self.cv_image.shape[1]
        self.original_height = self.cv_image.shape[0]

        self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(self.cv_image)

        self.display_width = 800
        self.display_height = 600
        pil_image = pil_image.resize((self.display_width, self.display_height))

        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=self.tk_image)

    def detect_polygons_by_color(self, image, lower_color, upper_color):
        """색상 범위를 기준으로 객체 탐지"""
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv_image, lower_color, upper_color)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygons = [contour.flatten().tolist() for contour in contours if cv2.contourArea(contour) > 10]
        return polygons

    def auto_detect(self):
        """현재 이미지에 대해 색상 기반 자동 탐지를 수행하고 시각화"""
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])

        # # 색상 범위 설정 (예: 빨간색 범위)
        # lower_red = np.array([0, 100, 100])  # HSV 값
        # upper_red = np.array([10, 255, 255])

        lower_red = np.array([0,0,0])
        upper_red = np.array([180, 255, 50])

        polygons = self.detect_polygons_by_color(self.cv_image, lower_red, upper_red)

        if not polygons:
            messagebox.showinfo("Info", "No objects detected based on color.")
            return

        # 탐지된 폴리곤 시각화
        for polygon in polygons:
            points = np.array(polygon).reshape(-1, 2)
            cv2.polylines(self.cv_image, [points], isClosed=True, color=(0, 255, 0), thickness=2)

        pil_image = Image.fromarray(self.cv_image)
        pil_image = pil_image.resize((self.display_width, self.display_height))
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=self.tk_image)

        self.current_segmentation = polygons  # 탐지된 폴리곤 저장
        messagebox.showinfo("Info", f"{len(polygons)} objects detected based on color.")

    def save_and_next_image(self):
        """탐지된 폴리곤 데이터를 저장하고 다음 이미지로 이동"""
        if not self.current_segmentation:
            messagebox.showwarning("Warning", "No segmentation data to save.")
            return

        image_id = self.current_index + 1
        image_file = self.image_files[self.current_index]

        # JSON 이미지 섹션 업데이트
        if not any(img["id"] == image_id for img in self.json_data["images"]):
            self.json_data["images"].append({
                "id": image_id,
                "file_name": image_file,
                "width": self.original_width,
                "height": self.original_height
            })

        # JSON annotation 섹션 업데이트
        for polygon in self.current_segmentation:
            annotation = {
                "id": len(self.json_data["annotations"]) + 1,
                "image_id": image_id,
                "category_id": self.category_map["godoo"],  # 기본값으로 godoo 사용
                "segmentation": [polygon],
                "bbox": [
                    min(polygon[::2]),
                    min(polygon[1::2]),
                    max(polygon[::2]) - min(polygon[::2]),
                    max(polygon[1::2]) - min(polygon[1::2])
                ],
                "area": 0  # 면적 계산 가능 (추가 작업 필요)
            }
            self.json_data["annotations"].append(annotation)

        self.save_json()
        self.current_index += 1
        self.load_image()

# --- 실행 ---
if __name__ == "__main__":
    image_folder = "./apple/ripe_고두"  # 라벨링할 이미지 폴더 경로
    json_folder = "./json"  # JSON 파일 저장 폴더

    root = tk.Tk()
    root.title("Image Labeling Tool")
    app = ImageLabelingApp(root, image_folder, json_folder)
    root.mainloop()
