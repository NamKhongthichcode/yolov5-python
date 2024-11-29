import base64
import io
import os
import torch
from flask import Flask, request, render_template, jsonify, Response
import cv2
import pathlib  # for windows
pathlib.PosixPath = pathlib.WindowsPath
from PIL import Image
import time
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
        results = model(frame)
        annotated_frame = results.render()[0]  # Render các bounding box lên frame

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
    return  render_template('index.html')

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
        if file_extension in {'mp4'}:

            video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(video_path)
            return Response(process_video(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

    return jsonify({'success': False, 'error': 'Invalid file format'}), 400

if __name__ == '__main__':
    app.run(debug=True)