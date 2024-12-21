document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('image');
    const fileNameSpan = document.getElementById('file-name');

    if (imageInput && fileNameSpan) {
        imageInput.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : "No file chosen";
            fileNameSpan.textContent = fileName;
        });
    }
});
