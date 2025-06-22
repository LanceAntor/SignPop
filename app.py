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
letters_hit_bottom = False  # Add this line

# Tutorial mode variables
last_detected_letter = None
tutorial_mode_active = False

# Define the exact dark blue color to match CSS
DARK_BLUE = (51, 0, 13)  # BGR format for OpenCV (equivalent to #0d0033)

class FallingLetter:
    def __init__(self, letter, x, y, base_speed=None):
        self.letter = letter
        self.x = int(x)  # Ensure x is an integer
        self.y = int(y)  # Ensure y is an integer
        # Allow custom base speed or use random
        self.speed = base_speed if base_speed is not None else random.randint(2, 5)
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
    base_letter_interval = 3.0  # Base time between new letters
    
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
                
                # Calculate difficulty modifiers based on score
                speed_multiplier = 1 + (score // 50) * 0.5  # Increase speed by 0.5x every 50 points
                frequency_modifier = max(0.5, 1.0 - (score // 100) * 0.2)  # Decrease interval by 20% every 100 points
                multi_letter_chance = min(80, score // 30)  # Chance to spawn multiple letters (up to 80%)
                
                # Calculate actual letter interval based on score
                letter_interval = base_letter_interval * frequency_modifier
                
                # Add new falling letter at dynamic intervals
                current_time = time.time()
                if current_time - last_letter_time > letter_interval:
                    # Always add at least one letter
                    letter = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", 
                                          "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", 
                                          "W", "X", "Y", "Z"])
                    x_pos = random.randint(80, 550)
                    
                    # Start letters at the top of the game area, just slightly below the border
                    y_pos = 50  # Use a smaller value to appear at the top edge of the border
                    
                    with lock:
                        # Calculate base speed with some randomness but adjust for difficulty
                        base_speed = random.randint(2, 5) * speed_multiplier
                        falling_letters.append(FallingLetter(letter, x_pos, y_pos, base_speed))
                    
                    # Chance to add additional letters as score increases
                    if random.randint(1, 100) <= multi_letter_chance:
                        num_extra = min(3, score // 150 + 1)  # Add up to 3 extra letters based on score
                        for _ in range(num_extra):
                            extra_letter = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", 
                                                       "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", 
                                                       "W", "X", "Y", "Z"])
                            extra_x = random.randint(80, 550)
                            with lock:
                                falling_letters.append(FallingLetter(extra_letter, extra_x, y_pos, base_speed))
                    
                    last_letter_time = current_time
                    # Reset the timer with some randomness
                    base_letter_interval = random.uniform(2.0, 4.0)
                
                # Process letters
                letters_to_remove = []
                letters_hit_bottom = False  # Flag to indicate if any letters hit bottom in this frame

                with lock:
                    for i, letter_obj in enumerate(falling_letters):
                        # Update position - letters fall faster as score increases
                        letter_obj.y += letter_obj.speed
                        
                        # Check if letter hit bottom
                        if letter_obj.y > 450:
                            letters_to_remove.append(i)
                            lives -= 1
                            letters_hit_bottom = True  # Set flag when letter hits bottom
                            if lives <= 0:
                                game_active = False
                        
                        # Check if letter was detected
                        if last_prediction["label"] == letter_obj.letter and last_prediction["confidence"] > 75 and letter_obj.active:
                            # Visual effect for popped letter
                            cv2.circle(canvas, (int(letter_obj.x), int(letter_obj.y)), 45, (0, 255, 0), 3)
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
                try:
                    # Make sure coordinates are valid integers
                    x = int(letter_obj.x)
                    y = int(letter_obj.y)
                    # Draw letter circle with consistent color
                    cv2.circle(canvas, (x, y), 40, (180, 0, 180), -1)
                    cv2.putText(canvas, letter_obj.letter, 
                              (x - 12, y + 15), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                except Exception as e:
                    print(f"Error drawing letter: {e} - Coordinates: {letter_obj.x}, {letter_obj.y}")
        
        # Convert canvas to JPEG
        ret, buffer = cv2.imencode('.jpg', canvas)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def root():
    return render_template('signpop_home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

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
    
    print("Game started - active:", game_active, "started:", game_started)
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
    global letters_hit_bottom
    status = {
        'game_active': game_active,
        'game_started': game_started,
        'score': score,
        'lives': lives,
        'letters_count': len(falling_letters),
        'letter_hit_bottom': letters_hit_bottom
    }
    letters_hit_bottom = False  # Reset the flag after sending
    return jsonify(status)

# Add these global variables and routes for the tutorial page
@app.route('/video_feed_tutorial')
def video_feed_tutorial():
    """Provide video feed with hand detection for tutorial page"""
    return Response(generate_tutorial_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detected_letter')
def detected_letter():
    """Return the last detected letter for polling"""
    global last_detected_letter
    return jsonify({"letter": last_detected_letter})

@app.route('/activate_tutorial')
def activate_tutorial():
    """Activate tutorial mode and initialize camera"""
    global tutorial_mode_active, camera
    tutorial_mode_active = True
    
    # Initialize camera if needed
    if camera is None or not camera.isOpened():
        camera = init_camera()
    
    return jsonify({"status": "success"})

@app.route('/deactivate_tutorial')
def deactivate_tutorial():
    """Deactivate tutorial mode when camera is turned off"""
    global tutorial_mode_active
    tutorial_mode_active = False
    return jsonify({"status": "success"})

@app.route('/stop_camera')
def stop_camera():
    """Stop the camera when toggled off"""
    global camera, tutorial_mode_active
    
    # Release camera if it's active
    with lock:
        if camera is not None and camera.isOpened():
            camera.release()
            camera = None
    
    tutorial_mode_active = False
    return jsonify({"status": "success"})

@app.route('/start_camera')
def start_camera():
    """Start the camera when toggled on"""
    global camera, tutorial_mode_active
    
    # Initialize camera if needed
    with lock:
        if camera is None or not camera.isOpened():
            camera = init_camera()
    
    tutorial_mode_active = True
    return jsonify({"status": "success"})

def generate_tutorial_frames():
    """Generate frames with hand detection for tutorial page"""
    global camera, last_detected_letter, tutorial_mode_active
    
    # Ensure camera is initialized
    if camera is None or not camera.isOpened():
        camera = init_camera()
    
    # Parameters for hand detection
    offset = 20
    imageSize = 300
    
    while True:
        # Create a default frame in case camera fails
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = DARK_BLUE
        
        # Only process if camera is available
        if camera is not None and camera.isOpened():
            success, frame = camera.read()
            
            if success:
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process hand detection
                predicted_label, confidence, processed_frame, _ = detector.detect_hand_sign(frame.copy())
                
                # Use the processed frame if available
                if processed_frame is not None:
                    frame = processed_frame
                
                # Update last detected letter if confidence is high enough
                if confidence > 75:
                    last_detected_letter = predicted_label
                    
                    # Add text overlay showing detected letter
                    cv2.putText(frame, f"Detected: {predicted_label} ({confidence:.1f}%)", 
                               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            else:
                # Display message if camera read fails
                cv2.putText(frame, "Camera error", (220, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            # Display message if no camera
            cv2.putText(frame, "No camera available", (180, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                       
        # Convert the frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


if __name__ == '__main__':
    app.run(debug=True)