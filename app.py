from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import ssl
import eventlet
import eventlet.wsgi
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Store player positions
players = {}

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")

@socketio.on('update_position')
def update_position(data):
    """Receives position updates from a client and broadcasts them to others."""
    player_id = data['id']
    logger.info(f"Position update from {player_id}")
    
    players[player_id] = {
        'position': data['position'],
        'rotation': data['rotation'],
        'sid': request.sid
    }
    
    # Log current player count
    logger.info(f"Current players: {len(players)}")
    
    # Broadcast to all other clients
    emit('players_update', players, broadcast=True, include_self=False)

@socketio.on('disconnect')
def remove_player():
    """Remove player when they disconnect."""
    logger.info(f"Client disconnected: {request.sid}")
    
    for player_id in list(players.keys()):
        if players[player_id].get('sid') == request.sid:
            del players[player_id]
            logger.info(f"Removed player: {player_id}")
            break
    
    # Broadcast updated players list
    emit('players_update', players, broadcast=True)

if __name__ == '__main__':
    # Create SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    # Monkey patch for socketio
    eventlet.monkey_patch()
    
    logger.info("Starting server on port 8000 with SSL...")
    
    # Wrap socket with SSL
    sock = eventlet.listen(('0.0.0.0', 8000))
    ssl_sock = eventlet.wrap_ssl(sock, certfile='cert.pem', keyfile='key.pem', server_side=True)
    
    # Run server
    eventlet.wsgi.server(ssl_sock, app)