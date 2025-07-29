# Disney Wish Oracle - Web Version 🌐

The Disney Wish Oracle has been converted from a desktop Tkinter application to a web-based application that can be served via NGrok for remote access!

## 🎯 Features

- **Magical Intro Experience**: Beautiful start screen with full-screen intro video
- **Unique Gift Reveals**: Each of the 30 gifts has its own magical reveal animation
- **Manual Gift Selection**: Choose exactly which gift to reveal next (no random wheel!)
- **Phone Call Reveals**: Every 5th gift (5, 10, 15, 20, 25, 30) revealed via magical phone calls
- **Web-based UI**: Beautiful, responsive web interface with Disney theming
- **Remote Access**: Perfect for NGrok deployment and remote gift reveals
- **Webhook Support**: Phone call reveals can be triggered remotely via API
- **Mobile Friendly**: Responsive design works on all devices
- **Real-time Updates**: Dynamic interface updates without page refreshes

## 🎬 Intro Experience

When you first visit the site, you'll see:
1. **Welcome Screen**: Magical start screen with animated background
2. **Start Button**: Click "BEGIN THE MAGIC!" to start the intro video
3. **Full-Screen Video**: The intro.mp4 video plays in full screen
4. **Skip Option**: Press Escape or click "Skip Introduction" to skip
5. **Auto-Transition**: After the video ends, automatically goes to the main app

## 🎁 Gift Reveal System

### Manual Selection
- **Gift Grid**: Beautiful grid showing all 30 available gifts
- **Choose Order**: You decide which gift to reveal next (no randomness!)
- **Unique Methods**: Each gift has its own special reveal animation:
  - 🎩 Magic Hat Reveal
  - ⭐ Shooting Star
  - 🧚‍♀️ Fairy Dust Sprinkle
  - 🏰 Castle Door Opening
  - 🔮 Crystal Ball Vision
  - 🪄 Magic Wand Tap
  - 🎆 Fireworks Explosion
  - ❄️ Snow Globe Shake
  - And 22 more unique animations!

### Phone Call Reveals
- **Special Gifts**: Gifts #5, #10, #15, #20, #25, #30 are revealed via phone calls
- **VAPI Integration**: Real AI-powered Disney character calls
- **Remote Triggering**: Phone calls can be triggered via webhook endpoint
- **Automatic Reveal**: After the call, the gift is automatically revealed

## 🚀 Quick Start

### 1. Run the Web Server

Use the new web server entry point:

```bash
python main_web.py
```

Or run with custom host/port:

```bash
HOST=127.0.0.1 PORT=5000 python main_web.py
```

### 2. Access the Web Interface

Open your browser and navigate to:
- **Local**: http://localhost:8080
- **Network**: http://your-ip-address:8080

### 3. Use with NGrok

To make it accessible from anywhere:

```bash
# Install ngrok first: https://ngrok.com/download
ngrok http 8080
```

NGrok will provide a public URL like `https://abc123.ngrok.io` that you can access from anywhere!

## 🎮 How to Use

1. **Start Screen**: Click "BEGIN THE MAGIC!" to watch the intro video
2. **Intro Video**: Watch the magical introduction (or skip with Escape key)
3. **Gift Selection**: Choose any available gift from the beautiful grid
4. **Unique Reveals**: Watch each gift's special reveal animation
5. **Character Message**: Disney character delivers personalized message
6. **Accept Gift**: Accept the revealed gift to add it to your collection
7. **Phone Calls**: For gifts 5, 10, 15, 20, 25, 30 - wait for magical phone call!
8. **Track Progress**: View detailed progress and statistics
9. **Repeat**: Continue selecting gifts in any order you prefer

## 🌐 API Endpoints

### Web Interface
- `GET /` - Magical intro screen
- `GET /main` - Main web interface (after intro)
- `GET /health` - Health check

### Game API (for web UI)
- `GET /api/game_status` - Get current game state
- `POST /api/spin_wheel` - Handle individual gift selection (legacy name)
- `POST /api/accept_gift` - Accept a revealed gift
- `POST /api/trigger_call` - Trigger VAPI call for phone reveals
- `POST /api/reset_game` - Reset the entire game

### Asset Serving
- `GET /static/assets/<filename>` - Serve video files and other assets
- `GET /static/images/<filename>` - Serve gift and character images

### Webhook API (for phone calls)
- `GET /status` - Game status (JSON)
- `POST /reveal_present` - **PHONE CALL ENDPOINT** - Reveal gift after call
- `POST /reveal_random` - Reveal random gift

## 📱 Phone Call System

### How Phone Calls Work
1. **User Selection**: User clicks on gift #5, #10, #15, #20, #25, or #30
2. **Call Triggered**: System automatically initiates VAPI call
3. **Disney Magic**: AI Disney character calls and reveals the gift
4. **Auto-Reveal**: After call ends, gift is automatically revealed in the web interface

### Remote Phone Triggers
Perfect for surprise reveals during the Disney trip:

```bash
# Trigger phone call for gift #15
curl -X POST https://your-ngrok-url.ngrok.io/reveal_present \
  -H "Content-Type: application/json" \
  -d '{"present_id": 15}'
```

### VAPI Integration
- **Custom Messages**: Each phone call includes gift-specific context
- **Disney Characters**: AI-powered character voices
- **Birthday Context**: Calls mention Rafa's 30th birthday celebration
- **Fort Wilderness Theme**: References to the Disney location

## 📁 File Structure

```
disney_wish_oracle/
├── main_web.py              # New web server entry point
├── webhook_server.py        # Updated Flask server with web UI
├── templates/               # HTML templates
│   ├── base.html           # Base template for main app
│   ├── index.html          # Main interface with gift grid
│   └── intro.html          # New intro screen template
├── static/                 # Static assets
│   ├── css/
│   │   ├── style.css       # Disney-themed styles + gift grid
│   │   └── intro.css       # New intro screen styles
│   └── js/
│       ├── app.js          # Legacy app functions
│       ├── gift-reveal.js  # NEW: Gift selection & unique reveals
│       └── intro.js        # New intro video functionality
├── assets/                 # Media files
│   ├── intro.mp4           # Intro video file
│   └── images/             # Gift and character images
├── game_logic.py           # Game logic (enhanced)
├── api_integration.py      # AI integration (unchanged)
├── data/                   # Game data
└── main.py                 # Original Tkinter version (still available)
```

## 🎬 Video Requirements

For the intro video (`intro.mp4`):
- **Format**: MP4 (H.264 codec recommended)
- **Location**: Place in `assets/intro.mp4`
- **Size**: Any reasonable size (will be scaled to full screen)
- **Duration**: Any duration (skip button provided)
- **Fallback**: If video fails to load, automatically proceeds to main app

## 🔧 Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8080)

### Gift System Settings

- **Manual Selection**: No random selection - user chooses order
- **Phone Call Gifts**: Every 5th gift (5, 10, 15, 20, 25, 30) automatically
- **Unique Reveals**: 24 different reveal animations for regular gifts
- **VAPI Integration**: Automatic phone call triggering for special gifts

## 🎂 Perfect for Rafa's Birthday!

This new system is ideal for:
- **Controlled Experience**: Choose gift reveal order for perfect timing
- **Cinematic Feel**: Unique animations make each reveal special
- **Phone Surprises**: Every 5th gift creates surprise phone call moments
- **Remote Control**: Family can trigger phone calls remotely via webhooks
- **Photo/Video Perfect**: Each reveal is unique and photo-worthy
- **Group Participation**: Everyone can suggest which gift to open next
- **Professional Presentation**: Intro video + unique reveals = magical experience

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**: Change the port with `PORT=5000 python main_web.py`
2. **Missing templates**: Ensure all files in `templates/` and `static/` exist
3. **Video not playing**: Check that `assets/intro.mp4` exists and is a valid MP4 file
4. **Gift animations not working**: Check browser console for JavaScript errors
5. **Phone calls failing**: Verify VAPI configuration in `api_integration.py`
6. **API errors**: Check console logs for detailed error messages

### Phone Call Troubleshooting

- **Calls not triggering**: Check VAPI API credentials and configuration
- **Wrong gift revealed**: Ensure webhook sends correct `present_id`
- **Call fails**: Check logs for VAPI API errors
- **No character voice**: Verify VAPI voice configuration

### Gift System Troubleshooting

- **Gifts not showing**: Check that game data loads correctly
- **Animations broken**: Verify CSS and JavaScript files load properly
- **Wrong reveal type**: Check gift ID calculation (every 5th = phone call)
- **UI not updating**: Clear browser cache and refresh

### Logs

The server provides detailed logs including:
- Startup information
- Gift selection tracking
- Phone call triggers
- Animation loading
- Error messages
- Game state changes
- Video serving status

## 🎨 Customization

### Gift Reveal Animations
Edit `static/js/gift-reveal.js` to customize:
- Add new animation types
- Modify existing animations
- Change timing and effects
- Add sound effects (if desired)

### Phone Call System
Edit `api_integration.py` to customize:
- VAPI voice settings
- Call message templates
- Character selection logic
- Call timing

### Visual Styling
The interface can be customized by editing:
- `static/css/style.css` - Gift grid and main app styling
- `templates/index.html` - Gift grid HTML structure
- `static/css/intro.css` - Intro visual styling
- `static/js/gift-reveal.js` - Reveal behavior and animations

## 🔄 Migration from Wheel Version

### What Changed
- ❌ **REMOVED**: Spinning wheel interface
- ❌ **REMOVED**: Random gift selection
- ✅ **NEW**: Manual gift selection grid
- ✅ **NEW**: 24 unique reveal animations
- ✅ **NEW**: Dedicated phone call system for every 5th gift
- ✅ **NEW**: Enhanced webhook support for phone reveals

### What Stayed the Same
- ✅ Game logic and data format unchanged
- ✅ Progress files compatible
- ✅ Webhook endpoints preserved (enhanced)
- ✅ AI integration intact
- ✅ All 30 gifts and Disney characters available
- ✅ VAPI phone call integration

## 📞 Phone Call Reveals

The system automatically handles phone calls for gifts 5, 10, 15, 20, 25, and 30:

### For Users:
1. Click on a phone call gift (shows 📞 icon)
2. System displays "waiting for call" screen
3. VAPI automatically triggers the call
4. Enjoy the magical Disney character phone call
5. Gift automatically appears after the call

### For Remote Triggers:
```bash
# Trigger gift #10 phone call remotely
curl -X POST https://your-ngrok-url.ngrok.io/reveal_present \
  -H "Content-Type: application/json" \
  -d '{"present_id": 10}'
```

Perfect for family members to surprise Rafa during the Disney trip!

---

**Happy 30th Birthday, Rafa! 🎂✨**

*Choose your own magical adventure at Fort Wilderness!* 