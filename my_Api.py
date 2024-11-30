# app.py

import base64
import io
import os
import torch
from flask import Flask, request, render_template, jsonify, send_from_directory
import cv2
import pathlib  # for windows
pathlib.PosixPath = pathlib.WindowsPath
from PIL import Image
import time
import urllib.parse

app = Flask(__name__)

# Đường dẫn mô hình YOLOv5
MODEL_PATH = 'weight/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, trust_repo=True)

# Thư mục upload và kết quả
app.config['RESULT_FOLDER'] = './Result'
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Phát hiện đối tượng với YOLOv5
        with torch.no_grad(), torch.amp.autocast('cuda'):
            results = model(frame)
            annotated_frame = results.render()[0]

        # Debug thông tin
        print("Processing frame...")
        print(f"Results: {results}")

        # Chuyển đổi frame thành định dạng JPEG và trả về
        ret, jpeg = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        time.sleep(0.03)  # Thời gian trễ để đồng bộ video

    cap.release()

# render giao diện webapp
@app.route('/')
def render():
    return render_template('index.html')

# media have images and video
@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'media' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['media']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file and allowed_file(file.filename):
        file_extension = file.filename.rsplit('.', 1)[1].lower()

        if file_extension in {'png', 'jpg', 'jpeg'}:
            img = Image.open(file.stream)
            results = model(img)
            img_result = results.render()[0]
            buffered = io.BytesIO()
            img_result = Image.fromarray(img_result)
            img_result.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return jsonify({'success': True, 'image_data': img_base64})

        if file_extension in {'mp4'}:
            filename = file.filename.replace(" ", "_")  # Thay khoảng trắng bằng dấu gạch dưới
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            return jsonify({'success': True, 'video_path': urllib.parse.quote(filename)})

    return jsonify({'success': False, 'error': 'Invalid file format'}), 400

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)