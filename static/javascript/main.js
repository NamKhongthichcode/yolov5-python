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
        formData.append("media", file);

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
                    const detectedVideo = document.getElementById("detectedVideo");

                    if (data.image_data) {
                        detectedImage.style.display = "block";
                        detectedImage.src = 'data:image/jpeg;base64,' + data.image_data;
                        detectedVideo.style.display = "none";
                    } else if (data.video_path) {
                        const videoSource = document.getElementById("videoSource");

                        console.log("thanh cong upload video");

                        detectedVideo.src = '/results/' + encodeURIComponent(data.video_path); // Correct video URL
                        detectedVideo.style.display = "block";

                        const videoType = data.video_path.split('.').pop().toLowerCase(); // Lấy phần mở rộng từ video path, ví dụ: 'mp4'

                        // Cập nhật thông tin định dạng video
                        videoFormat.textContent = "Video format: " + videoType.toUpperCase();  // Hiển thị định dạng video
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
});
