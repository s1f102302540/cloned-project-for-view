import time
import json
from asgiref.sync import sync_to_async
from .models import Session, Player, Card, CardDeck, CardEffect, Deck
from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import sleep
from django.contrib.auth.models import User
import random
import asyncio
import time
from channels.layers import get_channel_layer

@sync_to_async
def activate_turn(self, session):
    session.turn_proceccing+=1
    session.save()
    print("セッションを起動しました。")

@sync_to_async
def get_player_username(player):
    return player.user.username

@sync_to_async
def process_turn(self, session, player):
    # 待機後に実行する処理
    session.current_turn+=1
    if session.max_mana<10:
        session.max_mana+=1
    session.mana=session.max_mana
    session.save()
    
    players = self.player.session.players.all()
    for player in players:
        player.max_mana+=1
        if player.mana < player.max_mana:
            player.mana+=player.max_mana
            if player.mana > player.max_mana:
                player.mana=player.max_mana
        deck= Deck.objects.get(id = player.deck_id)
        print("デッキ:",deck, player.deck_id)
        cards=CardDeck.objects.filter(deck = deck)
        for card in cards:
            print("読み込んだカード: ",card.card)
        player.save()

@sync_to_async
def get_player_count(self, player):
    players = player.session.players.all()
    player_count=0
    for p in players:
        player_count+=1
    return player_count

@sync_to_async
def set_deck_id(self, player, deck_id):
    player.deck_id=int(deck_id)
    player.save()

@sync_to_async
def check_battle_end(self, player):
    players = player.session.players.all()
    alive_count=0
    player_count=0
    for p in players:
        if p.health>0:
            alive_count+=1
            alive_player=p.user.username
            player_count+=1
        else:
            player_count+=1
    print("生存数:", alive_count, "  プレイヤー数:", player_count)
    if alive_count==1 and player_count>1:
        player.session.players
        message=(str(alive_player)+"が戦線に勝利しました！")
        print(message)
        p.session.delete()
        return message
    return None

@sync_to_async
def apply_effect(self, card_effects, player):
    message=[]
    for effect in card_effects:
        print("ターゲット",effect.target_type, " エフェクトタイプ:",effect.effect_type, " 効果量",effect.var)
        target=effect.target_type
        effect_type=effect.effect_type
        var=effect.var
        #effect.apply を呼び出してターゲットに効果を適用
        if target == 2:  # 自分に適用
            if effect_type=="damage":
                helath_before=player.health
                player.health-=var
                print(player.health)
                message.append(str(player.user.username)+"に"+str(var)+"のダメージ！"+"体力:"+str(health_before)+"=>"+str(player.health))
                player.save()
            elif effect_type=="heal":
                health_before=player.health
                player.health+=var
                print(player.health)
                message.append(str(player.user.username)+"が"+str(var)+"回復！"+"体力:"+str(health_before)+"=>"+str(player.health))
                player.save()
        elif int(effect.target_type) == 1:  # 相手プレイヤーに適用
            opponents = player.session.players.all().exclude(id=player.id)  # プレイヤーの対戦相手
            print("敵: ", opponents)
            if opponents:  # 対戦相手が存在する場合
                for opponent in opponents:
                    if effect_type=="damage":
                        health_before=opponent.health
                        opponent.health-=var
                        print(opponent, opponent.health)
                        message.append(str(opponent.user.username)+"に"+str(var)+"のダメージ！"+"体力:"+str(health_before)+"=>"+str(opponent.health))
                        opponent.save()
            else:
                message.append("敵が見つからない！")
        elif effect.target_type == 3:  # すべてのプレイヤーに適用
           for p in player.session.players.all():
                effect.apply(p)
        message.append('<br>')
    return message
            

@sync_to_async
def get_cardeffect_by_card(card):
    return CardEffect.objects.filter(card=card)

class CardGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session = await self.get_session(self.session_id)
        self.group_name = f'session_{self.session_id}'  # グループ名の設定
        
        # グループへの参加
        await self.channel_layer.group_add(
        self.group_name,
        self.channel_name
        )

        print(f"User {self.scope['user'].username} joined group {self.group_name}")
        # WebSocket接続を許可
        await self.accept()

        await self.send(text_data=json.dumps({
            'message': f'ルーム {self.session_id} への接続が確立されました。'
        }))
        
        self.user = self.scope['user']
        self.player = await self.get_player(self.session_id, self.scope['user'])

        player_count= await get_player_count(self, self.player)
        print("現在のプレイヤー数: ", player_count)
        
        delay = random.uniform(0.01, 1.0)
        print(f"遅延: {delay:.2f}秒")
        await asyncio.sleep(delay)
        self.session = await self.get_session(self.session_id)

        print("セッションの状態: " ,self.session.turn_proceccing, self.session.current_turn, int(self.session.turn_proceccing) == int(self.session.current_turn))
        if int(player_count)==1:
            await self.send(text_data=json.dumps({
            'type': 'message',
            'message': '戦線開始に必要なプレイヤーを待っています。(現在1)'
        }))
        elif int(player_count)>1 and int(self.session.turn_proceccing) == int(self.session.current_turn):
            await activate_turn(self,self.session)
            asyncio.create_task(self.perform_background_task(self.session))
        
        await self.view_player_info(self.player)
        #self.deck = await self.get_deck(self.player.user)
        self.deck_id = self.scope['url_route']['kwargs']['deck_id']
        print(self.deck_id)
        await set_deck_id(self ,self.player, self.deck_id)

        # プレイヤーに利用可能なカードを送信
        #await self.send_player_data()

        # プレイヤーのデッキからランダムにカードを選択
        #card_to_use = self.get_random_card(self.deck)
        #await self.send(text_data=json.dumps({
        #    'type': 'card_selected',
        #    'card': card_to_use,
        #}))
        
        # ターン管理用のタイマーをスタート
        #await self.start_turn_timer()

    async def disconnect(self, close_code):
        # 切断処理（必要に応じて処理を追加）
        await self.channel_layer.group_discard(
        self.group_name,
        self.channel_name
        )
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        
        if action == 'draw_card':
            await self.draw_card()
        elif action == 'play_card':
            card_id = text_data_json['card_id']
            await self.play_card(card_id)

    async def perform_background_task(self, session):
        await asyncio.sleep(1)
        await self.channel_layer.group_send(self.group_name,{'type': 'message','message': 'ターン:'+str(session.current_turn)}  )
        await asyncio.sleep(9)
        self.player = await self.get_player(self.session_id, self.scope['user'])
        await process_turn(self, session, self.player)
        await self.channel_layer.group_send(self.group_name,{'type': 'turn_end','message': 'ターンが経過しました。'}  )
            



    async def card_played(self, event):
        player_name = event['player_name']
        card = event['card']
        player_mana = event['player_mana']
        message=event['message']
        await self.send(text_data=json.dumps({
            'type': 'card_played',
            'player_name': player_name,
            'card': card,
            'player_mana': player_mana,
            'message': message
        }))

    async def end_log(self, event):
        end_log=event['end_log']
        await self.send(text_data=json.dumps({
            'type': 'end_log',
            'message': end_log,
        }))

    async def message(self, event):
        message=event['message']
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
        }))

    async def turn_end(self, event):
        message=event['message']
        await self.send(text_data=json.dumps({
            'type': 'turn_end',
            'message': message,
        }))

    async def play_card(self, card_id):
        player = await self.get_player(self.session_id, self.scope['user'])
        player_name = await get_player_username(player)
        card = await self.get_card_by_id(card_id)
        player.mana -= card.cost
        await sync_to_async(player.save)()
        
        card_effects = await get_cardeffect_by_card(card)  # カードに関連する効果を取得
        messages = await apply_effect(self, card_effects, player)
        # カードを使用した後の状態を通知(グループに送るようにしたから多分いらない)
        #await self.send(text_data=json.dumps({
        #    'type': 'card_played',
        #    'player_name': player_name,
        #    'card': card.name,
        #    'player_mana': player.mana
        #    
        #}))
        await self.channel_layer.group_send(
        self.group_name,
        {
        'type': 'card_played',
        'player_name': player_name,
        'card': card.name,
        'player_mana': player.mana,
        'message': messages
        }  
        )
        print(f"Message sent to group {self.group_name}: {player_name} played {card.name}")
        end_log= await check_battle_end(self, player)
        if end_log:
            await self.channel_layer.group_send(
            self.group_name,
            {
            'type': 'end_log',
            'end_log':end_log
            }  
            )
            print(f"sended end log")
        

    async def draw_card(self):
        player = await self.get_player(self.session_id, self.scope['user'])
        card = await self.get_random_card(self.deck)

        # カードを引いた後の状態を更新
        await self.send(text_data=json.dumps({
            'type': 'card_drawn',
            'card': card.name
        }))



    async def apply_card_effect(self, player, card):
        """
        カードの効果を適用する処理
        """
        card_effects = await self.get_card_effects(card)
        print(card_effects)
        #for effect in card_effects:
        #    # カードの効果を実行（例：プレイヤーのHPを回復する、ダメージを与えるなど）
        #    if effect.type == 'damage':
        #        player.hp -= effect.amount
        #    elif effect.type == 'heal':
        #        player.hp += effect.amount
        #    elif effect.type == 'mana':
        #        player.mana += effect.amount

            # 効果が適用された後、プレイヤーのデータを更新
        #    await sync_to_async(player.save)()

    async def send_player_data(self):
        player = await self.get_player(self.session_id, self.scope['user'])
        cards = await self.get_available_cards(player)
        
        await self.send(text_data=json.dumps({
            'type': 'session_info',
            'session': {
                'name': self.session.name,
                'current_turn': self.session.current_turn  # 現在のターン（時間経過で進行）
            },
            'player': {
                'username': player.user.username,
                'mana': player.mana
            },
            'available_cards': [{'id': card.id, 'name': card.name, 'cost': card.cost} for card in cards]
        }))

    async def start_turn_timer(self):
        while True:
            # 最新のSessionデータを取得して同期を取る
            self.session = await self.get_session(self.session_id)

            # 現在のターンを終了し、次のターンに進む
            self.session.current_turn += 1
            await sync_to_async(self.session.save)()  # 非同期で保存

            # 現在のターンをクライアントに通知
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'turn_update',
                    'current_turn': self.session.current_turn
                }
            )

            # 10秒後に次のターンに進む
            await sleep(10)  # 非同期でスリープ

    def get_random_card(self, deck):
        # デッキからランダムに1枚選択
        cards_in_deck = CardDeck.objects.filter(deck=deck)
        card_ids = [card.card.id for card in cards_in_deck]
        random_card_id = random.choice(card_ids)
        return Card.objects.get(id=random_card_id)
    
    @sync_to_async
    def get_session(self, session_id):
        return Session.objects.get(id=session_id)

    @sync_to_async
    def get_player(self, session_id, user):
    # userがUserインスタンスであることを確認
        print(f"user.id: {user.id}, type: {type(user.id)}")
        if not isinstance(user, User):
            raise ValueError("Invalid user instance")

        return Player.objects.get(session_id=session_id, user=int(user.id))

    @sync_to_async
    def get_card_by_id(self, card_id):
        return Card.objects.get(id=card_id)


    @sync_to_async
    def get_player_by_username(self, username):
        return Player.objects.get(user__username=username)

    @sync_to_async
    def get_deck(self, player):
        return Deck.objects.get(player=player)

    @sync_to_async
    def get_available_cards(self, player):
        # プレイヤーが使用できるカードを取得
        return Card.objects.filter(deck__player=player)

    @sync_to_async
    def get_card_effects(self, card):
        # カードの効果を取得
        return CardEffect.objects.filter(card=card)
    
    @sync_to_async
    def view_player_info(self, player):
        print(player.user)

    @sync_to_async 
    def get_cardeffect_by_card(card):
        return CardEffect.objects.filter(card=card)
