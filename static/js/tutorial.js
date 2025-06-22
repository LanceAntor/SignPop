document.addEventListener('DOMContentLoaded', () => {
    const alphabetButtons = document.querySelectorAll('.alphabet-btn');
    const signImage = document.getElementById('signImage');
    const detectedLetter = document.getElementById('detectedLetter');
    const cameraFeed = document.getElementById('cameraFeed');
    const cameraPlaceholder = document.getElementById('cameraPlaceholder');
    const cameraToggle = document.getElementById('cameraToggle');
    let lastDetectedLetter = '';
    let cameraActive = false; // Start with camera inactive
    const clickSound = document.getElementById('clickSound');
    
    // Function to play click sound
    function playClickSound() {
        if (clickSound) {
            clickSound.currentTime = 0;
            clickSound.play().catch(err => console.error("Error playing sound:", err));
        }
    }
    
    // Initialize with camera off
    cameraFeed.style.display = 'none';
    cameraPlaceholder.style.display = 'flex';
    cameraToggle.innerHTML = '<i class="fas fa-video-slash"></i>';
    cameraToggle.classList.add('off');
    detectedLetter.textContent = 'Camera off';
    
    // Deactivate tutorial mode when page loads (camera starts off)
    fetch('/deactivate_tutorial')
        .then(response => response.json())
        .catch(error => console.error('Error deactivating tutorial mode:', error));
    
    fetch('/stop_camera')
        .then(response => response.json())
        .catch(error => console.error('Error stopping camera initially:', error));
    
    // Set the first button (A) as active by default
    alphabetButtons[0].classList.add('active');
    
    // Add click event listeners to all alphabet buttons
    alphabetButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Play click sound
            playClickSound();
            
            // Remove active class from all buttons
            alphabetButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Get the letter from the button's data attribute
            const letter = button.getAttribute('data-letter');
            
            // Check if the file extension is jpg or png based on your file structure
            let fileExtension = 'jpg';
            if (letter === 'F' || letter === 'H' || letter === 'P' || letter === 'Z') {
                fileExtension = 'png';
            }
            
            // Update the image source to show the selected letter's sign
            signImage.src = `/static/ASL_Alphabet/${letter}.${fileExtension}`;
            signImage.alt = `Sign language for letter ${letter}`;
        });
    });
    
    // Camera toggle functionality - completely stop/start camera
    cameraToggle.addEventListener('click', () => {
        // Play click sound
        playClickSound();
        
        cameraActive = !cameraActive;
        
        if (cameraActive) {
            // Turn camera on - make a request to start the camera
            fetch('/start_camera')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Show camera feed with a new timestamp to force reload
                        cameraFeed.src = `/video_feed_tutorial?t=${new Date().getTime()}`;
                        cameraFeed.style.display = 'block';
                        cameraPlaceholder.style.display = 'none';
                        cameraToggle.innerHTML = '<i class="fas fa-video"></i>';
                        cameraToggle.classList.remove('off');
                        
                        // Reactivate tutorial mode
                        fetch('/activate_tutorial')
                            .then(response => response.json())
                            .catch(error => console.error('Error activating tutorial mode:', error));
                        
                        // Reset detection status
                        detectedLetter.textContent = 'Ready to detect';
                    }
                })
                .catch(error => console.error('Error starting camera:', error));
        } else {
            // Turn camera off - make a request to release the camera
            fetch('/stop_camera')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Hide camera feed and show placeholder
                        cameraFeed.style.display = 'none';
                        cameraPlaceholder.style.display = 'flex';
                        cameraToggle.innerHTML = '<i class="fas fa-video-slash"></i>';
                        cameraToggle.classList.add('off');
                        
                        // Stop getting detected letters while camera is off
                        detectedLetter.textContent = 'Camera off';
                        
                        // Deactivate tutorial mode
                        fetch('/deactivate_tutorial')
                            .then(response => response.json())
                            .catch(error => console.error('Error deactivating tutorial mode:', error));
                    }
                })
                .catch(error => console.error('Error stopping camera:', error));
        }
    });
    
    // Function to poll server for detected letter
    function pollDetectedLetter() {
        // Only poll if camera is active
        if (!cameraActive) return;
        
        fetch('/detected_letter')
            .then(response => response.json())
            .then(data => {
                if (data.letter && data.letter !== lastDetectedLetter) {
                    lastDetectedLetter = data.letter;
                    detectedLetter.textContent = `Detected: ${data.letter}`;
                    
                    // Highlight the corresponding button if available
                    const matchingButton = document.querySelector(`.alphabet-btn[data-letter="${data.letter}"]`);
                    if (matchingButton) {
                        alphabetButtons.forEach(btn => btn.classList.remove('active'));
                        matchingButton.classList.add('active');
                        
                        // Update the reference image to match the detected letter
                        let fileExtension = 'jpg';
                        if (data.letter === 'F' || data.letter === 'H' || data.letter === 'P' || data.letter === 'Z') {
                            fileExtension = 'png';
                        }
                        signImage.src = `/static/ASL_Alphabet/${data.letter}.${fileExtension}`;
                        signImage.alt = `Sign language for letter ${data.letter}`;
                    }
                }
            })
            .catch(error => console.error('Error fetching detected letter:', error));
    }
    
    // Poll for detected letter every second
    setInterval(pollDetectedLetter, 1000);
});