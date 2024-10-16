let socket = io();
let username = null;
let currentItem = null;
let highestBid = 0;

window.onload = () => {
    // Ask for the user's name
    username = prompt("Enter your name:");
    socket.emit('join', { username: username, room: 'auction-room' });

    document.getElementById('name').textContent = `${username}`
    // Update the UI when a user joins the room
    socket.on('user_joined', (data) => {
        // No alerts, updating the UI dynamically
        console.log(`${data.msg}`);
    });

    // Update the UI with the new bid
    socket.on('new_bid', (data) => {
        if (data.amount > highestBid) {
            highestBid = data.amount;
            document.getElementById('bid-info').textContent = `Highest bid: ${data.amount} by ${data.username}`;
        }
        
        let bidsDiv = document.getElementById('bids');
        bidsDiv.innerHTML += `<p>${data.username} bid ${data.amount}</p>`;
    });

    // Display the newly suggested item
    socket.on('new_item_suggested', (data) => {
        currentItem = data.item;
        highestBid = 0;  // Reset highest bid for new item
        document.getElementById('current-item').textContent = `Current item: ${data.item}`;
        document.getElementById('suggest-info').textContent = `Suggested by: ${data.username}`;
        document.getElementById('bid-info').textContent = `Highest bid: N/A`;
    });
};

// Function to place a bid
function placeBid() {
    let bidAmount = document.getElementById('bid-amount').value;

    // Ensure bid amount is valid and username exists
    if (bidAmount && username) {
        socket.emit('bid', { username: username, amount: parseInt(bidAmount) });
        document.getElementById('bid-amount').value = '';  // Clear the input
    } else {
        console.log("Invalid bid or username");
    }
}

// Function to suggest a new item
function suggestItem() {
    let item = document.getElementById('suggest-item').value;
    if (item && username) {
        socket.emit('suggest_item', { item: item, username: username });
        document.getElementById('suggest-item').value = '';  // Clear the input
    } else {
        console.log("Invalid item suggestion");
    }
}

function endItem(){
    if (username){
        socket.emit('end_item')
    }
    document.getElementById('bids').innerHTML = '';
}