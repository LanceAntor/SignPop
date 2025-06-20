from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import random
import time
import threading
from hand_detector import HandSignDetector

app = Flask(__name__)

# Initialize the detector
detector = HandSignDetector('Model/keras_model.h5', 'Model/labels.txt')

# Game state variables
score = 0
lives = 3
game_active = False
game_started = False
falling_letters = []
camera = None
lock = threading.Lock()  # For thread safety
last_prediction = {"label": None, "confidence": 0}

# Define the exact dark blue color to match CSS
DARK_BLUE = (51, 0, 13)  # BGR format for OpenCV (equivalent to #0d0033)

class FallingLetter:
    def __init__(self, letter, x, y):
        self.letter = letter
        self.x = x
        self.y = y
        self.speed = random.randint(2, 5)
        self.active = True

def init_camera():
    global camera
    try:
        # If camera exists but isn't open, release it first
        if camera is not None and not camera.isOpened():
            camera.release()
            camera = None
            
        # Initialize a new camera if needed
        if camera is None:
            camera = cv2.VideoCapture(0)
            camera.set(3, 640)
            camera.set(4, 480)
            # Check if camera opened successfully
            if not camera.isOpened():
                print("Error: Could not open camera.")
                # Try alternative camera index
                camera = cv2.VideoCapture(1)
                if not camera.isOpened():
                    print("Error: Could not open camera with alternative index.")
    except Exception as e:
        print(f"Camera initialization error: {e}")
    return camera

def generate_frames():
    global score, lives, game_active, game_started, falling_letters, last_prediction, camera
    
    # Only initialize camera if game is active
    if game_active and game_started:
        camera = init_camera()
    
    # No initial letters - start with empty list
    with lock:
        falling_letters = []
    
    last_letter_time = time.time()
    letter_interval = 3.0  # Time between new letters
    
    while True:
        # Reinitialize camera if game is active but camera is None or closed
        if game_active and game_started and (camera is None or not camera.isOpened()):
            camera = init_camera()
            
        # Create canvas with EXACT dark blue background matching CSS
        canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        canvas[:, :] = DARK_BLUE
        
        # Only process camera and game logic if game is active
        if game_active:
            success = False
            frame = None
            
            if camera is not None and camera.isOpened():
                success, frame = camera.read()
            
            if success and frame is not None:
                # Mirror the frame
                frame = cv2.flip(frame, 1)
                
                # Process hand sign detection
                predicted_label, confidence, _, _ = detector.detect_hand_sign(frame)
                last_prediction = {"label": predicted_label, "confidence": confidence}
                
                # Add new falling letter at random intervals
                current_time = time.time()
                if current_time - last_letter_time > letter_interval:
                    letter = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", 
                                          "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", 
                                          "W", "X", "Y", "Z"])
                    x_pos = random.randint(80, 550)
                    with lock:
                        falling_letters.append(FallingLetter(letter, x_pos, 150))
                    last_letter_time = current_time
                    letter_interval = random.uniform(2.0, 5.0)  # Random interval
                
                # Process letters
                letters_to_remove = []
                with lock:
                    for i, letter_obj in enumerate(falling_letters):
                        # Update position
                        letter_obj.y += letter_obj.speed
                        
                        # Check if letter hit bottom
                        if letter_obj.y > 450:
                            letters_to_remove.append(i)
                            lives -= 1
                            if lives <= 0:
                                game_active = False
                        
                        # Check if letter was detected
                        if last_prediction["label"] == letter_obj.letter and last_prediction["confidence"] > 75 and letter_obj.active:
                            # Visual effect for popped letter
                            cv2.circle(canvas, (letter_obj.x, letter_obj.y), 45, (0, 255, 0), 3)
                            letters_to_remove.append(i)
                            score += 10
                            # Reset the prediction after it's used
                            last_prediction = {"label": None, "confidence": 0}
                    
                    # Remove letters (in reverse order to avoid index issues)
                    for i in sorted(letters_to_remove, reverse=True):
                        if i < len(falling_letters):
                            falling_letters.pop(i)
        
        # Draw falling letters regardless of game state
        with lock:
            for letter_obj in falling_letters:
                # Draw letter circle with consistent color
                cv2.circle(canvas, (letter_obj.x, letter_obj.y), 40, (180, 0, 180), -1)
                cv2.putText(canvas, letter_obj.letter, 
                          (letter_obj.x - 12, letter_obj.y + 15), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # Convert canvas to JPEG
        ret, buffer = cv2.imencode('.jpg', canvas)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_feed')
def camera_feed():
    """Provide raw camera feed for the camera panel"""
    def generate_camera():
        global camera
        
        while True:
            # Reinitialize camera if game is active but camera is None or closed
            if game_started and (camera is None or not camera.isOpened()):
                camera = init_camera()
                
            # Only show camera if game has started
            if game_started:
                if camera is not None and camera.isOpened():
                    success, frame = camera.read()
                    
                    if not success:
                        # Create a blank frame with message if camera fails
                        frame = np.zeros((150, 200, 3), dtype=np.uint8)
                        # frame[:, :] = DARK_BLUE
                        cv2.putText(frame, "No camera", (50, 75), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    else:
                        # Mirror the frame
                        frame = cv2.flip(frame, 1)
                        
                        # Resize for efficiency
                        frame = cv2.resize(frame, (200, 150))
                else:
                    # Create a blank frame with message if camera not initialized
                    frame = np.zeros((150, 200, 3), dtype=np.uint8)
                    frame[:, :] = DARK_BLUE
                    cv2.putText(frame, "No camera", (50, 75), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                # If game hasn't started, show camera icon instead
                frame = np.zeros((150, 200, 3), dtype=np.uint8)
                frame[:, :] = DARK_BLUE
                
                # Draw a simple camera icon
                cv2.rectangle(frame, (70, 60), (130, 100), (180, 0, 180), -1)  # Camera body
                cv2.rectangle(frame, (130, 70), (145, 90), (180, 0, 180), -1)  # Camera lens
            
            # Convert to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                  
    return Response(generate_camera(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_game')
def start_game():
    global game_active, game_started, score, lives, falling_letters, last_prediction, camera
    
    # Make sure to initialize the camera
    camera = init_camera()
    
    game_active = True
    game_started = True
    score = 0
    lives = 3
    last_prediction = {"label": None, "confidence": 0}
    
    # No initial letters - start with empty list
    with lock:
        falling_letters = []
        
    return jsonify({'status': 'success'})

# Add this function to release the camera
def release_camera():
    global camera
    if camera is not None and camera.isOpened():
        camera.release()
        camera = None
        print("Camera released")

# Update the end_game function in your Flask app
@app.route('/end_game')
def end_game():
    global game_active, game_started, camera, score, falling_letters
    game_active = False
    game_started = False
    
    # Save the current score before releasing the camera
    final_score = score
    
    # Clear all falling letters
    with lock:
        falling_letters = []
    
    # Release the camera
    release_camera()
    
    return jsonify({
        'status': 'success',
        'score': final_score
    })

@app.route('/get_status')
def get_status():
    return jsonify({
        'game_active': game_active,
        'game_started': game_started,
        'score': score,
        'lives': lives,
        'letters_count': len(falling_letters)
    })

if __name__ == '__main__':
    app.run(debug=True)