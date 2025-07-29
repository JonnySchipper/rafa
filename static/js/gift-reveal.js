/**
 * Disney Wish Oracle - Gift Reveal JavaScript
 * Handles unique reveal methods for each gift and phone call functionality
 */

// Global state
let currentScreen = 'home';
let gameData = window.gameData || {};
let currentGift = null;
let currentCharacter = null;

// Reveal methods for each gift number
const revealMethods = {
    1: "🎩 Magic Hat Reveal",
    2: "⭐ Shooting Star",
    3: "🧚‍♀️ Fairy Dust Sprinkle",
    4: "🏰 Castle Door Opening",
    6: "🔮 Crystal Ball Vision",
    7: "🪄 Magic Wand Tap",
    8: "🎆 Fireworks Explosion",
    9: "❄️ Snow Globe Shake",
    11: "📚 Enchanted Book",
    12: "🪞 Magic Mirror",
    13: "🧞‍♂️ Genie Lamp Rub",
    14: "🌊 Ocean Wave Reveal",
    16: "🦋 Butterfly Transformation",
    17: "🌙 Moonbeam Shine",
    18: "🎪 Circus Magic",
    19: "🌈 Rainbow Bridge",
    21: "🕯️ Candle Flame Dance",
    22: "🎵 Musical Note Float",
    23: "🌸 Flower Bloom",
    24: "⚡ Lightning Strike",
    26: "🌟 Constellation Form",
    27: "🎭 Theater Curtain",
    28: "🧙‍♂️ Wizard Spell",
    29: "🎨 Paint Brush Magic"
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Disney Wish Oracle Gift Reveal Initialized! ✨');
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Show initial screen
    showHomeScreen();
    
    // Update gift reveal methods in the UI
    updateGiftRevealMethods();
    
    // Debug logging
    console.log('Game Data:', gameData);
    console.log('Available Gifts:', gameData.availableGifts);
    console.log('Available Gifts Length:', gameData.availableGifts ? gameData.availableGifts.length : 'undefined');
    console.log('Summary:', gameData.summary);
}

function setupEventListeners() {
    // No specific event listeners needed for now
    console.log('Event listeners set up');
}

function updateGiftRevealMethods() {
    // Update the reveal method text for each gift card
    const magicRevealSpans = document.querySelectorAll('.magic-reveal[data-gift-id]');
    magicRevealSpans.forEach(span => {
        const giftId = parseInt(span.getAttribute('data-gift-id'));
        const revealMethod = revealMethods[giftId] || '✨ Magical Reveal';
        span.textContent = revealMethod;
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
}

function showProgressScreen() {
    showScreen('progressScreen');
    updateProgressDisplay();
}

function showSettingsScreen() {
    showScreen('settingsScreen');
}

function showVapiScreen() {
    showScreen('vapiScreen');
}

function showRevealScreen() {
    showScreen('revealScreen');
}

function showPhoneCallScreen(giftId) {
    showScreen('phoneCallScreen');
    document.getElementById('phoneGiftNumber').textContent = giftId;
    
    // Trigger the actual phone call via VAPI
    triggerPhoneCall(giftId);
}

// Gift Selection and Reveal Functions
async function selectGift(giftId) {
    console.log('Gift selected:', giftId);
    
    // Find the gift data
    const gift = gameData.availableGifts.find(g => g.id === giftId);
    if (!gift) {
        showNotification('Gift not found!', 'error');
        return;
    }
    
    // Check if this is a phone call gift (every 5th)
    if (giftId % 5 === 0) {
        // Show phone call screen
        showPhoneCallScreen(giftId);
        return;
    }
    
    // For regular gifts, proceed with magical reveal
    await handleGiftReveal(gift);
}

async function handleGiftReveal(gift) {
    try {
        showLoading('Creating magical reveal...');
        
        // Call API to get character and generate message
        const result = await makeApiCall('/api/spin_wheel', 'POST', {
            gift_id: gift.id
        });
        
        hideLoading();
        
        if (result.success) {
            // Set current gift and character
            window.currentGift = result.gift;
            window.currentCharacter = result.character;
            
            // Create unique reveal animation
            await createRevealAnimation(gift.id);
            
            // Update reveal screen
            updateRevealScreen(result);
            
            // Show reveal screen after animation
            setTimeout(() => {
                showRevealScreen();
            }, 2000);
        } else {
            showNotification('Failed to process gift selection: ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Error processing gift selection: ' + error.message, 'error');
    }
}

// Unique Reveal Animations
async function createRevealAnimation(giftId) {
    const animationArea = document.getElementById('revealAnimationArea');
    if (!animationArea) return;
    
    // Clear previous animations
    animationArea.innerHTML = '';
    
    // Create animation based on gift type
    const animation = createAnimationForGift(giftId);
    animationArea.appendChild(animation);
    
    // Show the reveal screen briefly to see animation
    showRevealScreen();
    
    // Let animation play
    return new Promise(resolve => {
        setTimeout(resolve, 9000);
    });
}

function createAnimationForGift(giftId) {
    const container = document.createElement('div');
    container.className = 'gift-animation-container';
    container.style.cssText = `
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    `;
    
    const revealMethod = revealMethods[giftId];
    
    switch(giftId) {
        case 1: // Magic Hat
            return createMagicHatAnimation(container);
        case 2: // Shooting Star
            return createShootingStarAnimation(container);
        case 3: // Fairy Dust
            return createFairyDustAnimation(container);
        case 4: // Castle Door
            return createCastleDoorAnimation(container);
        case 6: // Crystal Ball
            return createCrystalBallAnimation(container);
        case 7: // Magic Wand
            return createMagicWandAnimation(container);
        case 8: // Fireworks
            return createFireworksAnimation(container);
        case 9: // Snow Globe
            return createSnowGlobeAnimation(container);
        // Add more cases for other gifts...
        default:
            return createDefaultMagicAnimation(container, revealMethod);
    }
}

function createMagicHatAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 4rem; animation: hatReveal 9s ease-in-out;">
            🎩✨🐰
        </div>
        <style>
            @keyframes hatReveal {
                0% { transform: scale(0) rotate(0deg); opacity: 0; }
                50% { transform: scale(1.2) rotate(180deg); opacity: 1; }
                100% { transform: scale(1) rotate(360deg); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createShootingStarAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 3rem; animation: shootingStar 9s ease-in-out;">
            ⭐💫🌟
        </div>
        <style>
            @keyframes shootingStar {
                0% { transform: translateX(-200px) translateY(-100px) scale(0); opacity: 0; }
                50% { transform: translateX(0) translateY(0) scale(1.5); opacity: 1; }
                100% { transform: translateX(200px) translateY(100px) scale(1); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createFairyDustAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 3rem; animation: fairyDust 9s ease-in-out;">
            🧚‍♀️✨💫
        </div>
        <style>
            @keyframes fairyDust {
                0% { transform: scale(0) rotate(0deg); opacity: 0; }
                50% { transform: scale(1.3) rotate(180deg); opacity: 1; }
                100% { transform: scale(1) rotate(360deg); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createCastleDoorAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 4rem; animation: castleDoor 9s ease-in-out;">
            🏰🚪✨
        </div>
        <style>
            @keyframes castleDoor {
                0% { transform: scaleX(0); opacity: 0; }
                50% { transform: scaleX(1.1); opacity: 1; }
                100% { transform: scaleX(1); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createCrystalBallAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 4rem; animation: crystalBall 9s ease-in-out;">
            🔮✨🌟
        </div>
        <style>
            @keyframes crystalBall {
                0% { transform: scale(0); opacity: 0; filter: blur(10px); }
                50% { transform: scale(1.2); opacity: 1; filter: blur(0px); }
                100% { transform: scale(1); opacity: 1; filter: blur(0px); }
            }
        </style>
    `;
    return container;
}

function createMagicWandAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 3rem; animation: magicWand 9s ease-in-out;">
            🪄✨🌟
        </div>
        <style>
            @keyframes magicWand {
                0% { transform: rotate(0deg) scale(0); opacity: 0; }
                50% { transform: rotate(180deg) scale(1.3); opacity: 1; }
                100% { transform: rotate(360deg) scale(1); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createFireworksAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 3rem; animation: fireworks 9s ease-in-out;">
            🎆🎇✨
        </div>
        <style>
            @keyframes fireworks {
                0% { transform: scale(0); opacity: 0; }
                25% { transform: scale(0.8); opacity: 0.8; }
                50% { transform: scale(1.5); opacity: 1; }
                75% { transform: scale(1.2); opacity: 0.9; }
                100% { transform: scale(1); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createSnowGlobeAnimation(container) {
    container.innerHTML = `
        <div style="font-size: 4rem; animation: snowGlobe 9s ease-in-out;">
            ❄️🌨️✨
        </div>
        <style>
            @keyframes snowGlobe {
                0% { transform: rotate(0deg) scale(0); opacity: 0; }
                50% { transform: rotate(180deg) scale(1.2); opacity: 1; }
                100% { transform: rotate(360deg) scale(1); opacity: 1; }
            }
        </style>
    `;
    return container;
}

function createDefaultMagicAnimation(container, revealMethod) {
    const emoji = revealMethod.split(' ')[0] || '✨';
    container.innerHTML = `
        <div style="font-size: 4rem; animation: defaultMagic 9s ease-in-out;">
            ${emoji}✨🌟
        </div>
        <style>
            @keyframes defaultMagic {
                0% { transform: scale(0) rotate(0deg); opacity: 0; }
                50% { transform: scale(1.5) rotate(180deg); opacity: 1; }
                100% { transform: scale(1) rotate(360deg); opacity: 1; }
            }
        </style>
    `;
    return container;
}

// Phone Call Functions
async function triggerPhoneCall(giftId) {
    try {
        console.log('Triggering phone call for gift', giftId);
        
        // Use the existing VAPI endpoint to trigger the call
        const result = await makeApiCall('/api/trigger_call', 'POST', {
            gift_id: giftId,
            message: `Special phone reveal for Gift #${giftId}! This is one of the magical phone call gifts for Rafa's 30th birthday!`
        });
        
        if (result.success) {
            showNotification(`📞 Phone call initiated for Gift #${giftId}! 📞`, 'success');
            
            // Show success status
            const phoneStatus = document.getElementById('phoneStatus');
            if (phoneStatus) {
                phoneStatus.innerHTML = `
                    <div style="color: #32CD32; text-align: center;">
                        <h3>✅ Call Initiated Successfully! ✅</h3>
                        <p>The magical phone call for Gift #${giftId} has been started!</p>
                        <p>🎭 A Disney character will call soon to reveal your special gift!</p>
                        <p><small>Call ID: ${result.call_id || 'N/A'}</small></p>
                    </div>
                `;
            }
        } else {
            showNotification(`❌ Phone call failed: ${result.message}`, 'error');
            
            const phoneStatus = document.getElementById('phoneStatus');
            if (phoneStatus) {
                phoneStatus.innerHTML = `
                    <div style="color: #DC143C; text-align: center;">
                        <h3>❌ Call Failed ❌</h3>
                        <p>Unable to initiate phone call for Gift #${giftId}</p>
                        <p>Error: ${result.error || 'Unknown error'}</p>
                        <button onclick="showHomeScreen()" class="back-btn" style="margin-top: 1rem;">
                            🏠 Return to Gifts
                        </button>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Phone call error:', error);
        showNotification('Failed to trigger phone call: ' + error.message, 'error');
    }
}

// Update the reveal screen with gift and character data
function updateRevealScreen(data) {
    // Update character name
    const characterName = document.getElementById('characterName');
    if (characterName) {
        characterName.textContent = `🌟 ${data.character.name} 🌟`;
    }
    
    // Update character image
    const characterImage = document.getElementById('characterImage');
    if (characterImage) {
        if (data.character.image_url) {
            characterImage.innerHTML = `<img src="${data.character.image_url}" alt="${data.character.name}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 15px;">`;
        } else {
            characterImage.innerHTML = `<div class="character-placeholder">✨ ${data.character.name} ✨</div>`;
        }
    }
    
    // Update character message
    const characterSpeaker = document.getElementById('characterSpeaker');
    if (characterSpeaker) {
        characterSpeaker.textContent = `💬 ${data.character.name} says:`;
    }
    
    const characterMessage = document.getElementById('characterMessage');
    if (characterMessage) {
        characterMessage.textContent = data.message || 'A magical message awaits you!';
    }
    
    // Update gift info
    const giftTitle = document.getElementById('giftTitle');
    if (giftTitle) {
        giftTitle.textContent = `🎁 GIFT #${data.gift.id} 🎁`;
    }
    
    // Update gift image
    const giftImage = document.getElementById('giftImage');
    if (giftImage) {
        if (data.gift.image_url) {
            giftImage.innerHTML = `<img src="${data.gift.image_url}" alt="Gift #${data.gift.id}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 15px;">`;
        } else {
            giftImage.innerHTML = `<div class="gift-placeholder">🎁 SURPRISE GIFT #${data.gift.id} 🎁</div>`;
        }
    }
}

// API Functions (using same pattern as existing app.js)
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
        
        hideLoading();
        console.log('Game state refreshed');
    } catch (error) {
        hideLoading();
        showNotification('Failed to refresh game state: ' + error.message, 'error');
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

async function triggerCall() {
    try {
        showLoading('Initiating magical birthday call...');
        
        const result = await makeApiCall('/api/trigger_call', 'POST');
        
        hideLoading();
        
        if (result.success) {
            showNotification(`🎉 ${result.message} 🎉\n\nCall ID: ${result.call_id || 'N/A'}`, 'success');
        } else {
            showNotification(`❌ Call failed: ${result.message}\n\nError: ${result.error || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        hideLoading();
        showNotification('Failed to trigger call: ' + error.message, 'error');
    }
}

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
                    <button onclick="closeCelebration()" class="main-action-btn" style="min-width: 200px;">
                        🎁 Choose Next Gift! 🎁
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

function closeCelebration() {
    const modal = document.getElementById('celebrationModal');
    if (modal) {
        modal.remove();
    }
    showHomeScreen();
}

// Expose functions to global scope for HTML onclick handlers
window.showHomeScreen = showHomeScreen;
window.showProgressScreen = showProgressScreen;
window.showSettingsScreen = showSettingsScreen;
window.showVapiScreen = showVapiScreen;
window.showRevealScreen = showRevealScreen;
window.selectGift = selectGift;
window.acceptGift = acceptGift;
window.triggerCall = triggerCall;
window.confirmReset = confirmReset;
window.closeCelebration = closeCelebration; 