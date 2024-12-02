let videoStream;
let mediaRecorder;
let recordedChunks = [];
let videoPath = '';  // Biến để lưu đường dẫn video đã quay

// Lấy các nút
const startCaptureButton = document.getElementById('startCapture');
const stopCaptureButton = document.getElementById('stopCapture');
const sendVideoButton = document.getElementById('sendVideo');

// Khi ấn nút Start Capture
startCaptureButton.addEventListener('click', async () => {
    try {
        // Mở webcam
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = document.createElement('video');
        videoElement.srcObject = videoStream;
        videoElement.play();

        // Tạo MediaRecorder để ghi video
        mediaRecorder = new MediaRecorder(videoStream);
        mediaRecorder.ondataavailable = event => {
            recordedChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            // Khi kết thúc quay video, tạo file video
            const blob = new Blob(recordedChunks, { type: 'video/mp4' });
            const videoFile = new File([blob], 'webcam_output.mp4', { type: 'video/mp4' });

            // Tạo đường dẫn video
            const formData = new FormData();
            formData.append('video', videoFile);

            // Gửi video lên server
            const response = await fetch('/upload_video', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                videoPath = data.video_path;
                console.log('Video uploaded successfully:', videoPath);
            } else {
                console.error('Failed to upload video');
            }
        };

        // Bắt đầu ghi
        mediaRecorder.start();
        startCaptureButton.disabled = true;
        stopCaptureButton.disabled = false;
        sendVideoButton.disabled = true;
    } catch (error) {
        console.error('Error accessing webcam:', error);
    }
});

// Khi ấn nút Stop Capture
stopCaptureButton.addEventListener('click', () => {
    mediaRecorder.stop();
    videoStream.getTracks().forEach(track => track.stop());
    stopCaptureButton.disabled = true;
    sendVideoButton.disabled = false;
});

// Khi ấn nút Send Video
sendVideoButton.addEventListener('click', async () => {
    const formData = new FormData();
    formData.append('video_path', videoPath);

    const uploadResponse = await fetch('/upload_video', {
        method: 'POST',
        body: formData,
    });

    if (uploadResponse.ok) {
        const uploadData = await uploadResponse.json();
        console.log('Video uploaded:', uploadData);
    } else {
        console.error('Failed to upload video.');
    }
});
