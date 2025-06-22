// Define soundEnabled variable
let soundEnabled = true;

function playClickSound() {
    try {
        const clickSound = document.getElementById('clickSound');
        if (clickSound) {
            clickSound.currentTime = 0; // Reset sound to beginning
            clickSound.play().catch(err => console.error("Error playing sound:", err));
        } else {
            console.error("Click sound element not found");
        }
    } catch (error) {
        console.error("Error in playClickSound:", error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('start-btn');
    const tutorialButton = document.getElementById('tutorial-btn');

    if (startButton) {
        // Prevent default link behavior to allow sound to play before navigation
        startButton.addEventListener('click', function(event) {
            event.preventDefault();
            playClickSound();
            // Use setTimeout to allow sound to play before navigating
            setTimeout(function() {
                window.location.href = '/index';
            }, 300);
        });
    } else {
        console.error("Start button not found");
    }

    if (tutorialButton) {
        // Prevent default link behavior to allow sound to play before navigation
        tutorialButton.addEventListener('click', function(event) {
            event.preventDefault();
            playClickSound();
            // Use setTimeout to allow sound to play before navigating
            setTimeout(function() {
                window.location.href = '/tutorial';
            }, 300);
        });
    } else {
        console.error("Tutorial button not found");
    }
});