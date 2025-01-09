import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import json
import os

class ImageLabelingApp:
    def __init__(self, root, image_folder, json_path):
        self.root = root
        self.image_folder = image_folder
        self.json_path = json_path
        self.image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
        self.current_index = 0
        self.category_map = {"godoo": 1, "yeolgwa": 2, "tanger": 3}
        self.json_data = self.load_json()
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

    def load_json(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                return json.load(f)
        else:
            return {"images": [], "annotations": [], "categories": [
                {"id": 1, "name": "godoo"},
                {"id": 2, "name": "yeolgwa"},
                {"id": 3, "name": "tanger"}
            ]}

    def save_json(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.json_data, f, indent=4)

    def load_image(self):
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Info", "All images have been labeled.")
            return

        self.current_segmentation = []  # 새 이미지로 이동 시 초기화
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        self.cv_image = cv2.imread(image_path)
        self.cv_image = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(self.cv_image)
        pil_image = pil_image.resize((800, 600))  # 이미지 크기 조정
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=self.tk_image)

    def add_polygon_point(self, event):
        """이미지 클릭 시 폴리곤 좌표 추가"""
        x = event.x
        y = event.y
        self.current_segmentation.append((x, y))
        print(f"Added point: ({x}, {y})")

        # 화면에 클릭한 점 표시
        cv2.circle(self.cv_image, (x, y), radius=5, color=(0, 255, 0), thickness=-1)
        pil_image = Image.fromarray(self.cv_image)
        pil_image = pil_image.resize((800, 600))  # 이미지 크기 조정
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
                "width": 800,  # 실제 이미지 크기 설정
                "height": 600
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
    json_path = "./json/labels_my-project-name_2024-12-30-01-54-16.json"  # 업데이트할 JSON 파일 경로

    root = tk.Tk()
    root.title("Image Labeling Tool")
    app = ImageLabelingApp(root, image_folder, json_path)
    root.mainloop()
