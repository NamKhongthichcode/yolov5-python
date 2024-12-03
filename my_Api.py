import base64
import io
import os
import torch
from flask import Flask, request, render_template, jsonify, Response
import cv2
import pathlib  # for windows
pathlib.PosixPath = pathlib.WindowsPath
from PIL import Image
import urllib.parse

app = Flask(__name__)

# Đường dẫn mô hình YOLOv5
MODEL_PATH = 'weight/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, trust_repo=True)

# Thư mục upload
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# render giao diện webapp
@app.route('/')
def render():
    return  render_template('index.html')

# media have images and videos
@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['file']
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
            filename = file.filename.replace(" ", "_")
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)

            return jsonify({'success': True, 'video_path': f"{urllib.parse.quote(filename)}"}), 200 # string to url

    return jsonify({'success': False, 'error': 'Invalid file format'}), 400


@app.route('/stream_video/<filename>')
def stream_video(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return jsonify({'success': False, 'error': f"Error opening video file: {video_path}"}), 500

    def generate_frames():
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Dự đoán và xử lý khung hình với YOLOv5
            results = model(frame)
            detected_frame = results.render()[0]

            # Encode frame thành JPEG để stream
            _, buffer = cv2.imencode('.jpg', detected_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        cap.release()  # Giải phóng tài nguyên video
        os.remove(video_path)  # Xóa file video

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Sử lý webcam
@app.route('/webcam')
def webcam_stream():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({"error": "Webcam not available"}), 400

    def generate_frames():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Xử lý YOLO
            results = model(frame)
            results.render()

            # Encode frame thành JPEG
            _, buffer = cv2.imencode('.jpg', results.ims[0])

            # Trả frame dưới dạng HTTP Streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        cap.release()  # Giải phóng tài nguyên webcam

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)