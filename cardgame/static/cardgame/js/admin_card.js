document.addEventListener('DOMContentLoaded', function() {
    // 効果を追加する関数
    function addEffect() {
        const container = document.getElementById("effects-container");
        const effectHTML = `
            <div class="effect-group">
                <label for="effect_type">効果タイプ:</label>
                <select name="effect_type">
                    <option value="damage">ダメージ</option>
                    <option value="heal">回復</option>
                    <option value="modify_value">値変更</option>
                </select>
                <label for="target_type">ターゲットタイプ:</label>
                <select name="target_type">
                    <option value="1">対戦相手</option>
                    <option value="2">自分</option>
                    <option value="3">すべて</option>
                </select>
                <label for="var">効果量:</label>
                <input type="number" name="var" required>
                <button type="button" onclick="removeEffect(this)">削除</button>
            </div>
        `;
        container.insertAdjacentHTML("beforeend", effectHTML);
    }
    
    // グローバルスコープに公開
    window.addEffect = addEffect;

    // 効果を削除する関数
    function removeEffect(button) {
        const effectGroup = button.closest('.effect-group');
        effectGroup.remove();
    }

    // グローバルスコープに公開
    window.removeEffect = removeEffect;

    // 「効果を追加」ボタンにイベントリスナーを追加
    const addButton = document.getElementById('add-effect-button');
    if (addButton) {
        addButton.addEventListener('click', addEffect);
    }
});
