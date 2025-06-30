// 盤面のサイズ
const SIZE = 8;

// 石の状態
const EMPTY = 2;
const BLACK = 0;
const WHITE = 1;

let othelloSocket;
const roomName = JSON.parse(document.getElementById('room-name').textContent);
let chosenColor = null;

//function createWebSocketConnection(roomName) {
function createWebSocketConnection() {
    othelloSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/othello_index/'
        + roomName
        + '/'
    );
    console.log("createWebSocketConnection関数は正常に動作する");
}

// 他の色のボタンを無効化する関数
function disableOtherButton(selectedColor) {
    if (selectedColor === 'black') {
        document.getElementById('white-btn').disabled = true;  // 白ボタン無効化
    } else if (selectedColor === 'white') {
        document.getElementById('black-btn').disabled = true;  // 黒ボタン無効化
    }
}

function chooseColor(color) {
    if (chosenColor === null) {
        chosenColor = color;  // 色を設定
        console.log(chosenColor);
        if (chosenColor === 'black') {
            const player_color = 0;
        } else {
            const player_color = 1;
        }
        sendColorChoiceToServer(color);  // サーバーに選択した色を送信
        document.getElementById("color-selection-message").innerText = `あなたは${color === 'black' ? '黒' : '白'}を選びました。`;
        disableOtherButton(color);  // 他のボタンを無効化
    }
    console.log("chooseColor関数は正常に動作する");
}

/*
function chooseColor(color) {
    if (chosenColor === null) {
        chosenColor = color;
        sendColorChoiceToServer(color);
        document.getElementById("color-selection-message").innerText = `あなたは${color === 'black' ? '黒' : '白'}を選びました。`;
        disableOtherButton(color);
        let element = document.getElementById("black-btn");
        if (color === 'black') {
            document.getElementById("black-btn").innerHTML = '<button disabled id="black-btn" onclick="chooseColor('black')">黒を選ぶ</button>';
        } else {
            document.getElementById("white-btn").innerHTML = <button disabled id="white-btn"  onclick="chooseColor('white')">白を選ぶ</button>;
        }
    }
    console.log("chooseColor関数は正常に動作する");
}
*/

function sendColorChoiceToServer(color) {
    if (othelloSocket && othelloSocket.readyState === WebSocket.OPEN) {
        othelloSocket.send(JSON.stringify({
            type: 'color_choice',
            color: color
        }));
    } else {
        console.log("WebSocket is not open.");
    }
    console.log("sendColorChoiceToServer関数は正常に動作する");
}

// boardを初期化し定義します
let board;
/* 盤面の初期化 */
function initializeBoard() {
    board = Array.from({ length: SIZE }, () => Array(SIZE).fill(EMPTY));
    const mid = Math.floor(SIZE / 2);
    board[mid - 1][mid - 1] = WHITE;
    board[mid - 1][mid] = BLACK;
    board[mid][mid - 1] = BLACK;
    board[mid][mid] = WHITE;
    console.log(board);
    //console.log(board[3][4]);
    console.log("initialzeBoard関数は正常に動作する");
    return board;
}

function updateBoard(newBoard) {
    board = newBoard;
}

function setupWebSocketListener(othelloSocket) {
    // サーバからデータを受信
    othelloSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'updatecolor') {
            let chosen_color = data.color;
            //相手が黒を選択した場合
            // let element = document.getElementById("black-btn");
            if (chosen_color === 0) {
                document.getElementById('black-btn').disabled = true;  // 黒ボタン無効化
            } else {
                document.getElementById('white-btn').disabled = true;  // 白ボタン無効化
            }
        }
        if (data.ready !== null) {
            if((data.ready === 0) && data.player_ava === player_color){
                othelloSocket.send(JSON.stringify({
                    'type': 'gameuodate',
                    'board': board,
                    'data-x': data-x,
                    
                }))
            }
        }

        // 次のプレイヤーの情報
        player_ava = data.player_ava;
    }

    othelloSocket.onopen = function() {
        // 初期盤面を送信
        const board = initializeBoard();
        if (data.type === '')
        sendGamesState(board, 0); // 初期プレイヤーを0と仮定
    };
    console.log("setupWebSocketListener関数は正常に動作する");
}


function sendGamesState(board) {
    othelloSocket.send(JSON.stringify({
        board: board,
        player_ava: player_ava
    }));
    console.log("sendGamesState関数は正常に動作する");
    return {sendGamesState};
}

function main() {
    console.log("メイン関数が開始されました");

    // WebSocket接続の作成
    createWebSocketConnection();

    // WebSocketリスナーの設定
    setupWebSocketListener(othelloSocket);

    // 初期盤面の設定
    const board = initializeBoard();

    // 初期盤面状態をサーバーに送信
    sendGamesState(board);

    // ボタンのクリックイベントを確認
    document.getElementById('black-btn').addEventListener('click', () => chooseColor('black'));
    document.getElementById('white-btn').addEventListener('click', () => chooseColor('white'));

    console.log("メイン関数は正常に動作しています");
}

// ページ読み込み後にメイン関数を実行
window.onload = main;
