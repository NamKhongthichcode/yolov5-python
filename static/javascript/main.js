document.addEventListener("DOMContentLoaded", () => {
  const uploadArea = document.getElementById("upload-area");
  const fileInput = document.getElementById("file-input");
  const clearButton = document.getElementById("clear-button");
  const btnSelect = document.getElementById("button-select");

  // Khi click vào khu vực tải lên
  uploadArea.addEventListener("click", () => {
    fileInput.click();
  });
  btnSelect.addEventListener("click", () => {
    fileInput.click();
  });

  // Kéo thả file vào khu vực tải lên
  uploadArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadArea.style.backgroundColor = "#333";
  });

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.backgroundColor = "#2d2d2d";
  });

  uploadArea.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadArea.style.backgroundColor = "#2d2d2d";
    const files = event.dataTransfer.files;
    if (files.length) {
      fileInput.files = files;
      console.log("File dropped:", files[0]);
      const file = files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const img = document.getElementById("imageDisplay");
          img.src = e.target.result;
          img.style.display = "block";
        };
        reader.readAsDataURL(file);
      }
    }
  });

  // Xóa file đã chọn khi nhấn "Clear"
  clearButton.addEventListener("click", () => {
    fileInput.value = "";
    console.log("File input cleared");
  });

  document
    .getElementById("file-input")
    .addEventListener("change", function (event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const img = document.getElementById("imageDisplay");
          img.src = e.target.result;
          img.style.display = "block";
        };
        reader.readAsDataURL(file);
      }
    });


});
