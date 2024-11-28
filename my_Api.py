import base64
import io
import os
from operator import index
import torch
from flask import Flask, request, render_template, jsonify, Response, send_file
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pathlib  # for windows
from pathlib import Path
pathlib.PosixPath = pathlib.WindowsPath
from matplotlib import pyplot as plt
from PIL import Image
from flask_cors import CORS

app = Flask(__name__)

# Đường dẫn mô hình YOLOv5
MODEL_PATH = 'weight/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, trust_repo=True)

# Thư mục upload và kết quả
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def render():
    return  render_template('index.html')

@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'media' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['media']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file and allowed_file(file.filename):

        # lấy đuôi file
        file_extension = file.filename.rsplit('.', 1)[1].lower()

        # Xử lý ảnh
        if file_extension in {'png', 'jpg', 'jpeg'}:

            img = Image.open(file.stream) # PIL Image object

            # Xử lý ảnh và nhận diện với YOLOv5
            results = model(img)

            # Mã hóa ảnh kết quả dưới dạng base64
            img_result = results.render()[0]  # Kết quả ảnh đã nhận diện
            buffered = io.BytesIO()
            img_result = Image.fromarray(img_result)
            img_result.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            return jsonify({'success': True, 'image_data': img_base64})

        # Xử lý video
        elif file_extension in {'mp4'}:
            # Lưu video vào tệp tạm thời
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(video_path)

            # Xử lý video với YOLOv5 (có thể có thêm bước nhận diện nếu cần)
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if not ret:
                return jsonify({'success': False, 'error': 'Error reading video file'})

            # Mã hóa video thành base64 (chỉ xử lý frame đầu tiên trong ví dụ này)
            _, buffer = cv2.imencode('.jpg', frame)
            video_base64 = base64.b64encode(buffer).decode("utf-8")

            # Nếu muốn trả về URL video, có thể thay đổi thành URL của video đã lưu trên server
            return jsonify({'success': True, 'video_data': video_base64})

        return jsonify({'success': False, 'error': 'Invalid file format'})

if __name__ == "__main__":
    app.run(debug=True)