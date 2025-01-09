import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import json
import os
from datetime import datetime  # 현재 시간 가져오기

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
        self.current_segmentation = []  # 현재 폴리곤 좌표 저장

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        for category in self.category_map.keys():
            btn = tk.Button(self.button_frame, text=category, command=lambda c=category: self.save_polygon(c))
            btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(root, text="Next Image", command=self.next_image)
        self.next_button.pack(pady=10)

        self.load_image()

        # 마우스 클릭 이벤트 연결
        self.image_label.bind("<Button-1>", self.add_polygon_point)

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
            # 새 JSON 기본 구조 생성
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
            messagebox.showinfo("Info", f"New JSON file created: {self.json_path}")
            return new_json

    def save_json(self, data=None):
        """JSON 파일 저장"""
        if data is None:
            data = self.json_data
        with open(self.json_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_image(self):
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Info", "All images have been labeled.")
            return

        self.current_segmentation = []  # 새 이미지로 이동 시 초기화
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        self.cv_image = cv2.imread(image_path)

        # 원본 이미지 크기 저장
        self.original_width = self.cv_image.shape[1]
        self.original_height = self.cv_image.shape[0]

        self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(self.cv_image)

        # Tkinter에 표시할 크기로 조정
        self.display_width = 800
        self.display_height = 600
        pil_image = pil_image.resize((self.display_width, self.display_height))  # 이미지 크기 조정

        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=self.tk_image)

    def add_polygon_point(self, event):
        """이미지 클릭 시 폴리곤 좌표 추가"""
        # 표시된 이미지에서 클릭한 좌표를 원본 이미지 좌표로 변환
        scale_x = self.original_width / self.display_width
        scale_y = self.original_height / self.display_height
        x = int(event.x * scale_x)
        y = int(event.y * scale_y)

        self.current_segmentation.append((x, y))
        print(f"Added point (Original): ({x}, {y})")

        # 화면에 클릭한 점 표시 (변환된 좌표 사용하지 않고 표시된 이미지 기준으로 표시)
        cv2.circle(self.cv_image, (x, y), radius=5, color=(0, 255, 0), thickness=-1)
        pil_image = Image.fromarray(self.cv_image)
        pil_image = pil_image.resize((self.display_width, self.display_height))  # 이미지 크기 조정
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=self.tk_image)

    def save_polygon(self, category):
        """현재 폴리곤을 JSON에 저장"""
        if not self.current_segmentation:
            messagebox.showwarning("Warning", "No polygon points to save.")
            return

        image_id = self.current_index + 1
        image_file = self.image_files[self.current_index]

        # JSON 이미지 섹션 업데이트
        if not any(img["id"] == image_id for img in self.json_data["images"]):
            self.json_data["images"].append({
                "id": image_id,
                "file_name": image_file,
                "width": self.original_width,  # 실제 이미지 크기
                "height": self.original_height
            })

        # JSON annotation 섹션 업데이트
        annotation = {
            "id": len(self.json_data["annotations"]) + 1,
            "image_id": image_id,
            "category_id": self.category_map[category],
            "segmentation": [sum(self.current_segmentation, ())],  # 폴리곤 좌표
            "bbox": [
                min(pt[0] for pt in self.current_segmentation),  # x_min
                min(pt[1] for pt in self.current_segmentation),  # y_min
                max(pt[0] for pt in self.current_segmentation) - min(pt[0] for pt in self.current_segmentation),  # width
                max(pt[1] for pt in self.current_segmentation) - min(pt[1] for pt in self.current_segmentation)   # height
            ],
            "area": 0  # 폴리곤 면적 계산 가능 (추가 작업 필요)
        }
        self.json_data["annotations"].append(annotation)
        self.save_json()

        # 저장 후 초기화
        self.current_segmentation = []
        messagebox.showinfo("Info", f"Polygon for '{category}' saved.")

    def next_image(self):
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