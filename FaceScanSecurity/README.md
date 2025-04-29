# Face Recognition Authentication System

A web-based face recognition system built with Flask and OpenCV that enables facial authentication.

## Features

- **Face Enrollment**: Register your face in the system
- **Face Verification**: Authenticate using facial recognition
- **User Management**: View and manage registered users
- **Responsive UI**: Works on different devices and screen sizes

## Technology Stack

- **Backend**: Flask (Python)
- **Face Detection**: OpenCV (Haar Cascade Classifiers)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Bootstrap 5 (Replit Dark Theme)

## How It Works

1. **Enrollment**: The system captures your face image through the webcam and extracts facial features
2. **Storage**: These features are securely stored and associated with your profile
3. **Verification**: When verifying, the system compares your current face with stored profiles
4. **Authentication**: If a match is found, access is granted

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/face-recognition-system.git
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Access the application at `http://localhost:5000`

## Project Structure

- `app.py`: Main Flask application with routes and API endpoints
- `face_utils.py`: Face detection and recognition utilities
- `main.py`: Application entry point
- `templates/`: HTML templates for web interface
- `static/`: JavaScript, CSS, and other static assets
- `face_data/`: Directory for storing face encodings and user data

## Security Considerations

- Face data is stored locally and not shared with external services
- Implementation focuses on security and privacy
- Face matching uses distance metrics with customizable tolerance levels