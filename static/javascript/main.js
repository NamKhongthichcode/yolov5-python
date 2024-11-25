document.addEventListener("DOMContentLoaded", () => {
    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const clearButton = document.getElementById("clear-button");
    const submitButton = document.getElementById("submit-button");
    const uploadForm = document.getElementById("upload-form");

    // Khi click vào khu vực tải lên, mở file input
    uploadArea.addEventListener("click", () => {
        fileInput.click();
    });

    // Xử lý kéo thả file vào khu vực tải lên
    uploadArea.addEventListener("dragover", (event) => {
        event.preventDefault();  // Chặn hành động mặc định
        uploadArea.style.backgroundColor = "#333";  // Thay đổi màu nền khi kéo thả
    });

    uploadArea.addEventListener("dragleave", () => {
        uploadArea.style.backgroundColor = "#2d2d2d";  // Đổi lại màu nền khi kéo ra ngoài
    });

    uploadArea.addEventListener("drop", (event) => {
        event.preventDefault();
        uploadArea.style.backgroundColor = "#2d2d2d";  // Đổi lại màu nền khi thả file
        const files = event.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;  // Cập nhật file input với file thả vào
            console.log("File dropped:", files[0]);
        }
    });

    // Xóa file đã chọn khi nhấn "Clear"
    clearButton.addEventListener("click", () => {
        fileInput.value = "";  // Xóa nội dung file input
        uploadArea.style.backgroundColor = "#2d2d2d";  // Đổi lại màu nền ban đầu
        console.log("File input cleared");
    });

    // Gửi ảnh lên server khi nhấn "Submit"
    submitButton.addEventListener("click", (event) => {
        event.preventDefault();
        if (fileInput.files.length > 0) {
            const formData = new FormData(uploadForm);  // Tạo đối tượng FormData với dữ liệu từ form

            fetch("http://127.0.0.1:5000/upload_image", {  // Đổi URL thành URL của server thực tế
                method: "POST",
                body: formData  // Gửi FormData chứa file lên server
            })
            .then(response => response.json())
            .then(data => {
                console.log("Upload successful:", data);
                // Có thể xử lý kết quả trả về tại đây, ví dụ như hiển thị thông báo thành công
            })
            .catch(error => {
                console.error("Upload failed:", error);
                alert("Upload failed. Please try again.");  // Thông báo lỗi nếu upload thất bại
            });
        } else {
            alert("Please select an image first.");  // Thông báo nếu chưa chọn ảnh
        }
    });
});
