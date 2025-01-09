import tkinter as tk
from tkinter import filedialog
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
        
        self.image_label = tk.Label(root)
        self.image_label.pack()
        
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        
        for category in self.category_map.keys():
            btn = tk.Button(self.button_frame, text=category, command=lambda c=category: self.add_annotation(c))
            btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.next_button = tk.Button(root, text="Next Image", command=self.next_image)
        self.next_button.pack(pady=10)

        self.load_image()

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
            tk.messagebox.showinfo("Info", "All images have been labeled.")
            return
        
        image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
        cv_image = cv2.imread(image_path)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        pil_image = pil_image.resize((800, 600))  # 이미지 크기 조정
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=self.tk_image)
    
    def add_annotation(self, category):
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
            "segmentation": [],  # 실제 segmentation 데이터 추가 필요
            "bbox": [],  # 실제 bounding box 추가 필요
            "area": 0  # 면적 계산 추가 필요
        }
        self.json_data["annotations"].append(annotation)
        
        self.save_json()
        tk.messagebox.showinfo("Info", f"Annotation for '{category}' added.")
    
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