from flask import Flask, render_template, session, redirect, request, url_for
from flask_socketio import SocketIO, emit, join_room
import time
import threading
from collections import deque

AUCTION_TIME_LIMIT = 60  # 60 seconds per auction
MAX_USERS = 8
INITIAL_MONEY = 100.0

class AuctionManager:
    def __init__(self):
        self.bidders = {}
        self.item_queue = deque()
        self.current_item = None
        self.auction_in_progress = False

    def add_bidder(self, username):
        """Add a bidder to the auction."""
        self.bidders[username] = {'money': INITIAL_MONEY, 'items': []}

    def suggest_item(self, username, item_name):
        """Queue an item suggested by a user."""
        self.item_queue.append({
            'name': item_name,
            'suggested_by': username,
            'highest_bid': 0,
            'highest_bidder': None
        })

    def start_next_auction(self):
        """Start the next auction if available and not in progress."""
        if not self.auction_in_progress and self.item_queue:
            self.auction_in_progress = True
            self.current_item = self.item_queue.popleft()

            # Notify users that a new auction has started
            socketio.emit('start_auction', {'item': self.current_item}, broadcast=True)

            # Start the auction timer
            threading.Thread(target=self.auction_timer).start()

    def auction_timer(self):
        """Timer for the auction countdown."""
        time_left = AUCTION_TIME_LIMIT
        while time_left > 0:
            time.sleep(1)
            time_left -= 1
            socketio.emit('timer_update', {'time_left': time_left}, broadcast=True)

        # End the auction after the timer finishes
        self.end_auction()

    def end_auction(self):
        """End the auction and start the next one."""
        if self.current_item:
            winner = self.current_item['highest_bidder']
            if winner:
                self.bidders[winner]['items'].append(self.current_item)

            # Notify users about the auction result
            socketio.emit('auction_ended', {
                'item': self.current_item,
                'winner': winner,
                'highest_bid': self.current_item['highest_bid']
            }, broadcast=True)

            # Reset for the next auction
            self.current_item = None
            self.auction_in_progress = False
            self.start_next_auction()  # Start the next auction automatically

auction_manager = AuctionManager()