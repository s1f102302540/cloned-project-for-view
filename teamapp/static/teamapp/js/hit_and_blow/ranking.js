// teamapp/js/hit_and_blow/ranking.js

document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = document.getElementById('refresh-ranking');
    const rankingList = document.getElementById('ranking-list');

    // ボタンのクリックイベント
    refreshButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/hit_and_blow/ranking/api/'); // APIエンドポイントを設定
            if (!response.ok) throw new Error('データ取得に失敗しました');

            const data = await response.json();
            rankingList.innerHTML = ''; // ランキングリストをリセット
            data.top_players.forEach((player, index) => {
                const listItem = document.createElement('li');
                listItem.textContent =
                    index === 0 ? ` ${player.username} さん - ポイント: ${player.points}` : `${player.username} さん - ポイント: ${player.points}`;
                rankingList.appendChild(listItem);
            });
        } catch (error) {
            console.error('ランキング更新エラー:', error);
        }
    });
});
