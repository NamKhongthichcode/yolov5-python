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
        document.getElementById("Video").style.display = "none";
        document.getElementById("detectedImage").style.display = "none";
        document.getElementById("detectedVideo").style.display = "none";
        clear_content.style.display = "block";
    });

//    fileInput.addEventListener("change", function (event) {
//        const file = event.target.files[0];
//        if (file) {
//            const reader = new FileReader();
//            const clear_content = document.querySelector('.drop_click');
//            reader.onload = function (e) {
//                const img = document.getElementById("imageDisplay");
//                img.src = e.target.result;
//                img.style.display = "block";
//                clear_content.style.display = "none";
//            };
//            reader.readAsDataURL(file);
//        }
//    });
    fileInput.addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
        const clear_content = document.querySelector('.drop_click');
        const img = document.getElementById("imageDisplay");
        const vi = document.getElementById("Video");
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
        } else if (fileType.startsWith("video")) {
            const reader = new FileReader();
            reader.onload = function (e) {
                vi.src = e.target.result;
                vi.style.display = "block";
                video.src = e.target.result;
                video.style.display = "block";
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
                if (data.success) {

                    const detectedImage = document.getElementById("detectedImage");
                    const detectedVideo = document.getElementById("detectedVideo");

                    if (data.image_data) {
                        // Hiển thị ảnh nhận diện dưới dạng base64
                        console.log("true day la anh ")
                        detectedImage.style.display = "block";
                        detectedImage.src = 'data:image/jpeg;base64,' + data.image_data;
                        detectedVideo.style.display = "none";

                    } else if (data.video_data) {
                        // Hiển thị video dưới dạng base64 (hoặc có thể xử lý URL video)
                        console.log("true dung la video");
                        detectedVideo.style.display = "block";
                        detectedVideo.src = 'data:video/mp4;base64,' + data.video_data;
                        detectedImage.style.display = "none";
                    }
                } else {
                    console.error("Error during detection:", data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });
});
