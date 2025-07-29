# 🏰 Disney Wish Oracle 🏰

## Rafa's Magical 30th Birthday Adventure at Fort Wilderness!

A magical, interactive gift-revealing game designed for Rafa's special 30th birthday celebration during your Disney Fort Wilderness trip (July 30 - August 1, 2025). Experience the wonder of Disney as beloved characters guide you through revealing 30 carefully chosen birthday gifts!

**🌐 NEW: Remote Webhook Support!** Now includes a built-in web server for triggering gift reveals remotely via HTTP requests!

## ✨ Features

- **🎭 Disney Character Oracles**: 15+ beloved Disney characters match with gifts based on themes
- **🤖 AI-Powered Messages**: Grok API integration for unique, personalized reveals (with magical fallbacks)
- **🎡 Dynamic Spinning Wheel**: Shows ALL available gifts, removes revealed gifts automatically
- **🖼️ Gift Image Display**: Show actual gift photos during reveals for maximum surprise
- **🌐 Remote Webhook Control**: Trigger gift reveals via HTTP POST requests from anywhere!
- **🎮 Multiple Game Modes**: Random or Sequential reveals
- **💾 Progress Saving**: Continue your adventure across multiple sessions
- **🎨 Beautiful GUI**: Disney-themed interface with animations and progress tracking
- **🎂 Birthday Magic**: Tailored specifically for Rafa's interests and the Fort Wilderness experience

## 🌐 Webhook Server Features

- **🚀 Real-time Integration**: Built-in Flask server runs alongside the main app
- **📡 Remote Triggers**: Reveal gifts from phones, tablets, or other devices
- **🔒 Thread-Safe**: Secure communication between webhook and UI
- **📊 Status API**: Check game progress remotely
- **🎲 Random Reveals**: Trigger random gift selections via API
- **🌍 Network Accessible**: Available on local network for multi-device fun

## 🎯 Game Concept

Enter the magical "Wish Portal" where Disney characters act as oracles, revealing Rafa's birthday gifts one by one. Each reveal is a unique experience with:

- **🎡 Magical Spinning Wheel**: ALL 30 gifts start on the wheel, sections disappear as gifts are revealed
- **🤖 Intelligent Character Matching**: Baymax reveals health items, Tiana unveils food gifts, Mulan presents Japan-themed surprises
- **🎁 Surprise Element**: Gift descriptions are hidden until the big reveal with actual photos
- **🎪 Dynamic Storytelling**: Grok AI generates personalized messages, riddles, and birthday wishes
- **✨ Immersive Experience**: Loading animations, character images, celebration screens, and wheel updates
- **🌐 Remote Control**: Family and friends can trigger surprises from their devices!

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Internet connection (for Grok API, optional - works offline with magical fallback messages)

### Installation

1. **Clone or download** this project to your Disney trip laptop/device

2. **Install dependencies**:
   ```bash
   cd disney_wish_oracle
   pip install -r requirements.txt
   ```

3. **Add Gift Images**:
   - Place gift images in the `assets/images/` folder
   - Name them: `1.png`, `2.png`, `3.png`, ... `30.png` (matching gift IDs)
   - Supported formats: PNG, JPG
   - Recommended size: 300x300 pixels for best display

4. **Set up Grok API** (Optional but recommended):
   - Get your API key from [x.ai/api](https://x.ai/api)
   - Set environment variable:
     ```bash
     # Windows
     set GROK_API_KEY=your_api_key_here
     
     # Mac/Linux
     export GROK_API_KEY=your_api_key_here
     ```

5. **Add Disney Character Images** (Optional):
   - Place character images in the `assets/` folder
   - Names should match: `baymax.png`, `tiana.png`, `mickey.png`, etc.

6. **Run the Game**:
   ```bash
   python main.py
   ```

## 🌐 Webhook API Usage

The app automatically starts a webhook server on `http://localhost:5000` when launched.

### 🎯 Endpoints

#### **POST /reveal_present**
Reveal a specific gift by ID.

```bash
curl -X POST http://localhost:5000/reveal_present \
  -H "Content-Type: application/json" \
  -d '{"present_id": 15}'
```

**Request Body:**
```json
{
  "present_id": 15
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gift 15 reveal request queued",
  "present_id": 15,
  "status": "queued"
}
```

#### **POST /reveal_random**
Reveal a random available gift.

```bash
curl -X POST http://localhost:5000/reveal_random
```

**Response:**
```json
{
  "success": true,
  "message": "Random gift 7 reveal request queued",
  "present_id": 7,
  "status": "queued"
}
```

#### **GET /status**
Check current game status.

```bash
curl http://localhost:5000/status
```

**Response:**
```json
{
  "total_gifts": 30,
  "revealed_gifts": 5,
  "remaining_gifts": 25,
  "completion_percentage": 16.7,
  "is_complete": false,
  "available_gift_ids": [1, 3, 4, 6, 7, ...]
}
```

#### **GET /**
Health check endpoint.

```bash
curl http://localhost:5000/
```

### 🎪 Webhook Use Cases

- **📱 Phone Triggers**: Create buttons on phones to reveal specific gifts
- **🎉 Surprise Timing**: Trigger reveals at perfect moments during the trip
- **👨‍👩‍👧‍👦 Family Participation**: Let everyone contribute to the surprise
- **🕰️ Scheduled Reveals**: Use automation tools to trigger timed reveals
- **🎮 Interactive Games**: Build mini-games that trigger gift reveals as rewards

## 🎮 How to Play

### Starting Your Adventure

1. Launch the game to see the magical welcome screen with webhook server info
2. Check your progress: gifts revealed, completion percentage
3. Click **"🎁 SPIN THE WHEEL OF WISHES! 🎁"** to begin
4. **OR** use webhook endpoints to trigger reveals remotely!

### The Magical Wheel Experience

1. **🎪 The Wheel**: See ALL remaining gifts displayed on a colorful spinning wheel
2. **🌟 Spin**: Click "SPIN THE WHEEL!" and watch it spin with smooth animations
3. **🎯 Selection**: The wheel randomly selects which gift to reveal next
4. **✨ Character Entrance**: A matching Disney character appears with magical flair
5. **💬 Magical Message**: Receive a personalized message (AI-generated or fallback)
6. **🎁 Big Reveal**: See the actual gift image - the moment of surprise!
7. **🎉 Celebration**: Accept the gift and see the wheel update automatically
8. **🔄 Continue**: The revealed gift disappears from the wheel for next time

### Remote Control Experience

1. **🌐 Webhook Notification**: When a remote reveal is triggered, see a notification popup
2. **📡 Source Information**: Know who triggered the reveal and from where
3. **🎭 Seamless Integration**: Remote reveals flow naturally into the game experience
4. **✨ Real-time Updates**: UI updates instantly when webhook requests are received

### Game Modes

- **🎲 Random Magic**: Pure surprise - wheel spins randomly
- **📋 Sequential Order**: Gifts revealed in order 1-30
- **🌐 Remote Control**: Gifts revealed via webhook triggers

## 🎁 The 30 Birthday Gifts

The game includes 30 carefully curated gifts, each with:
- **Unique ID**: 1-30 for easy tracking and webhook targeting
- **Themed Matching**: Each gift matched to appropriate Disney characters
- **Image Support**: Display actual gift photos during reveals
- **Mystery Element**: Descriptions hidden until reveal for maximum surprise
- **Remote Access**: Can be triggered individually via webhook API

## 🏰 Disney Characters

Meet your oracle council of 15+ Disney characters:

- **Baymax** 🤗: Health & comfort items
- **Princess Tiana** 👑: Food & cooking gifts
- **Mulan** ⚔️: Japan-themed & strength items
- **Mickey Mouse** 🐭: Classic Disney & travel gear
- **Jafar** 🐍: Games & villainous fun
- **And many more!** ✨

## 🎡 The Spinning Wheel

### Dynamic Features:
- **All Gifts Visible**: Every unrevealed gift appears on the wheel
- **Smart Sizing**: Wheel adjusts size based on remaining gifts
- **Color Coded**: Each gift gets a unique vibrant color
- **Number Display**: Gift numbers clearly shown in each segment
- **Auto-Update**: Revealed gifts automatically disappear (including webhook reveals)
- **Smooth Animation**: Professional easing and spin effects

### How It Works:
1. Starts with all 30 gifts displayed
2. Each spin randomly selects one segment
3. Revealed gifts are removed from future spins (manual + webhook)
4. Wheel recalculates and redraws automatically
5. Continues until all gifts are revealed

## 🛠️ Technical Details

### File Structure
```
disney_wish_oracle/
├── main.py              # Application entry point with webhook integration
├── game_logic.py        # Core game mechanics (updated for dynamic wheel)
├── api_integration.py   # Grok API wrapper with fallbacks
├── ui_components.py     # GUI with spinning wheel (major update)
├── webhook_server.py    # NEW: Flask webhook server
├── requirements.txt     # Python dependencies (includes Flask)
├── data/
│   ├── gifts.json      # All 30 gifts with image paths
│   ├── characters.json # Disney character data
│   └── progress.json   # Auto-generated save file
├── assets/
│   └── images/         # Gift images (1.png through 30.png)
│   └── (character images)
└── README.md
```

### Architecture

- **Main Thread**: Tkinter GUI and game logic
- **Webhook Thread**: Flask server running in background
- **Thread Communication**: Queue-based messaging for thread safety
- **Real-time Updates**: Tkinter's `after()` method for UI updates
- **Error Handling**: Graceful fallbacks for network issues

### Recent Updates:
- ✅ Removed day-based system for simpler gameplay
- ✅ Added dynamic spinning wheel showing ALL gifts
- ✅ Implemented automatic wheel updates after reveals
- ✅ Added gift image display during reveals
- ✅ Hidden gift descriptions for surprise element
- ✅ Enhanced animations and visual feedback
- ✅ Improved error handling and canvas management
- ✅ **NEW: Flask webhook server for remote control**
- ✅ **NEW: Thread-safe real-time reveal system**
- ✅ **NEW: Multi-device support for collaborative surprises**

## 🔧 Troubleshooting

### Common Issues

**Game won't start:**
- Check Python 3.10+ is installed
- Install requirements: `pip install -r requirements.txt`
- Run from the disney_wish_oracle directory

**Webhook server doesn't start:**
- Check if port 5000 is available
- Look for error messages in console
- Game will still work without webhook support

**Remote reveals not working:**
- Verify webhook server is running (check startup message)
- Test with: `curl http://localhost:5000/`
- Check firewall settings for network access

**No gift images:**
- Add PNG/JPG files to `assets/images/` folder
- Name them `1.png`, `2.png`, etc. (matching gift IDs)
- Missing images show mystery box placeholders

**Wheel doesn't spin:**
- Ensure at least one gift remains unrevealed
- Check for any error messages in the console

**Progress lost:**
- Check `data/progress.json` exists
- Avoid deleting this file during play
- Use "Reset Game" only when intentional

### Network Configuration

**For network access (multiple devices):**
1. Find your computer's IP address
2. Replace `localhost` with your IP in webhook URLs
3. Ensure firewall allows connections on port 5000
4. Test from other device: `curl http://YOUR_IP:5000/`

## 🎂 For Rafa's Birthday

This magical experience is specifically designed for your Fort Wilderness adventure:

- **🎪 Perfect Entertainment**: Engaging spinning wheel keeps excitement high
- **🎁 Surprise Element**: Gift descriptions hidden until reveal moment
- **✨ Personalized Magic**: AI messages tailored to your interests
- **🎮 Replayable Fun**: Dynamic wheel ensures unique experience each time
- **📱 Easy to Use**: Simple interface perfect for relaxing between park visits
- **🎉 Memorable Moments**: Creates lasting digital memories alongside physical gifts
- **🌐 Interactive Surprises**: Family can trigger reveals from anywhere!
- **🕰️ Perfect Timing**: Trigger reveals at just the right moment

## 🎉 Happy 30th Birthday, Rafa!

May this magical oracle bring joy, surprise, and Disney wonder to your special celebration! Each spin of the wheel is a new adventure, every reveal is a wish come true, and now anyone can add to the magic remotely!

✨ *"All our dreams can come true, if we have the courage to pursue them."* - Walt Disney ✨

**Enjoy your magical birthday adventure with webhook-powered surprises!** 🏰🎂✨🌐 