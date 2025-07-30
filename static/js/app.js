/**
 * Disney Wish Oracle - Main Web Application JavaScript
 * Handles navigation, API calls, and interactive functionality
 */

// Global state
let currentScreen = 'home';
let gameData = window.gameData || {};
let currentGift = null;
let currentCharacter = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Disney Wish Oracle Web App Initialized! ✨');
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Show initial screen
    showHomeScreen();
    
    // Update available gifts display
    updateAvailableGiftsDisplay();
    
    // Debug logging
    console.log('🎮 Disney Wish Oracle Initialized!');
    console.log('📊 Game Data:', gameData);
    console.log('🎁 Available Gifts:', gameData.availableGifts);
    console.log('📈 Available Gifts Count:', gameData.availableGifts ? gameData.availableGifts.length : 'undefined');
    console.log('📋 Summary:', gameData.summary);
    
    // Check gift display
    setTimeout(() => {
        const giftCards = document.querySelectorAll('.gift-card');
        console.log(`🎯 Gift cards in DOM: ${giftCards.length}`);
        console.log('🔍 Gift card IDs:', Array.from(giftCards).map(card => card.dataset.giftId));
        
        if (giftCards.length !== gameData.availableGifts?.length) {
            console.warn('⚠️ MISMATCH: Expected', gameData.availableGifts?.length, 'gifts but found', giftCards.length, 'in DOM');
        }
    }, 1000);
    
    // Start polling for webhook reveals
    startWebhookPolling();
}

function setupEventListeners() {
    // Settings radio buttons
    const gameMode = document.querySelectorAll('input[name="gameMode"]');
    gameMode.forEach(radio => {
        radio.addEventListener('change', function() {
            console.log('Game mode changed to:', this.value);
        });
    });
}

// Screen Navigation Functions
function showScreen(screenId) {
    // Hide all screens
    const screens = document.querySelectorAll('.screen, .welcome-screen');
    screens.forEach(screen => {
        screen.classList.add('hidden');
    });
    
    // Show the requested screen
    const targetScreen = document.getElementById(screenId) || document.querySelector('.welcome-screen');
    if (targetScreen) {
        targetScreen.classList.remove('hidden');
        currentScreen = screenId;
    }
    
    console.log('Showing screen:', screenId);
}

function showHomeScreen() {
    showScreen('home');
    document.querySelector('.welcome-screen').classList.remove('hidden');
    
    // Restart webhook polling when returning to home screen
    // Don't clear processed reveals to prevent re-triggering recently revealed gifts
    if (!webhookPollingInterval) {
        startWebhookPolling();
    }
}

function showWheelScreen() {
    console.log('showWheelScreen called');
    console.log('gameData.availableGifts:', gameData.availableGifts);
    console.log('Length check:', !gameData.availableGifts || gameData.availableGifts.length === 0);
    
    if (!gameData.availableGifts || gameData.availableGifts.length === 0) {
        console.log('No available gifts found, showing notification');
        showNotification('All gifts have been revealed! 🎉', 'success');
        return;
    }
    
    showScreen('wheelScreen');
    initializeWheel();
}

function showProgressScreen() {
    showScreen('progressScreen');
}

function showSettingsScreen() {
    showScreen('settingsScreen');
}

function showRevealScreen() {
    showScreen('revealScreen');
}

// API Functions
async function makeApiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

async function refreshGameState() {
    try {
        showLoading('Refreshing game state...');
        
        const status = await makeApiCall('/api/game_status');
        gameData.summary = status.summary;
        gameData.availableGifts = status.available_gifts;
        
        // Update UI elements
        updateProgressDisplay();
        updateAvailableGiftsDisplay();
        
        hideLoading();
        console.log('Game state refreshed');
    } catch (error) {
        hideLoading();
        showNotification('Failed to refresh game state: ' + error.message, 'error');
    }
}

async function saveSettings() {
    try {
        showLoading('Saving settings...');
        
        const gameMode = document.querySelector('input[name="gameMode"]:checked')?.value;
        
        const settingsData = {
            mode: gameMode
        };
        
        await makeApiCall('/api/save_settings', 'POST', settingsData);
        
        gameData.session.mode = gameMode;
        
        hideLoading();
        showNotification('Settings saved successfully! ✨', 'success');
    } catch (error) {
        hideLoading();
        showNotification('Failed to save settings: ' + error.message, 'error');
    }
}

async function acceptGift() {
    if (!currentGift || !currentCharacter) {
        showNotification('Missing gift or character data!', 'error');
        return;
    }
    
    try {
        showLoading('Accepting magical gift...');
        
        const result = await makeApiCall('/api/accept_gift', 'POST', {
            gift_id: currentGift.id,
            character_name: currentCharacter.name
        });
        
        hideLoading();
        
        if (result.success) {
            // Refresh game state
            await refreshGameState();
            
            // Show celebration
            showCelebration(currentGift.id);
            
            // Clear current gift/character
            currentGift = null;
            currentCharacter = null;
        } else {
            showNotification('Failed to accept gift: ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Failed to accept gift: ' + error.message, 'error');
    }
}

// Reset game functionality
async function confirmReset() {
    if (!confirm('Are you sure you want to reset the entire magical adventure?\n\nThis will clear all progress and start fresh.\nThis action cannot be undone!')) {
        return;
    }
    
    try {
        showLoading('Resetting magical adventure...');
        
        const result = await makeApiCall('/api/reset_game', 'POST');
        
        hideLoading();
        
        if (result.success) {
            showNotification('Magical adventure has been reset successfully! ✨', 'success');
            
            // Refresh page to reset everything
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showNotification('Failed to reset game: ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Failed to reset game: ' + error.message, 'error');
    }
}

// UI Helper Functions
function updateProgressDisplay() {
    if (!gameData.summary) return;
    
    // Update progress cards
    const progressTitle = document.querySelector('.progress-title');
    if (progressTitle) {
        progressTitle.textContent = `✨ Magical Gifts Revealed: ${gameData.summary.revealed_gifts}/30 ✨`;
    }
    
    const progressPercentage = document.querySelector('.progress-percentage');
    if (progressPercentage) {
        progressPercentage.textContent = `🌟 Adventure Progress: ${gameData.summary.completion_percentage.toFixed(1)}% Complete 🌟`;
    }
    
    // Update detailed progress
    const statValues = document.querySelectorAll('.stat-value');
    if (statValues.length >= 3) {
        statValues[0].textContent = gameData.summary.revealed_gifts;
        statValues[1].textContent = gameData.summary.remaining_gifts;
        statValues[2].textContent = `${gameData.summary.completion_percentage.toFixed(1)}%`;
    }
    
    const progressFill = document.querySelector('.progress-fill');
    if (progressFill) {
        progressFill.style.width = `${gameData.summary.completion_percentage}%`;
    }
}

function updateAvailableGiftsDisplay() {
    if (!gameData.availableGifts) return;
    
    const availableCount = document.getElementById('availableCount');
    if (availableCount) {
        availableCount.textContent = gameData.availableGifts.length;
    }
    
    const availableGiftsText = document.getElementById('availableGiftsText');
    if (availableGiftsText && gameData.availableGifts.length > 0) {
        const giftNumbers = gameData.availableGifts.map(gift => gift.id).join(', ');
        availableGiftsText.textContent = `🎁 Gifts on wheel: ${giftNumbers} 🎁`;
    }
}

function showLoading(message = 'Loading magical content...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    
    if (overlay && text) {
        text.textContent = `✨ ${message} ✨`;
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#DC143C' : type === 'success' ? '#32CD32' : '#4169E1'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        z-index: 1001;
        max-width: 400px;
        font-weight: bold;
        white-space: pre-line;
        animation: slideInRight 0.5s ease-out;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove after 15 seconds (tripled from 5 seconds)
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.5s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 15000);
    
    // Add CSS for animations if not already present
    if (!document.getElementById('notificationStyles')) {
        const style = document.createElement('style');
        style.id = 'notificationStyles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

function showCelebration(giftId) {
    const celebrationHtml = `
        <div id="celebrationModal" class="loading-overlay" style="background: rgba(15, 23, 41, 0.95);">
            <div class="loading-content" style="max-width: 600px; padding: 3rem;">
                <h2 style="color: #FFD700; font-size: 2.5rem; margin-bottom: 1rem; font-family: 'Fredoka One', cursive;">
                    🎆 MAGICAL GIFT REVEALED! 🎆
                </h2>
                <p style="color: #FF69B4; font-size: 1.5rem; margin-bottom: 1rem;">
                    🎁 Gift #${giftId} has been added to your collection! 🎁
                </p>
                <p style="color: #87CEEB; font-size: 1.2rem; margin-bottom: 2rem;">
                    ✨ ${gameData.summary.revealed_gifts + 1}/30 gifts revealed! ✨<br>
                    🌟 ${gameData.summary.remaining_gifts - 1} more magical surprises await! 🌟
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button onclick="continueCelebration()" class="main-action-btn" style="min-width: 200px;">
                        🎡 SPIN AGAIN! 🎡
                    </button>
                    <button onclick="closeCelebration()" class="back-btn" style="min-width: 150px;">
                        🏠 Home
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', celebrationHtml);
}

function continueCelebration() {
    closeCelebration();
    showWheelScreen();
}

function closeCelebration() {
    const modal = document.getElementById('celebrationModal');
    if (modal) {
        modal.remove();
    }
    showHomeScreen();
}

// Utility Functions
function formatGiftNumbers(gifts) {
    if (!gifts || gifts.length === 0) return '';
    
    const numbers = gifts.map(gift => gift.id).sort((a, b) => a - b);
    
    if (numbers.length <= 10) {
        return numbers.join(', ');
    }
    
    return numbers.slice(0, 10).join(', ') + `... and ${numbers.length - 10} more!`;
}

// Gift reveal function for the new system
function revealGift(giftId) {
    console.log('🎁 Revealing gift:', giftId);
    
            // Check if this is a special gift using specific gift IDs
        function isSpecialGift(giftId) {
            // Use the exact gift IDs specified by the user
            const specialGiftIds = [28, 24, 19];
            return specialGiftIds.includes(giftId);
        }
        
        if (isSpecialGift(giftId)) {
        console.log('📞 Special gift detected! Triggering phone call...');
        triggerSpecialGiftCall(giftId);
    } else {
        // Navigate to the gift reveal page for regular gifts
        window.location.href = `/gift_reveal?gift=${giftId}`;
    }
}

// Function to trigger special gift calls and show pending state
async function triggerSpecialGiftCall(giftId) {
    try {
        // Trigger VAPI phone call with specific assistant
        const vapiResult = await makeVapiCall(giftId);
        
        if (vapiResult.success) {
            console.log('VAPI call initiated successfully:', vapiResult);
            // Silent success - no popup notification
        } else {
            console.error('VAPI call failed:', vapiResult);
            // Silent failure - no popup notification
        }
        
    } catch (error) {
        console.error('Error triggering VAPI call:', error);
        // Silent error - no popup notification
    }
}

// Function to make VAPI phone call through backend
async function makeVapiCall(giftId) {
    try {
        // Call our backend endpoint which handles VAPI integration
        const result = await makeApiCall('/api/trigger_call', 'POST', {
            gift_id: giftId,
            phone_number: '+1234567890', // This should be configured in settings
            message: `🎂 Happy 30th Birthday Rafa! 🎂 Disney magic is revealing your special gift #${giftId} from Fort Wilderness! ✨`
        });
        
        return {
            success: result.success || false,
            call_id: result.call_id || 'unknown',
            message: result.message || 'Disney character call status unknown'
        };
        
    } catch (error) {
        return {
            success: false,
            message: `Disney character call error: ${error.message}`
        };
    }
}

// Function to reveal special gift after phone call
function revealSpecialGiftAfterCall(giftId) {
    showNotification(`🎉 Phone call complete! 🎉\n\n🎁 Now revealing your special Gift #${giftId}!\n✨ Hope you enjoyed the magical call! ✨`, 'success');
    
    setTimeout(() => {
        window.location.href = `/gift_reveal?gift=${giftId}`;
    }, 2000);
}

// Legacy selectGift function for compatibility
function selectGift(giftId) {
    revealGift(giftId);
}

// Webhook polling functionality
let webhookPollingInterval = null;
let processedReveals = new Set(); // Track processed reveals to avoid duplicates

function startWebhookPolling() {
    console.log('🌐 Starting webhook polling for external reveals...');
    
    // Poll every 2 seconds for webhook-triggered reveals
    webhookPollingInterval = setInterval(checkForWebhookReveals, 2000);
}

function stopWebhookPolling() {
    if (webhookPollingInterval) {
        clearInterval(webhookPollingInterval);
        webhookPollingInterval = null;
        console.log('🌐 Webhook polling stopped');
    }
}

async function checkForWebhookReveals() {
    try {
        const response = await makeApiCall('/api/recent_reveals', 'GET');
        
        if (response.success && response.recent_reveals && response.recent_reveals.length > 0) {
            console.log('🔔 New webhook reveals detected:', response.recent_reveals);
            
            for (const reveal of response.recent_reveals) {
                // Create a unique key for this reveal
                const revealKey = `${reveal.id}-${reveal.revealed_at}`;
                
                // Only process if we haven't seen this reveal before
                if (!processedReveals.has(revealKey)) {
                    // Check if this is an external webhook reveal (not from web_interface)
                    if (reveal.revealed_by !== 'web_interface') {
                        // This is an external webhook reveal - process it immediately
                        processedReveals.add(revealKey);
                        console.log(`🌐 Processing external webhook reveal for gift #${reveal.id} by ${reveal.revealed_by}`);
                        handleWebhookReveal(reveal);
                        break; // Only handle one reveal at a time to avoid multiple redirects
                    } else {
                        // This is a UI reveal - check timing to avoid immediate re-triggering
                        const revealTime = new Date(reveal.revealed_at);
                        const now = new Date();
                        const timeDiff = (now - revealTime) / 1000; // seconds
                        
                        if (timeDiff > 5) {
                            // UI reveal is old enough - unlikely to be from current session
                            processedReveals.add(revealKey);
                            handleWebhookReveal(reveal);
                            break;
                        } else {
                            // Recent UI reveal - mark as processed but don't trigger
                            processedReveals.add(revealKey);
                            console.log(`⏭️ Skipping recent UI reveal for gift #${reveal.id} (${timeDiff.toFixed(1)}s ago)`);
                        }
                    }
                }
            }
        }
    } catch (error) {
        // Silent polling errors to avoid spam
        console.debug('Webhook polling error:', error);
    }
}

function handleWebhookReveal(reveal) {
    console.log(`🎁 Webhook revealed gift #${reveal.id}:`, reveal);
    
    // Stop polling to prevent repeated redirects
    stopWebhookPolling();
    
    // Check if this is a special gift using specific gift IDs
    function isSpecialGiftForWebhook(giftId) {
        // Use the exact gift IDs specified by the user
        const specialGiftIds = [6, 28, 25, 24, 21, 19];
        return specialGiftIds.includes(giftId);
    }
    
    if (isSpecialGiftForWebhook(reveal.id)) {
        console.log(`✨ Special gift #${reveal.id} detected! Showing pixie dust animation...`);
        // Show magical pixie dust animation before revealing the gift for special presents only
        showPixieDustAnimation(() => {
            // Navigate to gift reveal page after animation
            window.location.href = `/gift_reveal?gift=${reveal.id}`;
        });
    } else {
        console.log(`🎁 Regular gift #${reveal.id} - going directly to reveal page`);
        // For regular gifts, go directly to gift reveal page (no pixie dust)
        window.location.href = `/gift_reveal?gift=${reveal.id}`;
    }
}

// Magical pixie dust animation for webhook reveals
function showPixieDustAnimation(callback) {
    console.log('✨ Showing magical pixie dust animation...');
    
    // Create overlay for the animation
    const overlay = document.createElement('div');
    overlay.className = 'pixie-dust-overlay';
    overlay.innerHTML = `
        <div class="magic-container">
            <div class="pixie-dust-particles"></div>
            <div class="magic-wand">🪄</div>
        </div>
    `;
    
    // Add to body
    document.body.appendChild(overlay);
    
    // Create pixie dust particles
    createPixieDustParticles(overlay.querySelector('.pixie-dust-particles'));
    
    // Remove overlay and trigger callback after animation
    setTimeout(() => {
        overlay.remove();
        if (callback) callback();
    }, 10000); // 10 second exciting animation
}

function createPixieDustParticles(container) {
    const particles = ['✨', '⭐', '🌟', '💫', '✨', '⭐', '🌟', '💫', '🎆', '🎇', '💥', '⚡'];
    const colors = ['#FFD700', '#FF69B4', '#87CEEB', '#98FB98', '#DDA0DD', '#FF6347', '#40E0D0', '#FFFF00'];
    
    // Double the particles for even more excitement!
    for (let i = 0; i < 240; i++) {
        const particle = document.createElement('div');
        particle.className = 'pixie-particle';
        particle.textContent = particles[Math.floor(Math.random() * particles.length)];
        particle.style.color = colors[Math.floor(Math.random() * colors.length)];
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 2 + 's'; // Quick start
        particle.style.animationDuration = (1 + Math.random() * 2) + 's'; // Fast 1-3s cycles
        particle.style.animationIterationCount = 'infinite'; // Keep cycling for full 10s
        
        // Smaller size variation for more particles
        const sizeMultiplier = 0.4 + Math.random() * 0.8; // 0.4x to 1.2x size (smaller range)
        particle.style.fontSize = (1.2 * sizeMultiplier) + 'rem'; // Base size smaller (1.2rem instead of 2rem)
        
        container.appendChild(particle);
    }
}

// Expose functions to global scope for HTML onclick handlers
window.showHomeScreen = showHomeScreen;
window.showWheelScreen = showWheelScreen;
window.showProgressScreen = showProgressScreen;
window.showSettingsScreen = showSettingsScreen;
window.showRevealScreen = showRevealScreen;
window.saveSettings = saveSettings;
window.acceptGift = acceptGift;
window.confirmReset = confirmReset;
window.continueCelebration = continueCelebration;
window.closeCelebration = closeCelebration;
window.revealGift = revealGift;
window.selectGift = selectGift;
window.triggerSpecialGiftCall = triggerSpecialGiftCall;
window.revealSpecialGiftAfterCall = revealSpecialGiftAfterCall;

// Expose processedReveals globally for gift reveal page access
window.processedReveals = processedReveals; 