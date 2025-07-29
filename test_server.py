#!/usr/bin/env python3
"""
Simple test server for the Disney Wish Oracle web interface
"""

from flask import Flask, render_template, jsonify
import time
import os

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Sample data for testing
sample_gifts = [
    {'id': 1, 'description': 'Magical Disney Pin', 'themes': ['collectible'], 'revealed': False},
    {'id': 2, 'description': 'Mickey Ears Hat', 'themes': ['clothing'], 'revealed': False},
    {'id': 3, 'description': 'Disney Plushie', 'themes': ['toy'], 'revealed': False},
    {'id': 4, 'description': 'Disney Movie', 'themes': ['entertainment'], 'revealed': False},
    {'id': 5, 'description': 'Disney Snack', 'themes': ['food'], 'revealed': False},
]

sample_session = {
    'mode': 'test',
    'total_revealed': 0
}

@app.route('/')
def intro():
    cache_bust = str(int(time.time()))
    return render_template('intro.html', cache_bust=cache_bust)

@app.route('/main')
def main():
    # Create summary data that the template expects
    summary = {
        'revealed_gifts': 0,
        'remaining_gifts': len(sample_gifts),
        'total_gifts': len(sample_gifts),
        'completion_percentage': 0,
        'is_complete': False
    }
    
    cache_bust = str(int(time.time()))
    return render_template('index.html',
                         summary=summary,
                         available_gifts=sample_gifts,
                         revealed_gifts=[],
                         total_gifts=len(sample_gifts),
                         session_data=sample_session,
                         cache_bust=cache_bust)

@app.route('/gift_reveal')
def gift_reveal():
    cache_bust = str(int(time.time()))
    return render_template('gift_reveal.html', cache_bust=cache_bust)

@app.route('/api/test')
def api_test():
    return jsonify({'status': 'Test server running', 'gifts': len(sample_gifts)})

if __name__ == '__main__':
    print("🎪 Starting Disney Wish Oracle Test Server...")
    print("🌐 Server will be available at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 