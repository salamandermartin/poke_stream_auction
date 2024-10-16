from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import obs_websocket_manager as obsm

app = Flask(__name__)
socketio = SocketIO(app)

obs_manager = obsm.OBS_Manager()
obs_manager.set_defaults(True)

# In-memory store for auction data
auction_data = {
    "current_item": None,
    "bids": [],
    "suggested_items": [],
    "users": {},
}


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('User connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('User disconnected')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    auction_data['users'][username] = 30000  # Example: Each user starts with $1000

    if username not in obs_manager.auctioner_id:
        obs_manager.auctioner_pokemon[username] = []
        obs_manager.auctioner_id[username] = obs_manager.auctioner_assigner
        obs_manager.set_auctioner_name(username)
        obs_manager.auctioner_assigner += 1

    emit('user_joined', {'msg': f"{username} has joined the room."}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('user_left', {'msg': f"{username} has left the room."}, room=room)

@socketio.on('bid')
def on_bid(data):
    username = data['username']
    amount = data['amount']
    current_item = auction_data['current_item']

    previous_info = auction_data['bids'][-1]
    
    if auction_data['users'][username] >= amount and amount > previous_info['amount'] or len(obs_manager.auctioner_pokemon[username]) >= 6:
        auction_data['bids'].append({'username': username, 'amount': amount})
        # auction_data['users'][username] -= amount

        obs_manager.set_bidding_info(amount, username, previous_info['amount'], previous_info['username'], False)

        emit('new_bid', {'username': username, 'amount': amount}, broadcast=True)
    else:
        emit('error', {'msg': 'Insufficient funds or bid is not higher than the previous'}, room=request.sid)
        print('error')

@socketio.on('end_item')
def end_item():
    final_amount = auction_data['bids'][-1]['amount']
    final_username = auction_data['bids'][-1]['username']

    auction_data['users'][final_username] -= final_amount

    obs_manager.set_auctioner_money(auction_data['users'][final_username], final_username)
    obs_manager.auctioner_pokemon[final_username].append(auction_data['current_item'])

    party_index = len(obs_manager.auctioner_pokemon[final_username])
    auctioner_index = obs_manager.auctioner_id[final_username]
    obs_manager.set_party_pokemon(obs_manager.curr_img, auctioner_index, party_index)
    obs_manager.empty_fields()

@socketio.on('suggest_item')
def suggest_item(data):
    item = data['item']
    username = data['username']
    auction_data['suggested_items'].append(item)
    auction_data['bids'].append({'username': username, 'amount': 1})
    auction_data['current_item'] = item

    obs_manager.set_current_pokemon_auction_info(item.lower())
    obs_manager.set_bidding_info(1, username, 0, '', True)

    emit('new_item_suggested', {'item': item, 'username': username}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
