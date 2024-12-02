document.addEventListener("DOMContentLoaded", () => {
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const clearButton = document.getElementById("clear-button");
    const btnSelect = document.getElementById("button-select");
    const submitButton = document.getElementById("submit-button");

    // Handle click events for selecting files
    uploadArea.addEventListener("click", () => {
        fileInput.click();
    });

    btnSelect.addEventListener("click", () => {
        fileInput.click();
    });

    clearButton.addEventListener("click", () => {
        fileInput.value = "";
        const clear_content = document.querySelector('.drop_click');
        document.getElementById("imageDisplay").style.display = "none";
        document.getElementById("videoDisplay").style.display = "none";
        document.getElementById("detectedImage").style.display = "none";
        document.getElementById("detectedVideo").style.display = "none";
        document.getElementById("detectedWebcam").style.display = "none"
        clear_content.style.display = "block";
    });

    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
            const clear_content = document.querySelector('.drop_click');
            const img = document.getElementById("imageDisplay");
            const vi = document.getElementById("videoDisplay");
            const video = document.getElementById("detectedVideo");
            const fileType = file.type;

            if (fileType.startsWith("image")) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    img.src = e.target.result;
                    img.style.display = "block";
                    video.style.display = "none";
                    clear_content.style.display = "none";
                };
                reader.readAsDataURL(file);
            } else if (fileType.startsWith("video") || fileType === "video/x-fmp4") {
                const reader = new FileReader();

                reader.onload = function (e) {
                    vi.src = e.target.result;
                    console.log(vi.src);
                    vi.style.display = "block";
                    img.style.display = "none";
                    clear_content.style.display = "none";
                };
                reader.readAsDataURL(file);
            }
        }
    });

    submitButton.addEventListener("click", function (event) {
        event.preventDefault();  // Prevent form submission

        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a file first.");
            return;
        }

        // Hiển thị thông báo đang xử lý
        const processingDiv = document.getElementById("xu_ly");
        processingDiv.style.display = "block";


        // Create FormData object to send the file
        const formData = new FormData();
        formData.append("file", file);

        // Send the file to the server using fetch
        fetch("/upload_media", {
            method: "POST",  // Ensure method is POST
            body: formData,  // Send the FormData containing the file
        })
            .then(response => response.json())
            .then(data => {
                processingDiv.style.display = "none"; // Ẩn thông báo khi hoàn tất xử lý

                if (data.success) {
                    const detectedImage = document.getElementById("detectedImage");

                    if (data.image_data) {

                        detectedImage.style.display = "block";
                        detectedImage.src = 'data:image/jpeg;base64,' + data.image_data;
                        detectedVideo.style.display = "none";

                    } else if (data.video_path) {

                        const videoSource = document.getElementById("videoSource");
                        detectedVideo.src = '/results/' + encodeURIComponent(data.video_path); // Correct video URL
                        detectedVideo.style.display = "block";
                        const videoType = data.video_path.split('.').pop().toLowerCase(); // Lấy phần mở rộng từ video path, ví dụ: 'mp4'
                        videoFormat.style.display = "block";  // Hiển thị thông tin định dạng


                        console.log(detectedVideo.src);
                        detectedImage.style.display = "none";
                    }
                } else {
                processingDiv.style.display = "none"; // Ẩn thông báo khi failed
                    console.error("Error during detection:", data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });

//    document.getElementById("webcam-button").addEventListener("click", function() {
//    const webcamVideo = document.getElementById("detectedWebcam");
//
//    // Ẩn các phần khác khi chuyển sang webcam
//    document.getElementById("detectedImage").style.display = "none";  // Ẩn ảnh phát hiện
//    document.getElementById("detectedVideo").style.display = "none";  // Ẩn video phát hiện
//
//    // Hiển thị video webcam
//    webcamVideo.style.display = "block"; // Hiển thị video webcam
//
//    // Kiểm tra nếu webcam đã sẵn sàng
//    webcamVideo.src = "/webcam_feed";  // Set nguồn video là từ route webcam_feed
//    webcamVideo.load();  // Đảm bảo video được tải
//    webcamVideo.play();  // Chạy video
//});
});