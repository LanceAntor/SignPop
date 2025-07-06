import streamlit as st
import cv2
import numpy as np
import random
import time
import threading
from hand_detector import HandSignDetector
import os

# Page configuration
st.set_page_config(
    page_title="SignPop - ASL Game",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'detector' not in st.session_state:
    st.session_state.detector = HandSignDetector('Model/keras_model.h5', 'Model/labels.txt')

if 'score' not in st.session_state:
    st.session_state.score = 0

if 'lives' not in st.session_state:
    st.session_state.lives = 3

if 'game_active' not in st.session_state:
    st.session_state.game_active = False

if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if 'falling_letters' not in st.session_state:
    st.session_state.falling_letters = []

if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = {"label": None, "confidence": 0}

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Define the exact dark blue color to match original design
DARK_BLUE = (51, 0, 13)  # BGR format for OpenCV

class FallingLetter:
    def __init__(self, letter, x, y, base_speed=None):
        self.letter = letter
        self.x = int(x)
        self.y = int(y)
        self.speed = base_speed if base_speed is not None else random.randint(2, 5)
        self.active = True

def create_game_canvas():
    """Create the game canvas with falling letters"""
    # Create canvas with dark blue background
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    canvas[:, :] = DARK_BLUE
    
    # Draw falling letters
    for letter_obj in st.session_state.falling_letters:
        try:
            x = int(letter_obj.x)
            y = int(letter_obj.y)
            # Draw letter circle
            cv2.circle(canvas, (x, y), 40, (180, 0, 180), -1)
            cv2.putText(canvas, letter_obj.letter, 
                      (x - 12, y + 15), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        except Exception as e:
            st.error(f"Error drawing letter: {e}")
    
    # Draw score and lives
    cv2.putText(canvas, f"Score: {st.session_state.score}", 
              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(canvas, f"Lives: {st.session_state.lives}", 
              (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return canvas

def update_game_state():
    """Update the game state - move letters, check collisions"""
    if not st.session_state.game_active:
        return
    
    letters_to_remove = []
    
    for i, letter_obj in enumerate(st.session_state.falling_letters):
        # Update position
        letter_obj.y += letter_obj.speed
        
        # Check if letter hit bottom
        if letter_obj.y > 450:
            letters_to_remove.append(i)
            st.session_state.lives -= 1
            if st.session_state.lives <= 0:
                st.session_state.game_active = False
        
        # Check if letter was detected (placeholder for webcam integration)
        # In a full implementation, this would connect to webcam feed
        if (st.session_state.last_prediction["label"] == letter_obj.letter and 
            st.session_state.last_prediction["confidence"] > 75 and letter_obj.active):
            letters_to_remove.append(i)
            st.session_state.score += 10
            st.session_state.last_prediction = {"label": None, "confidence": 0}
    
    # Remove letters (in reverse order to avoid index issues)
    for i in sorted(letters_to_remove, reverse=True):
        if i < len(st.session_state.falling_letters):
            st.session_state.falling_letters.pop(i)

def add_falling_letter():
    """Add a new falling letter"""
    letter = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", 
                          "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", 
                          "W", "X", "Y", "Z"])
    x_pos = random.randint(80, 550)
    y_pos = 50
    
    # Calculate speed based on score
    speed_multiplier = 1 + (st.session_state.score // 50) * 0.5
    base_speed = random.randint(2, 5) * speed_multiplier
    
    st.session_state.falling_letters.append(FallingLetter(letter, x_pos, y_pos, base_speed))

def start_game():
    """Start the game"""
    st.session_state.game_active = True
    st.session_state.game_started = True
    st.session_state.score = 0
    st.session_state.lives = 3
    st.session_state.falling_letters = []
    st.session_state.last_prediction = {"label": None, "confidence": 0}

def end_game():
    """End the game"""
    st.session_state.game_active = False
    st.session_state.game_started = False
    st.session_state.falling_letters = []

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #4CAF50;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .game-stats {
        text-align: center;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    .game-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
    }
    .sidebar-content {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🎮 SignPop Navigation")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = "Home"
    
    if st.button("🎯 Play Game", use_container_width=True):
        st.session_state.current_page = "Game"
    
    if st.button("📚 Tutorial", use_container_width=True):
        st.session_state.current_page = "Tutorial"
    
    st.markdown("---")
    st.markdown("### 📊 Game Stats")
    st.metric("Score", st.session_state.score)
    st.metric("Lives", st.session_state.lives)
    
    if st.session_state.game_active:
        st.success("🎮 Game Active")
    else:
        st.info("⏸️ Game Stopped")

# Main content area
if st.session_state.current_page == "Home":
    st.markdown('<h1 class="main-header">👋 Welcome to SignPop!</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### 🎯 Game Overview
        SignPop is an interactive ASL (American Sign Language) learning game where you:
        
        - 🤏 Use hand gestures to "pop" falling letters
        - 📚 Learn ASL alphabet signs
        - 🏆 Score points and challenge yourself
        - 💝 Have fun while learning!
        
        ### 🎮 How to Play
        1. Click "Play Game" to start
        2. Position your hand in front of the camera
        3. Make ASL signs to match falling letters
        4. Score points for correct signs!
        
        ### 🚀 Ready to Start?
        Navigate to the **Game** section to begin playing!
        """)
        
        if st.button("🎯 Start Playing Now!", use_container_width=True, type="primary"):
            st.session_state.current_page = "Game"
            st.rerun()

elif st.session_state.current_page == "Tutorial":
    st.markdown('<h1 class="main-header">📚 ASL Tutorial</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Learn the ASL Alphabet
    
    Here are the hand signs for each letter of the alphabet:
    """)
    
    # Display ASL alphabet images
    cols = st.columns(6)
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
              "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    
    for i, letter in enumerate(letters):
        with cols[i % 6]:
            img_path = f"static/ASL_Alphabet/{letter}.jpg"
            if os.path.exists(img_path.replace('.jpg', '.png')):
                img_path = img_path.replace('.jpg', '.png')
            
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Letter {letter}", width=100)
            else:
                st.write(f"**{letter}**")
    
    st.markdown("""
    ### 💡 Tips for Success
    - Ensure good lighting for camera detection
    - Position your hand clearly in front of the camera
    - Practice the signs slowly at first
    - Keep your hand steady when making signs
    """)
    
    if st.button("🎮 Ready to Play?", use_container_width=True, type="primary"):
        st.session_state.current_page = "Game"
        st.rerun()

elif st.session_state.current_page == "Game":
    st.markdown('<h1 class="main-header">🎯 SignPop Game</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎮 Game Area")
        
        # Game controls
        control_col1, control_col2, control_col3 = st.columns(3)
        
        with control_col1:
            if st.button("▶️ Start Game", use_container_width=True, disabled=st.session_state.game_active):
                start_game()
                st.rerun()
        
        with control_col2:
            if st.button("⏸️ Stop Game", use_container_width=True, disabled=not st.session_state.game_active):
                end_game()
                st.rerun()
        
        with control_col3:
            if st.button("🔄 Reset", use_container_width=True):
                end_game()
                st.rerun()
        
        # Game canvas placeholder
        game_placeholder = st.empty()
        
        # Note about camera integration
        st.info("""
        📷 **Camera Integration Note**: 
        This Streamlit version shows the game mechanics. For full camera integration, 
        you would need to use Streamlit's camera input component or deploy with 
        additional webcam handling capabilities.
        """)
        
        # Simulate game if active
        if st.session_state.game_active:
            # Add letters periodically (simulated)
            if len(st.session_state.falling_letters) < 3:
                add_falling_letter()
            
            # Update game state
            update_game_state()
            
            # Display game canvas
            canvas = create_game_canvas()
            game_placeholder.image(canvas, channels="BGR", use_column_width=True)
            
            # Auto-refresh for game animation
            time.sleep(0.1)
            st.rerun()
        else:
            # Show static game area when not active
            canvas = create_game_canvas()
            game_placeholder.image(canvas, channels="BGR", use_column_width=True)
    
    with col2:
        st.markdown("### 📊 Game Status")
        
        st.markdown(f"""
        **Score:** {st.session_state.score}  
        **Lives:** {st.session_state.lives}  
        **Letters:** {len(st.session_state.falling_letters)}  
        **Status:** {'🎮 Playing' if st.session_state.game_active else '⏸️ Stopped'}
        """)
        
        st.markdown("### 🎯 Instructions")
        st.markdown("""
        1. Click **Start Game** to begin
        2. Letters will fall from the top
        3. Make the corresponding ASL sign
        4. Score points for correct signs!
        5. Don't let letters hit the bottom!
        """)
        
        # Manual testing buttons (for demo purposes)
        st.markdown("### 🧪 Demo Controls")
        test_letter = st.selectbox("Test Letter Recognition:", 
                                 ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", 
                                  "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", 
                                  "W", "X", "Y", "Z"])
        
        if st.button("🎯 Simulate Sign Detection", use_container_width=True):
            st.session_state.last_prediction = {"label": test_letter, "confidence": 85}
            st.success(f"Simulated detection of letter '{test_letter}'!")

# Add JavaScript for auto-refresh (if needed)
if st.session_state.game_active:
    # This ensures the game updates in real-time
    st.markdown("""
    <script>
    setTimeout(function(){
        window.location.reload();
    }, 200);
    </script>
    """, unsafe_allow_html=True)
