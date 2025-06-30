const SIZE = 8;    // 盤面のサイズ

// 石の状態
const EMPTY = 2;
const BLACK = 0;
const WHITE = 1;

// プレイヤーの色
let player_color_in_chooseColor = null;

// ルーム名を取得します
const roomName = JSON.parse(document.getElementById('room-name').textContent);

// chooseColor関数で使う変数の宣言
let chosenColor = null;

let player_ready = 0;

// websocketのグローバル宣言
let othelloSocket;

// boardを初期化し定義します
let board;
/* 盤面の初期化 */

let player_ava;
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

function updateBoard(state) {
    // ボードのHTML要素を取得
    const boardContainer = document.querySelector('.board');
    boardContainer.innerHTML = ''; // 既存のセルをクリア

    for (let i = 0; i < SIZE; i++) { // 行をループ
        for (let j = 0; j < SIZE; j++) { // 列をループ
            const cell = document.createElement('div'); // 新しいセルを作成
            cell.className = 'cell'; // セルにクラスを追加

            // セルの状態に応じたクラスを追加
            if (state[i][j] === BLACK) {
                cell.classList.add('black'); // 黒のセル
            } else if (state[i][j] === WHITE) {
                cell.classList.add('white'); // 白のセル
            }

            // セルにクリックイベントを追加
            cell.addEventListener('click', () => send_sever_x_and_y(i, j, state));

            // セルをボードに追加
            boardContainer.appendChild(cell);
        }
    }
    console.log("ボードが更新されました:", state);
}

//function createWebSocketConnection(roomName) {
function createWebSocketConnection() {
    othelloSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/othello_index/'
        + roomName
        + '/'
    );
    console.log("WebSocket接続を作成しました: ", othelloSocket);


    othelloSocket.onopen = function() {
        console.log("WebSocket接続が確立しました");
        setupWebSocketListener(othelloSocket); // 接続確立後にリスナーを登録
        initializeBoard();
    };

    othelloSocket.onerror = function(error) {
        console.error("WebSocketエラー:", error);
    };

    othelloSocket.onclose = function() {
        console.log("WebSocket接続が閉じられました");
    };
}

// 他の色のボタンを無効化する関数
function disableOtherButton(selectedColor) {
    if (selectedColor === 'black') {
        document.getElementById('white-btn').disabled = true;  // 白ボタン無効化
        console.log("白ボタンを無効化しました");
    } else if (selectedColor === 'white') {
        document.getElementById('black-btn').disabled = true;  // 黒ボタン無効化
        console.log("黒ボタンを無効化しました");
    }
}

function chooseColor(color) {
    //let color_use_to_disable = ['black', 'white'];
    if (chosenColor === null) {
        chosenColor = color;  // 色を設定
        console.log(chosenColor);
        if (chosenColor === 'black') {
            player_color_in_chooseColor = 0;
        } else {
            player_color_in_chooseColor = 1;
        }
        sendColorChoiceToServer(color);  // サーバーに選択した色を送信
        document.getElementById("color-selection-message").innerText = `あなたは${color === 'black' ? '黒' : '白'}を選びました。`;
        disableOtherButton(color);
    }
    console.log("chooseColor関数は正常に動作する");
}

function sendColorChoiceToServer(color) {
    if (othelloSocket && othelloSocket.readyState === WebSocket.OPEN) {
        othelloSocket.send(JSON.stringify({
            gametype: 'color_choice',
            color: color
        }));
        console.log("色をサーバに送信しました");
    } else {
        console.log("WebSocket is not open.");
    }
    console.log("sendColorChoiceToServer関数は正常に動作する");
}

function debug_for_server_message(othelloSocket) {
    othelloSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("JSON文字列:", JSON.stringify(data, null, 2));
    }
}

function handleColorUpdate(color) {
    if (color === 0) {
        //document.getElementById('black-btn').disabled = true;
        disableOtherButton('black');
    } else {
        //document.getElementById('white-btn').disabled = true;
        disableOtherButton('white');
    }
}

function handleGameUpdate(data) {
    if (data.ready === 0 && data.player_ava === player_color) {

    }
}

function send_sever_x_and_y(x, y, board) {
    if (othelloSocket && othelloSocket.readyState === WebSocket.OPEN) {
        if (player_ava === player_color_in_chooseColor) {
            othelloSocket.send(JSON.stringify({
                gametype: 'gameupdate',
                board: board,
                'data-x': x,
                'data-y': y,
                player_ava: player_color_in_chooseColor,
        }));
    }
    }
}

function setupWebSocketListener(othelloSocket) {
    // サーバからデータを受信
    othelloSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        console.log("setupWebSocketListener関数が動作しています\nReceived data:", data); // ログを追加
        
        switch(data.gametype) {
            case 'updatecolor':
                let color_use_to_disable = ['black', 'white'];
                handleColorUpdate(color_use_to_disable[data.color]);
                if (data.color === 0) {
                    document.getElementById('black-btn').disabled = true;  // 白ボタン無効化
                } else {
                    document.getElementById('white-btn').disabled = true;  // 白ボタン無効化
                }
                if (data.color === player_color_in_chooseColor) {
                    othelloSocket.send(JSON.stringify({
                        gametype: 'ready',
                    }));
                }
                break;
            case 'gameupdate':
                // 盤面を更新する
                board = data.board;
                updateBoard(board);
                // 次に自分が手を出せるか判断する
                player_ava = data.player_ava
                if (player_ava === player_color_in_chooseColor) {
                    document.getElementById('message').innerText = 'あなたのターンです';
                } else {
                    document.getElementById('message').innerText = 'まだあなたのターンじゃないです';
                }
                break;
            case 'ready':
                player_ava = data.player_ava
                if (player_ava === player_color_in_chooseColor) {
                    document.getElementById('message').innerText = 'あなたのターンです';
                }
                break;
            case 'game_inupdate':
                // 最初に自分であるかどうかを判断する
                if (data.player_ava === player_color_in_chooseColor) {
                    // 自分である場合
                    // もし自分ならばアラートし、ちゃんとした手を出してね
                    alert('ここに置くことはできません')
                }
                    // 自分じゃなかったら、無視する
                break;

        }
    }
}

function main() {
    console.log("メイン関数が開始されました");

    // WebSocket接続の作成
    createWebSocketConnection();
    // setupWebSocketListener(othelloSocket);
    debug_for_server_message(othelloSocket);
    console.log("メイン関数は正常に動作しています");
}

// ページ読み込み後にメイン関数を実行
window.onload = main;