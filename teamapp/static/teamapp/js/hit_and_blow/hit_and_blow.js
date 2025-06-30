document.addEventListener("DOMContentLoaded", function () {
    // WebSocket 接続
    const websocket = new WebSocket('ws://' + window.location.host + '/ws/hit_and_blow_game/');
    let selectedColors = []; // ユーザーが選択した色のリスト
    let userScore = 0; // ユーザーのスコア
    let username = null; // ユーザー名

    // DOM要素の取得
    const titleElement = document.querySelector(".title");
    const colorButtonsContainer = document.getElementById("color-buttons");
    const sendButton = document.getElementById("send-btn");
    const selectedColorsList = document.getElementById("selected-colors-list");
    const chatBox = document.getElementById("chat-box");

    if (!titleElement || !colorButtonsContainer || !sendButton || !selectedColorsList || !chatBox) {
        console.error("必要な要素が見つかりません。HTML構造を確認してください。");
        return;
    }

    // スコア表示エリアの作成
    const scoreDisplay = document.createElement("div");
    scoreDisplay.id = "score-display";
    scoreDisplay.textContent = `現在のポイント: ${userScore}`;
    titleElement.insertAdjacentElement("afterend", scoreDisplay);

    // ユーザーネーム入力エリアの作成
    const usernameContainer = document.createElement("div");
    usernameContainer.id = "username-container";
    usernameContainer.innerHTML = `
        <label for="username-input">ユーザーネーム:</label>
        <input type="text" id="username-input" placeholder="名前を入力してください">
        <button id="set-username-btn">登録</button>
        <button id="edit-username-btn" style="display:none;">編集</button>
    `;
    titleElement.insertAdjacentElement("afterend", usernameContainer);

    const usernameInput = document.getElementById("username-input");
    const setUsernameBtn = document.getElementById("set-username-btn");
    const editUsernameBtn = document.getElementById("edit-username-btn");

    // ユーザーネーム登録処理
    setUsernameBtn.addEventListener("click", () => {
        const newUsername = usernameInput.value.trim();
        if (newUsername) {
            username = newUsername;
            usernameInput.disabled = true;
            setUsernameBtn.style.display = "none";
            editUsernameBtn.style.display = "inline";

            // WebSocket 経由でサーバーにユーザー名を送信
            websocket.send(JSON.stringify({
                action: "set_username",
                username: username
            }));

            alert(`ユーザーネームが "${username}" に設定されました!`);
        } else {
            alert("ユーザーネームを入力してください。");
        }
    });

    // ユーザーネーム編集処理
    editUsernameBtn.addEventListener("click", () => {
        usernameInput.disabled = false;
        setUsernameBtn.style.display = "inline";
        editUsernameBtn.style.display = "none";
    });

    // 色候補の設定
    const colors = ["赤", "青", "黄", "緑", "白", "黒", "茶", "紫", "金", "銀", "銅", "水", "ピンク", "オレンジ", "黄緑"];
    colors.forEach(color => {
        const button = document.createElement("button");
        button.textContent = color;
        button.classList.add("color-button");
        if (color === "黒" || color ==="紫" || color ==="茶") {
            button.classList.add("color-button-black");
        }
        button.style.backgroundColor = getColorCode(color);
        button.addEventListener("click", () => selectColor(color, button));
        colorButtonsContainer.appendChild(button);
    });

    // 色に対応するボタン背景色を設定
    function getColorCode(color) {
        const colorMap = {
            "赤": "#ff4d4d", "青": "#4d4dff", "緑": "#4dff4d", "黄": "#ffff4d",
            "黒": "#333333", "白": "#ffffff", "オレンジ": "#ffa500", "紫": "#800080",
            "ピンク": "#ff69b4", "茶": "#8b4513", "水": "#00ced1", "金": "#ffd700",
            "銀": "#c0c0c0", "黄緑": "#9ACD32", "銅": "#B87333",
        };
        return colorMap[color] || "#dddddd";
    }

    // 色を選択または取り消し
    function selectColor(color, button) {
        const colorIndex = selectedColors.indexOf(color);

        if (colorIndex === -1) { // 未選択の場合
            if (selectedColors.length < 4) {
                selectedColors.push(color);
                updateSelectedColors();

                if (selectedColors.length === 4) {
                    sendButton.disabled = false;
                }
            } else {
                alert('4つの色を選択してください');
            }
        } else { // 既に選択済みの場合
            selectedColors.splice(colorIndex, 1);
            updateSelectedColors();

            if (selectedColors.length < 4) {
                sendButton.disabled = true;
            }
        }
    }

    // 選択した色を更新表示
    function updateSelectedColors() {
        const selectedColorsList = document.getElementById("selected-colors-list");

        if (selectedColors.length === 0) {
            // プレースホルダーに戻す
            selectedColorsList.textContent = "色を選択してください";
            selectedColorsList.classList.remove("filled");
        } else {
            // 選択された色を表示
            selectedColorsList.textContent = selectedColors.join(', ');
            selectedColorsList.classList.add("filled");
        }
    }


    // 送信ボタンの処理
    sendButton.addEventListener('click', () => {
        if (selectedColors.length === 4 && username) {
            console.log('送信するデータ:', selectedColors, username);  // 送信データを確認
            websocket.send(JSON.stringify({
                action: 'submit_colors',
                colors: selectedColors,
                username: username,
            }));

            selectedColors = [];
            updateSelectedColors();  // 色をリセット
            sendButton.disabled = true;
        } else {
            alert("ユーザーネームと色を入力してください。");
        }
    });

    // WebSocketからのメッセージ受信時の処理
    websocket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.action === 'result') {
            displayChatMessage(`${username} さんの推測: ${data.user_guess.join(', ')}`);
            displayChatMessage(`ヒット: ${data.hits}, ブロー: ${data.blows}`);

            if (data.hits === 4) {
                alert("おめでとうございます！4ヒット達成！ポイントが加算されました。");
                userScore = data.score; // サーバーから受信したスコアを更新
                scoreDisplay.textContent = `現在のポイント: ${userScore}`;
                resetChatBox();
            }
        }
    };

    // チャットボックスをリセット
    function resetChatBox() {
        chatBox.innerHTML = '';
    }

    // チャットボックスにメッセージを追加
    function displayChatMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add("result");
        messageDiv.textContent = message;
        chatBox.appendChild(messageDiv);
    }

    // WebSocketエラー処理
    websocket.onerror = function () {
        alert("WebSocketの接続に問題があります。");
    };

    websocket.onclose = function () {
        alert("WebSocketが切断されました。ページをリロードしてください。");
    };

});
