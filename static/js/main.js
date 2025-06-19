$(document).ready(function() {
    console.log("Document ready, initializing game...");
    
    // Modal handling
    const modal = document.getElementById('gameOverModal');
    const closeButton = document.querySelector('.close-button');
    
    // Close modal on X click
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Game state polling
    function updateGameState() {
        $.get('/get_status', function(data) {
            console.log("Game status:", data);
            
            // Update score display
            $('#score-display').text(data.score);
            
            // Update hearts
            const heartsContainer = $('.hearts');
            heartsContainer.empty();
            
            for (let i = 0; i < data.lives; i++) {
                heartsContainer.append('<span class="heart">♥</span>');
            }
            
            // Check game state
            if (data.game_started && !data.game_active && data.lives <= 0) {
                // Game over state
                $('#start-button').prop('disabled', false);
                $('#end-button').prop('disabled', true);
                
                // Show game over modal
                $('#final-score').text(data.score);
                modal.style.display = 'flex';
            }
        });
    }
    
    // Poll game state every second
    setInterval(updateGameState, 1000);

    // Start game button
    $('#start-button').click(function() {
        console.log("Start button clicked");
        
        // Disable button during loading
        $('#start-button').prop('disabled', true);
        
        $.get('/start_game', function(data) {
            console.log("Start game response:", data);
            if (data.status === 'success') {
                $('#start-button').prop('disabled', true);
                $('#end-button').prop('disabled', false);
            } else {
                // Re-enable button if there was an error
                $('#start-button').prop('disabled', false);
                alert("Failed to start game: " + (data.message || "Unknown error"));
            }
        }).fail(function() {
            $('#start-button').prop('disabled', false);
            alert("Server error while starting game");
        });
    });
    
    // End game button
    $('#end-button').click(function() {
        console.log("End button clicked");
        
        $.get('/end_game', function(data) {
            console.log("End game response:", data);
            if (data.status === 'success') {
                $('#start-button').prop('disabled', false);
                $('#end-button').prop('disabled', true);
                
                // Show game over modal
                $('#final-score').text(data.score);
                modal.style.display = 'flex';
            }
        });
    });
    
    // Play again button
    $('#play-again-btn').click(function() {
        modal.style.display = 'none';
        
        // Disable button during loading
        $(this).prop('disabled', true);
        
        $.get('/start_game', function(data) {
            if (data.status === 'success') {
                $('#start-button').prop('disabled', true);
                $('#end-button').prop('disabled', false);
            } else {
                $('#start-button').prop('disabled', false);
                alert("Failed to restart game: " + (data.message || "Unknown error"));
            }
            
            // Re-enable button
            $('#play-again-btn').prop('disabled', false);
        }).fail(function() {
            $('#play-again-btn').prop('disabled', false);
            $('#start-button').prop('disabled', false);
            alert("Server error while restarting game");
        });
    });
    
    // Initialize
    console.log("Game initialization complete");
});