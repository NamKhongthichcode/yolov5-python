import base64
import io
import os
import threading

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

is_capturing = False
cap = None
out = None
video_thread = None

def capture_video():
    global cap, out, is_capturing
    cap = cv2.VideoCapture(0)  # Mở webcam (0 là ID của webcam mặc định)
    if not cap.isOpened():
        return jsonify({'success': False, 'error': 'Could not open webcam.'}), 500

    # Lấy thông tin video như codec, FPS và chiều rộng, chiều cao của webcam
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Ghi video từ webcam vào file kết quả
    result_path = './results/webcam_output.mp4'
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    out = cv2.VideoWriter(result_path, fourcc, fps, (frame_width, frame_height))

    # Quay video trong vòng lặp
    while cap.isOpened() and is_capturing:
        ret, frame = cap.read()
        if not ret:
            break
        # Dự đoán và xử lý khung hình với YOLOv5
        results = model(frame)
        detected_frame = results.render()[0]
        out.write(detected_frame)

    cap.release()
    out.release()


@app.route('/capture_video/start', methods=['GET'])
def start_capture():
    global is_capturing, video_thread
    if not is_capturing:
        is_capturing = True
        video_thread = threading.Thread(target=capture_video)
        video_thread.start()
        return jsonify({'success': True, 'message': 'Video capture started.'}), 200
    else:
        return jsonify({'success': False, 'error': 'Capture is already running.'}), 400

@app.route('/capture_video/stop', methods=['GET'])
def stop_capture():
    global is_capturing, video_thread
    if is_capturing:
        is_capturing = False
        video_thread.join()  # Chờ cho thread dừng lại
        if os.path.exists('./results/webcam_output.mp4'):
            return jsonify({'success': True, 'video_path': '/results/webcam_output.mp4'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to save video.'}), 500
    else:
        return jsonify({'success': False, 'error': 'Capture is not running.'}), 400


@app.route('/upload_video', methods=['POST'])
def upload_video():
    video_path = request.form.get('video_path')
    if video_path:
        # Thực hiện xử lý video, ví dụ lưu vào thư mục server
        save_path = './uploaded_videos/' + os.path.basename(video_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Chép video từ kết quả capture sang thư mục upload
        try:
            os.rename(video_path, save_path)
            return jsonify({'success': True, 'message': 'Video uploaded successfully.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to upload video: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'error': 'No video file received.'}), 400


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
