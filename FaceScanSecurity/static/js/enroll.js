document.addEventListener('DOMContentLoaded', function() {
    // Initialize the camera module
    cameraModule.init('video', 'canvas');
    
    // Get UI elements
    const startCameraBtn = document.getElementById('startCamera');
    const captureImageBtn = document.getElementById('captureImage');
    const enrollUserBtn = document.getElementById('enrollUser');
    const nameInput = document.getElementById('name');
    const resultDiv = document.getElementById('result');
    
    // Variable to store the captured image
    let capturedImage = null;
    
    // Start camera button click handler
    startCameraBtn.addEventListener('click', async function() {
        if (cameraModule.isActive) {
            // Camera is running, stop it
            cameraModule.stop();
            startCameraBtn.innerHTML = '<i class="fas fa-video"></i> Start Camera';
            captureImageBtn.disabled = true;
            enrollUserBtn.disabled = true;
        } else {
            // Start the camera
            const success = await cameraModule.start();
            if (success) {
                startCameraBtn.innerHTML = '<i class="fas fa-video-slash"></i> Stop Camera';
                captureImageBtn.disabled = false;
            }
        }
    });
    
    // Capture image button click handler
    captureImageBtn.addEventListener('click', function() {
        // Capture the current frame from the camera
        capturedImage = cameraModule.capture();
        
        if (capturedImage) {
            // Display the captured image
            const img = new Image();
            img.src = capturedImage;
            img.className = 'img-fluid rounded border';
            
            resultDiv.innerHTML = '';
            resultDiv.appendChild(img);
            resultDiv.style.display = 'block';
            
            // Enable enroll button if name is entered
            enrollUserBtn.disabled = !nameInput.value.trim();
        }
    });
    
    // Enable/disable enroll button based on name input
    nameInput.addEventListener('input', function() {
        enrollUserBtn.disabled = !nameInput.value.trim() || !capturedImage;
    });
    
    // Enroll user button click handler
    enrollUserBtn.addEventListener('click', async function() {
        const name = nameInput.value.trim();
        
        if (!name) {
            showAlert('Please enter your name', 'danger');
            return;
        }
        
        if (!capturedImage) {
            showAlert('Please capture an image first', 'danger');
            return;
        }
        
        // Disable buttons during enrollment
        enrollUserBtn.disabled = true;
        captureImageBtn.disabled = true;
        enrollUserBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enrolling...';
        
        try {
            // Convert the data URL to a Blob
            const imageBlob = cameraModule.dataURLtoBlob(capturedImage);
            
            // Create form data for the API request
            const formData = new FormData();
            formData.append('name', name);
            formData.append('image', imageBlob, 'capture.jpg');
            
            // Send the enrollment request
            const response = await fetch('/api/enroll', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                
                // Reset the form after successful enrollment
                nameInput.value = '';
                capturedImage = null;
                resultDiv.innerHTML = '';
                resultDiv.style.display = 'none';
                
                // Optionally redirect to manage page
                setTimeout(() => {
                    window.location.href = '/manage';
                }, 2000);
            } else {
                showAlert(result.message, 'danger');
                // Re-enable the enroll button
                enrollUserBtn.disabled = false;
            }
        } catch (error) {
            console.error('Error during enrollment:', error);
            showAlert('An error occurred during enrollment', 'danger');
            enrollUserBtn.disabled = false;
        } finally {
            // Reset button text
            enrollUserBtn.innerHTML = '<i class="fas fa-user-plus"></i> Enroll';
            // Re-enable capture button if camera is still active
            if (cameraModule.isActive) {
                captureImageBtn.disabled = false;
            }
        }
    });
    
    // Helper function to display alerts
    function showAlert(message, type) {
        resultDiv.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        resultDiv.style.display = 'block';
    }
});
