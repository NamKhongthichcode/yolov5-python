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
# from moviepy.editor import VideoFileClip

app = Flask(__name__)

# Đường dẫn mô hình YOLOv5
MODEL_PATH = 'weight/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, trust_repo=True)

# Thư mục upload và kết quả
app.config['RESULT_FOLDER'] = './results'
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# render giao diện webapp
@app.route('/')
def render():
    return  render_template('index.html')

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Để tải video từ thư mục kết quả
@app.route('/results/<path:filename>')
def download_result_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)




# media have images and video
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
        # Xử lý video
        if file_extension in {'mp4'}:
            filename = file.filename.replace(" ", "_")
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            result_path = os.path.join(app.config['RESULT_FOLDER'], filename)
            file.save(video_path)

            # Mở video bằng OpenCV
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return jsonify({'success': False, 'error': f"Error opening video file: {video_path}"}), 500

            # Lấy thông tin codec, FPS, chiều rộng và chiều cao của video
            fourcc = cv2.VideoWriter_fourcc(*'H264')  # Codec cho MP4
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Kiểm tra thông tin video
            print(f"Video codec: {fourcc} | FPS: {fps} | Width: {frame_width} | Height: {frame_height}")

            # Ghi video đã xử lý vào tệp kết quả
            out = cv2.VideoWriter(result_path, fourcc, fps, (frame_width, frame_height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                # Dự đoán và xử lý khung hình với YOLOv5
                results = model(frame)
                detected_frame = results.render()[0]
                out.write(detected_frame)

            cap.release()
            out.release()

            # Kiểm tra lại định dạng video kết quả
            cap_result = cv2.VideoCapture(result_path)
            if cap_result.isOpened():
                result_fourcc = int(cap_result.get(cv2.CAP_PROP_FOURCC))
                result_codec = chr((result_fourcc & 0xFF)) + chr((result_fourcc >> 8 & 0xFF)) + \
                               chr((result_fourcc >> 16 & 0xFF)) + chr((result_fourcc >> 24 & 0xFF))
                print(f"Result video codec: {result_codec}")  # Hiển thị codec của video kết quả

            # Kiểm tra nếu tệp video đã được tạo thành công
            if os.path.exists(result_path):
                return jsonify({'success': True, 'video_path': f"{urllib.parse.quote(filename)}"})
            else:
                return jsonify({'success': False, 'error': 'Failed to process video.'}), 500


    return jsonify({'success': False, 'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True)
