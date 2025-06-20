document.addEventListener('DOMContentLoaded', () => {
    const alphabetButtons = document.querySelectorAll('.alphabet-btn');
    const signImage = document.getElementById('signImage');
    const webcam = document.getElementById('webcam');
    const cameraIcon = document.querySelector('.camera-icon');
    
    // Set the first button (A) as active by default
    alphabetButtons[0].classList.add('active');
    
    // Add click event listeners to all alphabet buttons
    alphabetButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            alphabetButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Get the letter from the button's data attribute
            const letter = button.getAttribute('data-letter');
            
            // Check if the file extension is jpg or png based on your file structure
            let fileExtension = 'jpg';
            if (letter === 'D' || letter === 'F' || letter === 'H' || letter === 'P' || letter === 'Z') {
                fileExtension = 'png';
            }
            
            // Update the image source to show the selected letter's sign
            // Use the full URL path with static in it for Flask to find the images
            signImage.src = `/static/ASL_Alphabet/${letter}.${fileExtension}`;
            signImage.alt = `Sign language for letter ${letter}`;
        });
    });
    
    // Initialize webcam
    async function setupWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: true,
                audio: false
            });
            webcam.srcObject = stream;
            
            // Show webcam when it's active
            webcam.style.display = 'block';
            
            // Hide camera icon when webcam is active
            webcam.onloadedmetadata = () => {
                cameraIcon.style.display = 'none';
            };
        } catch (error) {
            console.error('Error accessing the webcam:', error);
            // Keep camera icon visible if there's an error
        }
    }
    
    // Start webcam
    setupWebcam();
});