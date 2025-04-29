// Common camera handling functions
const cameraModule = {
    videoElement: null,
    canvasElement: null,
    stream: null,
    isActive: false,
    
    init: function(videoId = 'video', canvasId = 'canvas') {
        this.videoElement = document.getElementById(videoId);
        this.canvasElement = document.getElementById(canvasId);
        
        // Update camera status display
        this.updateStatus(false);
    },
    
    start: async function() {
        try {
            // Request access to the user's camera
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: "user"
                }
            });
            
            // Attach the stream to the video element
            this.videoElement.srcObject = this.stream;
            this.isActive = true;
            
            // Update camera status
            this.updateStatus(true);
            
            return true;
        } catch (error) {
            console.error('Error accessing camera:', error);
            // Update status with error
            this.updateStatus(false, error.message);
            return false;
        }
    },
    
    stop: function() {
        if (this.stream) {
            // Stop all tracks in the stream
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
            
            // Clear the video source
            this.videoElement.srcObject = null;
            this.isActive = false;
            
            // Update camera status
            this.updateStatus(false);
        }
    },
    
    capture: function() {
        if (!this.isActive) {
            console.error('Camera is not active');
            return null;
        }
        
        // Set canvas dimensions to match video
        const width = this.videoElement.videoWidth;
        const height = this.videoElement.videoHeight;
        this.canvasElement.width = width;
        this.canvasElement.height = height;
        
        // Draw the current video frame to the canvas
        const context = this.canvasElement.getContext('2d');
        context.drawImage(this.videoElement, 0, 0, width, height);
        
        // Get the image as a data URL (JPEG format)
        return this.canvasElement.toDataURL('image/jpeg', 0.9);
    },
    
    dataURLtoBlob: function(dataURL) {
        // Convert data URL to Blob for easier upload
        const byteString = atob(dataURL.split(',')[1]);
        const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
        
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        
        return new Blob([ab], {type: mimeString});
    },
    
    updateStatus: function(isActive, errorMessage = null) {
        const statusElement = document.getElementById('camera-status');
        if (!statusElement) return;
        
        if (isActive) {
            statusElement.className = 'camera-status bg-success';
            statusElement.innerHTML = '<i class="fas fa-camera"></i> Camera active';
        } else {
            if (errorMessage) {
                statusElement.className = 'camera-status bg-danger';
                statusElement.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${errorMessage}`;
            } else {
                statusElement.className = 'camera-status bg-secondary';
                statusElement.innerHTML = '<i class="fas fa-camera"></i> Camera inactive';
            }
        }
    }
};
