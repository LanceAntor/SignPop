$(document).ready(function() {
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
        $.get('/start_game', function(data) {
            if (data.status === 'success') {
                $('#start-button').prop('disabled', true);
                $('#end-button').prop('disabled', false);
            }
        });
    });
    
    // End game button
    $('#end-button').click(function() {
        $.get('/end_game', function(data) {
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
        $.get('/start_game', function(data) {
            if (data.status === 'success') {
                $('#start-button').prop('disabled', true);
                $('#end-button').prop('disabled', false);
            }
        });
    });
});