import base64
import os
import torch
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import pathlib  # for windows
from pathlib import Path
pathlib.PosixPath = pathlib.WindowsPath

# Khởi tạo Flask
app = Flask(__name__)

# Đường dẫn tới thư mục chứa trọng số của YOLOv5
MODEL_PATH = 'weight/best.pt'

# Tải mô hình YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, trust_repo=False)
img_path = '"C:/Users/Nam/Desktop/40623737-chuối-và-táo-vuông-thành-phần-2-bị-cô-lập-trên-nền-trắng-là-yếu-tố-thiết-kế-bao-bì.jpg"'
result = model(img_path)
result.render()

# # Định nghĩa các định dạng file hợp lệ
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# # Kiểm tra định dạng file hợp lệ
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
# # Route chính để render trang HTML
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# # Route sử lý hình ảnh
# @app.route('/upload_image', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image file part"}), 400
#
#     image = request.files['image']
#
#     if image.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#
#     if not allowed_file(image.filename):
#         return jsonify({"error": "Invalid image file type"}), 400
#
#     # Lưu file hình ảnh
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
#     image.save(file_path)
#
#     # Xử lý ảnh với YOLOv5
#     results = model(file_path)
#     results.render()  # Render ảnh
#
#     # Lưu ảnh đã render
#     output_image_path = file_path.replace('.jpg', '_output.jpg').replace('.jpeg', '_output.jpeg').replace('.png', '_output.png')
#     cv2.imwrite(output_image_path, results.imgs[0])  # Lưu ảnh đã render
#
#     return jsonify({
#         "message": "Image processed successfully",
#         "output_image": output_image_path
#     })
#
# # Route xử lý video
# @app.route('/upload_video', methods=['POST'])
# def upload_video():
#     if 'video' not in request.files:
#         return jsonify({"error": "No video file part"}), 400
#
#     video = request.files['video']
#     if video.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#
#     if not allowed_file(video.filename):
#         return jsonify({"error": "Invalid video file type"}), 400
#
#     # Lưu video
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(video.filename))
#     video.save(file_path)
#
#     # Mở video và xử lý frame
#     cap = cv2.VideoCapture(file_path)
#     output_video_path = file_path.replace('.mp4', '_output.mp4')
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (640, 480))
#
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#
#         # Dự đoán bằng YOLOv5
#         results = model(frame)
#         results.render()  # Render ảnh lên frame
#
#         # Lưu frame vào video output
#         out.write(results.imgs[0])  # Lấy ảnh từ kết quả YOLOv5
#
#     cap.release()
#     out.release()
#
#     return jsonify({
#         "message": "Video processed successfully",
#         "output_video": output_video_path
#     })
#
# # Route xử lý webcam
# @app.route('/webcam', methods=['POST'])
# def webcam():
#     # Sử dụng webcam để lấy frame
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         return jsonify({"error": "Webcam not available"}), 400
#
#     ret, frame = cap.read()
#     if not ret:
#         return jsonify({"error": "Failed to capture frame"}), 400
#
#     # Xử lý frame với YOLOv5
#     results = model(frame)
#     results.render()  # Render lên ảnh
#
#     # Chuyển frame thành base64 để trả về
#     _, buffer = cv2.imencode('.jpg', results.imgs[0])
#     base64_frame = base64.b64encode(buffer).decode('utf-8')
#
#     cap.release()
#
#     return jsonify({
#         "message": "Webcam frame processed",
#         "frame": base64_frame
#     })
#
# if __name__ == '__main__':
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])
#     app.run(debug=True)
