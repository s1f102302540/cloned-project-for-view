import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from .models import Hit_and_blow_PlayerScore
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync


class HitAndBlowConsumer(AsyncWebsocketConsumer):
    ready = 0
    async def connect(self):
        print(f"WebSocketに接続！: {self.scope['client']}")
        self.room_name = "hit_and_blow"
        self.room_group_name = f"hit_and_blow_game_{self.room_name}"

        # グループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # ランダムな正解の色を生成
        self.correct_colors = random.sample(
            ["赤", "青", "緑", "黄", "黒", "白", "オレンジ", "紫", "ピンク", "茶", "水", "金", "銀", "銅", "黄緑"],
            4
        )
        print(f"正解の色: {self.correct_colors}")

        # スコアを初期化
        self.scores = {}  # {"user_id": points}

    async def disconnect(self, close_code):
        # グループから退出
        print(f"WebSocketの接続解除！: {self.scope['client']}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("サーバーが受け取ったメッセージ:", text_data)  # 受け取ったメッセージを確認
        data = json.loads(text_data)
        action = data.get("action")

        # ユーザーIDまたはユーザーネームを取得
        username = data.get("username")  # クライアントから送信されたユーザーネーム


        if action == "submit_colors":
            user_guess = data["colors"]
            print(f"{username}の推測: {user_guess}")

            # ヒット＆ブロー計算
            hits = sum(1 for i, color in enumerate(user_guess) if i < len(self.correct_colors) and color == self.correct_colors[i])
            blows = sum(1 for color in user_guess if color in self.correct_colors) - hits

            if hits == 4:
                # ユーザーデータを更新または作成
                player, created = await sync_to_async(Hit_and_blow_PlayerScore.objects.get_or_create)(username=username)
                player.points += 1
                await sync_to_async(player.save)()

                # 新しい問題を生成
                self.correct_colors = random.sample(
                    ["赤", "青", "緑", "黄", "黒", "白", "オレンジ", "紫", "ピンク", "茶", "水", "金", "銀", "銅", "黄緑"],
                    4
                )
                print(f"新しい正解の色: {self.correct_colors}")

            # 結果をクライアントに送信
            response = {
                'action': 'result',
                'user_guess': user_guess,
                'hits': hits,
                'blows': blows,
                'score': player.points if hits == 4 else None,
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': json.dumps(response),
                }
            )

        elif action == "get_ranking":
            # ランキングを取得
            top_scores = await sync_to_async(list)(
                Hit_and_blow_PlayerScore.objects.all().order_by('-points')[:3]
            )
            ranking = [{"username": p.username, "score": p.points} for p in top_scores]

            await self.send(text_data=json.dumps({
                'action': 'ranking',
                'ranking': ranking
            }))

    async def chat_message(self, event):
        # グループメッセージをクライアントに送信
        message = event['message']
        await self.send(text_data=message)

class OthelloConsumer(WebsocketConsumer):
    player_ava = 0
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print('self.room_name:', self.room_name)
        self.room_group_name = "othello_%s" % self.room_name
        # グループに参加
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

        # プレイヤーの色の状態を初期化
        # self.color = None

    def disconnect(self, close_code):
        # グループから離脱
            async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def is_valid_move(self, board, x, y, player_ava):
        # 石が置けるかどうかの判定を行う
        SIZE = 8
        if board[x][y] != 2:
            return False
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        opponent = 1 if player_ava == 0 else 0

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            has_opponent = False
        
            while 0 <= nx < SIZE and 0 <= ny < SIZE and board[nx][ny] == opponent:
                has_opponent = True
                nx, ny = nx + dx, ny + dy
            
            if has_opponent and 0 <= nx < SIZE and 0 <= ny < SIZE and board[nx][ny] == player_ava:
                return True
            
        return False
    
    def place_and_flip(self, board, x, y, player_ava):
        if not self.is_valid_move(board, x, y, player_ava):
            return False

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        opponent = 1 if player_ava == 0 else 0
        board[x][y] = player_ava

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            flip_positions = []

            while 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == opponent:
                flip_positions.append((nx, ny))
                nx += dx
                ny += dy

            if 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == player_ava:
                for fx, fy in flip_positions:
                    board[fx][fy] = player_ava

        return True

    # クライアントからのメッセージ受信
    def receive(self, text_data):
        data = json.loads(text_data)
        # 色の選択が終わっているかを格納する、2になったときに準備完了
        player_ready = 0
        
        # 黒から動く
        player_ava = 0

        print(f"Received data: {data}") # ログを追加
        
        # 色選択するのメッセージを受信した際
        if data['gametype'] == 'color_choice':
            chosen_color = data['color']
            player_ready += 1
            if chosen_color == "black":
                player_color = 0
            else:
                player_color = 1
            response = {
                'gametype': 'updatecolor',
                'color': player_color,
                'player_ready': player_color,
                'is_ready': player_ready,
            }
            print(f"send response: {response}")
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'message': json.dumps(response),
                }
            )
            return
        
        if data['gametype'] == 'ready':
            #self.send(text_data=json.dumps({
            response = {
                'ready': 0,
                'gametype': 'ready',
                'player_ava': player_ava,
            }
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'message': json.dumps(response),
                }
            )
            return

        # 色の選択が終わり、ゲーム開始の合図
        if data['gametype'] == 'gameupdate':
            board = data['board']
            x = data['data-x']
            y = data['data-y']
            player_ava = data['player_ava']

            # 石が置けるかどうかを判定
            if self.is_valid_move(board, x, y, player_ava) == False:
                # 石が置けない
                print(self.is_valid_move(board, x, y, player_ava))
                response  = {
                    'gametype': 'game_inupdate',
                    'board': board,
                    'player_ava': player_ava,
                }
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_update',
                        'message': json.dumps(response),
                    }
                )
                return
        
            # 石が置けるなら置く
            else:
                print(self.is_valid_move(board, x, y, player_ava))
                #board[x][y] = player_ava
                self.place_and_flip(board, x, y, player_ava)

                # プレイヤーの切り替え
                next_player = 1 if player_ava == 0 else 0

                response = {
                    'gametype': 'gameupdate',
                    'board': board,
                    'player_ava': next_player,
                }
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_update',
                        'message': json.dumps(response),
                    }
                )

    # グループメッセージをWebSocketに送信
    def game_update(self, event):
        '''
        board = event['board']
        player_ava = event['player_ava']

        await self.send(text_data=json.dumps({
            'board': board,
            'player_ava': player_ava
        }))
        '''
        message = event['message']
        print('game_update-message', message)
        self.send(text_data=message)

class SugorokuGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'sugoroku_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data['action']
        payload = data['payload']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_action',
                'action': action,
                'payload': payload
            }
        )

    async def game_action(self, event):
        action = event['action']
        payload = event['payload']
        await self.send(text_data=json.dumps({
            'action': action,
            'payload': payload
        }))