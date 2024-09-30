const socket = io();

// Listen for new auctions
socket.on('start_auction', (data) => {
    document.getElementById('current-item').innerText = `Item: ${data.item.name}`;
    document.getElementById('highest-bid').innerText = `Highest Bid: $${data.item.highest_bid}`;
});

// Listen for bid updates
socket.on('bid_update', (data) => {
    console.log(data)

    document.getElementById('highest-bid').innerText = `Highest Bid: $${data.highest_bid} (by ${data.highest_bidder})`;
    document.getElementById('current-leader').innerText = `Current Leader: $${data.highest_bidder}`;
});

// Listen for auction timer updates
socket.on('timer_update', (data) => {
    document.getElementById('timer').innerText = `Time Left: ${data.time_left}s`;
});

// Listen for auction ended
socket.on('auction_ended', (data) => {
    alert(`Auction ended! Winner: ${data.winner || 'None'} with a bid of $${data.highest_bid}`);
});

// Place a bid
function placeBid() {

    //takes money amount from field
    const bidAmount = parseFloat(document.getElementById('bid-amount').value);

    //connects to python socket place_bid
    socket.emit('place_bid', { bid_amount: bidAmount });
}
