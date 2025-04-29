document.addEventListener('DOMContentLoaded', function() {
    // Initialize the camera module
    cameraModule.init('video', 'canvas');
    
    // Get UI elements
    const startCameraBtn = document.getElementById('startCamera');
    const verifyFaceBtn = document.getElementById('verifyFace');
    const resultDiv = document.getElementById('result');
    const authSuccessDiv = document.getElementById('authSuccess');
    const authFailureDiv = document.getElementById('authFailure');
    const userNameSpan = document.getElementById('userName');
    const confidenceScoreSpan = document.getElementById('confidenceScore');
    
    // Start camera button click handler
    startCameraBtn.addEventListener('click', async function() {
        if (cameraModule.isActive) {
            // Camera is running, stop it
            cameraModule.stop();
            startCameraBtn.innerHTML = '<i class="fas fa-video"></i> Start Camera';
            verifyFaceBtn.disabled = true;
        } else {
            // Start the camera
            const success = await cameraModule.start();
            if (success) {
                startCameraBtn.innerHTML = '<i class="fas fa-video-slash"></i> Stop Camera';
                verifyFaceBtn.disabled = false;
            }
        }
    });
    
    // Verify face button click handler
    verifyFaceBtn.addEventListener('click', async function() {
        if (!cameraModule.isActive) {
            showAlert('Camera is not active', 'danger');
            return;
        }
        
        // Capture the current frame from the camera
        const capturedImage = cameraModule.capture();
        
        if (!capturedImage) {
            showAlert('Failed to capture image', 'danger');
            return;
        }
        
        // Disable the verify button and show loading state
        verifyFaceBtn.disabled = true;
        verifyFaceBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verifying...';
        
        // Hide previous results
        authSuccessDiv.style.display = 'none';
        authFailureDiv.style.display = 'none';
        
        try {
            // Convert the data URL to a Blob
            const imageBlob = cameraModule.dataURLtoBlob(capturedImage);
            
            // Create form data for the API request
            const formData = new FormData();
            formData.append('image', imageBlob, 'verification.jpg');
            
            // Send the verification request
            const response = await fetch('/api/verify', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                if (result.authenticated) {
                    // Authentication successful
                    userNameSpan.textContent = result.user;
                    confidenceScoreSpan.textContent = result.confidence;
                    authSuccessDiv.style.display = 'block';
                    
                    // Add animated effects
                    animateSuccess();
                } else {
                    // Authentication failed
                    authFailureDiv.style.display = 'block';
                    
                    // Add animated effects
                    animateFailure();
                }
            } else {
                // API error
                showAlert(result.message, 'danger');
            }
        } catch (error) {
            console.error('Error during verification:', error);
            showAlert('An error occurred during verification', 'danger');
        } finally {
            // Reset button state
            verifyFaceBtn.innerHTML = '<i class="fas fa-user-check"></i> Verify Identity';
            if (cameraModule.isActive) {
                verifyFaceBtn.disabled = false;
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
    
    // Animate success result
    function animateSuccess() {
        const icon = authSuccessDiv.querySelector('.auth-icon');
        if (icon) {
            icon.classList.add('animate-success');
            setTimeout(() => {
                icon.classList.remove('animate-success');
            }, 1000);
        }
    }
    
    // Animate failure result
    function animateFailure() {
        const icon = authFailureDiv.querySelector('.auth-icon');
        if (icon) {
            icon.classList.add('animate-failure');
            setTimeout(() => {
                icon.classList.remove('animate-failure');
            }, 1000);
        }
    }
});
