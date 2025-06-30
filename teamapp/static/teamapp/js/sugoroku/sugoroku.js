const roomName = JSON.parse(document.getElementById('room-name').textContent);
const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/sugoroku/' + roomName + '/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.action === 'move') {
        updateGameState(data.payload);
    }
};

socket.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};

function sendMove(moveData) {
    socket.send(JSON.stringify({
        action: 'move',
        payload: moveData
    }));
}

function updateGameState(state) {
    // ゲームの状態を更新するロジック
}
