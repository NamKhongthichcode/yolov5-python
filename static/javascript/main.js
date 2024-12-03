document.addEventListener("DOMContentLoaded", () => {
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const clearButton = document.getElementById("clear-button");
    const btnSelect = document.getElementById("button-select");
    const submitButton = document.getElementById("submit-button");
    const webcamButton = document.getElementById("webcam-button");

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
        document.getElementById("detectedWebcam").style.display = "none";
            // Ngừng luồng webcam
        const webcamOutput = document.getElementById("detectedWebcam");
        const VideoOutput = document.getElementById("detectedVideo");
        webcamOutput.src = ""; // Ngắt kết nối luồng
        VideoOutput.src = ""; // Ngắt kết nối luồng
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

//        // Hiển thị thông báo đang xử lý
//        const processingDiv = document.getElementById("xu_ly");
//        processingDiv.style.display = "block";


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

//                processingDiv.style.display = "none"; // Ẩn thông báo khi hoàn tất xử lý

                if (data.success) {
                    const detectedImage = document.getElementById("detectedImage");
                    const detectedVideo = document.getElementById("detectedVideo");

                    if (data.image_data) {

                        detectedImage.style.display = "block";
                        detectedImage.src = 'data:image/jpeg;base64,' + data.image_data;
                        detectedVideo.style.display = "none";

                    } else if (data.video_path){
                        // Hiển thị video khi có video_path
                        detectedImage.style.display = "none";
                        detectedVideo.style.display = "block";
                        detectedVideo.src = '/stream_video/' + encodeURIComponent(data.video_path);
                    }
                } else {
//                processingDiv.style.display = "none"; // Ẩn thông báo khi failed
                    console.error("Error during detection:", data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });

    if (webcamButton) {
        webcamButton.addEventListener("click", function () {
            console.log("Webcam button clicked"); // Kiểm tra xem sự kiện click đã được kích hoạt
           // Hiển thị thẻ img và gán src là luồng từ Flask
            const webcamImage = document.getElementById("detectedWebcam");
            webcamImage.style.display = "block";
            webcamImage.src = "/webcam"; // Đặt src là endpoint Flask

            });
    } else {
        console.error("Nút Webcam không tồn tại trong DOM.");
    }


});