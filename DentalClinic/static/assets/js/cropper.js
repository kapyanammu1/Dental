// Event listener for image input change
document.getElementById('image-input').addEventListener('change', function(event) {
    const imageInput = event.target;
    const previewImage = document.getElementById('cropper-preview');
    const file = imageInput.files[0];

    if (file) {
        // Display the selected image in the preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';

            // Destroy existing cropper instance if any
            if (window.cropper) {
                window.cropper.destroy();
            }

            // Initialize Cropper.js on the preview image
            window.cropper = new Cropper(previewImage, {
                aspectRatio: 1, // Adjust as needed, 1 for square
                viewMode: 1,
                autoCropArea: 1,
                movable: true,
                scalable: true,
                zoomable: true,
                rotatable: true,
            });
        };
        reader.readAsDataURL(file);
    }
});

// Event listener for saving the cropped image
document.getElementById('save-cropped-image').addEventListener('click', function(event) {
    event.preventDefault(); 
    console.log("Save button clicked");

    if (window.cropper) {
        // Get the cropped image as a Data URL
        const croppedCanvas = window.cropper.getCroppedCanvas();
        const croppedDataURL = croppedCanvas.toDataURL('image/jpeg');
        console.log(croppedDataURL);
        // Update the background image of the preview wrapper
        const previewWrapper = document.getElementById('image-preview-wrapper');
        previewWrapper.style.backgroundImage = `url(${croppedDataURL})`;
        
        // Hide the original preview image as the background is now updated
        document.getElementById('cropper-preview').style.display = 'none';
        console.log("Cropped image applied to preview");
    }
});
