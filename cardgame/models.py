from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
import random

class Session(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    turn_proceccing = models.PositiveIntegerField(default=0)
    current_turn = models.PositiveIntegerField(default=0)
    max_mana = models.PositiveIntegerField(default=0)
    mana = models.PositiveIntegerField(default=0)
    turn_player = models.ForeignKey(
        'Player', 
        related_name='active_sessions', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    def get_players(self):
        return self.players.filter(is_active=True)
    
class Card(models.Model):
    name = models.CharField(max_length=100)
    cost = models.IntegerField()

    def __str__(self):
        return self.name

class CardEffect(models.Model):
    card = models.ForeignKey(Card, related_name='effects', on_delete=models.CASCADE)
    effect_type = models.CharField(max_length=50)  # 'damage', 'heal', 'modify_value' などの種類
    target_type = models.IntegerField() 
    var = models.IntegerField(default=0)  # 効果の程度（ダメージ量、回復量など）

    def __str__(self):
        return f"{self.effect_type} ({self.target_type}) for {self.card.name}"

    def apply(self, target):
        if self.effect_type == 'damage':
            if self.target_type in ['self', 'all']:
                target.health -= self.var
            if self.target_type in ['opponent', 'all']:
                target.health += self.var
        elif self.effect_type == 'heal':
            if self.target_type in ['self', 'all']:
                target.health += self.var
            if self.target_type in ['opponent', 'all']:
                target.health -= self.var
        elif self.effect_type == 'modify_value':
            if self.target_type in ['self', 'all']:
                target.mana = min(target.mana + self.var, target.max_mana)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, related_name='players', on_delete=models.CASCADE)
    health = models.IntegerField(default=20)  # 初期体力20
    mana = models.IntegerField(default=0)    # 現在のマナ
    max_mana = models.IntegerField(default=0)  # 最大マナ
    deck_id = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)  # プレイヤー or 観戦者
    def draw_card(self, num=1):
        deck_cards = CardDeck.objects.filter(deck=self.deck)
        if deck_cards.count() == 0:
            return None
        drawn_cards = random.sample(list(deck_cards), num)
        return drawn_cards

    def restore_mana(self):
        if self.mana < 0:
            self.mana += self.max_mana
        else:
            self.mana = self.max_mana

    def __str__(self):
        return f"{self.user.username} - {self.session.name}"
    @property
    def opponent(self):
        return self.session.players.exclude(id=self.id).first()


class Deck(models.Model):
    name = models.CharField(max_length=100)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # ここでnull=Trueを追加
    # ほかのフィールドも必要に応じて

    def __str__(self):
        return self.name

class CardDeck(models.Model):
    deck = models.ForeignKey(Deck, related_name='deck_cards', on_delete=models.CASCADE)
    card = models.ForeignKey(Card, related_name='deck_cards', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.card.name} x{self.quantity} in {self.deck}"

class CardEffectRelation(models.Model):
    deck_card = models.ForeignKey(CardDeck, related_name='card_effects', on_delete=models.CASCADE)
    card_effect = models.ForeignKey(CardEffect, related_name='deck_card_effects', on_delete=models.CASCADE)
    var = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.card_effect.effect_type} for {self.deck_card.card.name}"
    
class GameRule(models.Model):
    session = models.OneToOneField(
        'Session', related_name='game_rule', on_delete=models.CASCADE
    )
    max_mana = models.PositiveIntegerField(default=10)
    mana_recovery = models.PositiveIntegerField(default=1)  # 毎ターンのマナ回復量
    turn_time_limit = models.PositiveIntegerField(default=60)  # ターン制限時間（秒）

    def __str__(self):
        return f"Rules for {self.session.name}"

class Turn(models.Model):
    session = models.ForeignKey(
        'Session', related_name='turns', on_delete=models.CASCADE
    )
    player = models.ForeignKey(
        'Player', related_name='turns', on_delete=models.CASCADE
    )
    turn_number = models.PositiveIntegerField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Turn {self.turn_number} for {self.player.user.username}"

class GameState(models.Model):
    session = models.OneToOneField(
        'Session', related_name='game_state', on_delete=models.CASCADE
    )
    current_turn = models.PositiveIntegerField(default=0)
    preparation_time_left = models.PositiveIntegerField(default=10)  # 秒単位の準備時間
    is_active = models.BooleanField(default=False)  # 戦闘が開始されているか

    def __str__(self):
        return f"State for {self.session.name}: {'Active' if self.is_active else 'Inactive'}"

    def start_battle(self):
        self.is_active = True
        self.current_turn = 1
        self.save()