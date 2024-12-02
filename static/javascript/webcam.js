const startCaptureButton = document.getElementById('start-capture');
        const stopCaptureButton = document.getElementById('stop-capture');
        const sendVideoButton = document.getElementById('send-video');
        const videoElement = document.getElementById('webcam-video');

        // Biến để lưu stream của webcam
        let mediaStream = null;
        let captureInterval = null;

        // Bắt đầu webcam khi nhấn nút
        startCaptureButton.addEventListener('click', async () => {
            try {
                // Truy cập webcam
                mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
                videoElement.srcObject = mediaStream; // Gán stream vào video tag

                // Bật nút dừng và vô hiệu hóa nút bắt đầu
                startCaptureButton.disabled = true;
                stopCaptureButton.disabled = false;

                // Gửi yêu cầu bắt đầu ghi video từ webcam
                const response = await fetch('/capture_video/start', { method: 'GET' });

                if (response.ok) {
                    const data = await response.json();
                    console.log('Video capture started');

                    // Xử lý khi video được ghi xong
                    stopCaptureButton.addEventListener('click', async () => {
                        // Gửi yêu cầu dừng ghi video
                        const stopResponse = await fetch('/capture_video/stop', { method: 'GET' });
                        if (stopResponse.ok) {
                            const stopData = await stopResponse.json();
                            console.log('Video capture stopped. Video saved at:', stopData.video_path);

                            // Bật nút gửi video
                            sendVideoButton.disabled = false;

                            // Gửi video khi nút gửi video được nhấn
                            sendVideoButton.addEventListener('click', async () => {
                                const videoPath = stopData.video_path;
                                const formData = new FormData();
                                formData.append('video', videoPath);

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
                        }
                    });
                } else {
                    console.error('Failed to start video capture:', response.statusText);
                }
            } catch (err) {
                console.error('Error accessing webcam:', err);
            }
        });