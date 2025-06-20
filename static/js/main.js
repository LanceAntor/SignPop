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
        endGame(true); // true indicates manual stop
    });

    // Play Again button in modal
    $('#playAgainBtn').click(function() {
        $('#gameOverModal').hide();
        startGame();
    });

    // Close modal button
    $('.close-modal').click(function() {
        $('#gameOverModal').hide();
    });

    // Also close modal if user clicks outside of it
    $(window).click(function(event) {
        if ($(event.target).is('#gameOverModal')) {
            $('#gameOverModal').hide();
        }
    });

    // Start game function
    function startGame() {
        // Call the start_game endpoint
        $.ajax({
            url: '/start_game',
            success: function(response) {
                if (response.status === 'success') {
                    // Update UI - disable play button, enable stop button
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
    function endGame(isManual = false) {
        // Call the end_game endpoint
        $.ajax({
            url: '/end_game',
            success: function(response) {
                if (response.status === 'success') {
                    // Update UI - enable play button, disable stop button
                    $('#start-button').prop('disabled', false);
                    $('#end-button').prop('disabled', true);
                    gameRunning = false;
                    
                    // Stop checking game status
                    clearInterval(statusCheckInterval);
                    
                    // Show game over modal if game ended by losing (not manual stop)
                    if (!isManual) {
                        // Update final score in modal
                        $('#finalScore').text(response.score);
                        
                        // Show modal
                        $('#gameOverModal').show();
                    }
                }
            }
        });
    }

    // Check game status
    function checkGameStatus() {
        if (!gameRunning) return;
        
        $.ajax({
            url: '/get_status',
            success: function(status) {
                // Update score
                $('#score-display').text(status.score);
                
                // Update hearts
                updateHearts(status.lives);
                
                // Check if game ended automatically (e.g., player lost all lives)
                if (!status.game_active && gameRunning) {
                    endGame(false); // false indicates automatic game end (loss)
                }
            }
        });
    }

    // Function to update hearts
    function updateHearts(count) {
        $('.lives').empty();
        for (let i = 0; i < count; i++) {
            $('.lives').append('<div class="heart"><i class="fas fa-heart" style="color: #FFD700;"></i></div>');
        }
    }
    
    // Initialize with yellow hearts
    updateHearts(3);
});