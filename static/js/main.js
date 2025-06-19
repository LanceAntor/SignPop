$(document).ready(function() {
    console.log("Document ready, initializing game...");
    
    // Immediately force hearts to be yellow on page load
    $('.heart').css('color', '#FFD700');
    
    // Modal handling
    const modal = document.getElementById('gameOverModal');
    const closeButton = document.querySelector('.close-button');
    
    // Close modal on X click
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Game variables
    let gameRunning = false;
    let statusCheckInterval;

    // Start game when clicking the play button
    $('#start-button').click(function() {
        startGame();
    });

    // Stop game when clicking the stop button
    $('#end-button').click(function() {
        endGame();
    });

    // Start game function
    function startGame() {
        // Call the start_game endpoint
        $.ajax({
            url: '/start_game',
            success: function(response) {
                if (response.status === 'success') {
                    // Update UI
                    $('#start-button').prop('disabled', true);
                    $('#end-button').prop('disabled', false);
                    gameRunning = true;
                    
                    // Start checking game status
                    statusCheckInterval = setInterval(checkGameStatus, 1000);
                }
            }
        });
    }

    // End game function
    function endGame() {
        // Call the end_game endpoint
        $.ajax({
            url: '/end_game',
            success: function(response) {
                if (response.status === 'success') {
                    // Update UI
                    $('#start-button').prop('disabled', false);
                    $('#end-button').prop('disabled', true);
                    gameRunning = false;
                    
                    // Stop checking game status
                    clearInterval(statusCheckInterval);
                    
                    // Reset hearts to 3 with yellow color
                    updateHearts(3);
                }
            }
        });
    }

    // Function to update hearts with explicit yellow color
    function updateHearts(count) {
        $('.lives').empty();
        for (let i = 0; i < count; i++) {
            $('.lives').append('<div class="heart"><i class="fas fa-heart"></i></div>');
        }
    }

    // Check game status
    function checkGameStatus() {
        if (!gameRunning) return;
        
        $.ajax({
            url: '/get_status',
            success: function(status) {
                // Update score
                $('#score-display').text(status.score);
                
                // Update hearts with our custom function that forces yellow
                updateHearts(status.lives);
                
                // Check if game ended
                if (!status.game_active && gameRunning) {
                    endGame();
                }
            }
        });
    }
    
    // Initialize with yellow hearts
    updateHearts(3);
});