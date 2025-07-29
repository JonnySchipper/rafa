/**
 * Disney Wish Oracle - Intro Screen JavaScript
 * Handles the magical intro experience with video playback
 */

// Global state
let videoLoaded = false;
let introVideo = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Disney Wish Oracle Intro Initialized! ✨');
    initializeIntro();
});

function initializeIntro() {
    // Get video element
    introVideo = document.getElementById('introVideo');
    
    if (introVideo) {
        // Set up video event listeners
        introVideo.addEventListener('loadeddata', onVideoLoaded);
        introVideo.addEventListener('canplaythrough', onVideoReady);
        introVideo.addEventListener('ended', onVideoEnded);
        introVideo.addEventListener('error', onVideoError);
        
        // Start preloading the video
        console.log('Preloading intro video...');
        introVideo.load();
    }
    
    // Add keyboard event listener for Escape key to skip video
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            skipVideo();
        }
    });
    
    console.log('Intro initialization complete');
}

function onVideoLoaded() {
    console.log('Video metadata loaded');
    videoLoaded = true;
    hideVideoLoading();
}

function onVideoReady() {
    console.log('Video ready to play');
    videoLoaded = true;
    hideVideoLoading();
}

function onVideoError(event) {
    console.error('Video loading error:', event);
    // If video fails to load, skip directly to the main app
    setTimeout(() => {
        showNotification('Video could not be loaded. Proceeding to main app...', 'info');
        proceedToMainApp();
    }, 2000);
}

function onVideoEnded() {
    console.log('Video playback ended');
    // Automatically proceed to main app when video ends
    proceedToMainApp();
}

function startIntroVideo() {
    console.log('Starting intro video...');
    
    // Hide the start screen
    const startScreen = document.getElementById('introStartScreen');
    const videoContainer = document.getElementById('videoContainer');
    
    if (startScreen && videoContainer) {
        startScreen.style.display = 'none';
        videoContainer.classList.remove('hidden');
        
        // Show loading if video not ready
        if (!videoLoaded) {
            showVideoLoading();
        }
        
        // Play the video
        if (introVideo) {
            introVideo.play().then(() => {
                console.log('Video playback started successfully');
                hideVideoLoading();
            }).catch((error) => {
                console.error('Error playing video:', error);
                // Show error and proceed to main app
                showNotification('Video playback failed. Proceeding to main app...', 'warning');
                setTimeout(proceedToMainApp, 2000);
            });
        }
    }
}

function skipVideo() {
    console.log('Skipping intro video...');
    
    // Stop video playback
    if (introVideo) {
        introVideo.pause();
        introVideo.currentTime = 0;
    }
    
    // Proceed to main app
    proceedToMainApp();
}

function showVideoLoading() {
    const loadingElement = document.querySelector('.video-loading');
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
}

function hideVideoLoading() {
    const loadingElement = document.querySelector('.video-loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

function proceedToMainApp() {
    console.log('Proceeding to main app...');
    
    // Show transition overlay
    const transitionOverlay = document.getElementById('transitionOverlay');
    if (transitionOverlay) {
        transitionOverlay.classList.remove('hidden');
    }
    
    // Hide video container
    const videoContainer = document.getElementById('videoContainer');
    if (videoContainer) {
        videoContainer.classList.add('hidden');
    }
    
    // Wait a moment for the transition, then redirect to main app
    setTimeout(() => {
        window.location.href = '/main';
    }, 3000);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'error' ? '#DC143C' : type === 'warning' ? '#FF8C00' : '#4169E1'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        z-index: 4000;
        font-weight: bold;
        animation: slideInDown 0.5s ease-out;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove after 9 seconds (tripled from 3 seconds)
    setTimeout(() => {
        notification.style.animation = 'slideOutUp 0.5s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 9000);
    
    // Add CSS for animations if not already present
    if (!document.getElementById('notificationStyles')) {
        const style = document.createElement('style');
        style.id = 'notificationStyles';
        style.textContent = `
            @keyframes slideInDown {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
            @keyframes slideOutUp {
                from { transform: translateX(-50%) translateY(0); opacity: 1; }
                to { transform: translateX(-50%) translateY(-100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Debug functions (can be called from browser console)
window.debugIntro = {
    skipToMain: proceedToMainApp,
    playVideo: startIntroVideo,
    skipVideo: skipVideo,
    videoLoaded: () => videoLoaded,
    videoElement: () => introVideo
};

console.log('Disney Wish Oracle Intro JS loaded! Use window.debugIntro for debugging.'); 