from flask import Flask, render_template, session, redirect, request, url_for
from flask_socketio import SocketIO, emit, join_room
import time
import threading
from collections import deque
from item import Item
import bidder

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# Constants
AUCTION_TIME_LIMIT = 60  # 60 seconds per auction
MAX_USERS = 8
INITIAL_MONEY = 100.0

# Auction Manager class
class AuctionManager:
    def __init__(self):
        self.bidders = {} #dictionary of bidders and information
        self.item_queue = deque() #queue of items to be auctioned
        self.current_item = None #item currently being auctioned
        self.auction_in_progress = False #state of auction room being active
        self.test_populate()

    def test_populate(self):
        start_item = Item('Pikachu', 'System', 1)
        self.item_queue.append(start_item)

    def add_bidder(self, username):
        """Add a bidder to the auction."""
        self.bidders[username] = {'money': 10000, 'items': []} #each bidder has 10000 dollars and no items yet

    def suggest_item(self, username, item_name):
        """Queue an item suggested by a user."""
        new_item = Item(item_name, username, 1)
        self.item_queue.append(new_item)

    def start_next_auction(self):
        """Start the next auction if available and not in progress."""
        if self.item_queue:
            self.auction_in_progress = True
            self.current_item = self.item_queue.popleft()

            # Notify the user that a new auction has started
            socketio.emit('start_auction', {'item': self.current_item}, to=request.sid)

            # Start the auction timer
            threading.Thread(target=self.auction_timer).start()

    def auction_timer(self):
        """Timer for the auction countdown."""
        time_left = 60
        while time_left > 0:
            time.sleep(1)
            time_left -= 1
            socketio.emit('timer_update', {'time_left': time_left}, to=request.sid)

        # End the auction after the timer finishes
        self.end_auction()

    def end_auction(self):
        """End the auction and start the next one."""
        if self.current_item:
            winner = self.current_item['highest_bidder']
            if winner:
                self.bidders[winner]['items'].append(self.current_item)

            # Notify the users about the auction result
            socketio.emit('auction_ended', {
                'item': self.current_item,
                'winner': winner,
                'highest_bid': self.current_item.highest_bid
            }, to=request.sid)

            # Reset for the next auction
            self.start_next_auction()  # Start the next auction automatically

auction_manager = AuctionManager()

@app.route('/')
def index():
    """Index page where users join the auction."""
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join_auction():
    """Handle user joining the auction."""
    username = request.form.get('username')

    if username and len(auction_manager.bidders) < 8:
        if username not in auction_manager.bidders:
            # Add the user to the auction
            auction_manager.add_bidder(username)
            session['username'] = username
            return redirect(url_for('auction_page'))
        else:
            return render_template('index.html', error="Username already taken.")
    return render_template('index.html', error="Auction room full or invalid username.")

@app.route('/auction')
def auction_page():
    """Auction room where users can participate."""
    return render_template('auction.html', item = auction_manager.item_queue.pop())

@socketio.on('suggest_item')
def handle_suggest_item(data):
    """Handle item suggestion."""
    username = session.get('username')
    item_name = data.get('item_name')

    if username and item_name:
        auction_manager.suggest_item(username, item_name)
        auction_manager.start_next_auction()

@socketio.on('place_bid')
def handle_place_bid(data):
    """Handle bid placement."""
    username = session.get('username')
    bid_amount = data.get('bid_amount')

    print(username)
    print(bid_amount)

    if auction_manager.current_item:
        current_item = auction_manager.current_item

        if bid_amount > current_item.highest_bid and auction_manager.bidders[username]['money'] >= bid_amount:
            # Update highest bid and bidder
            current_item.highest_bid = bid_amount
            current_item.highest_bidder = username
            auction_manager.bidders[username]['money'] -= bid_amount

            # Notify users about the new highest bid
            socketio.emit('bid_update', {
                'item': current_item,
                'highest_bid': bid_amount,
                'highest_bidder': username
            }, to=request.sid)
    

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnection."""
    username = session.get('username')
    if username in auction_manager.bidders:
        del auction_manager.bidders[username]
        emit('update_bidders', {'bidders': auction_manager.bidders}, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
