from django.shortcuts import render, redirect
from .models import Session
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import timedelta
from .models import Session, Player, Card, CardEffect, Deck, CardDeck, GameState
from django.db.models import Prefetch, Count, Sum
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from .forms import DeckForm, CardForm
from django.urls import reverse
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

def index(request):
    return render(request, 'cardgame/index.html')  # 標準ユーザーは通常ページに



def session_list(request):
    sessions = Session.objects.filter(is_active=True)
    return JsonResponse({'sessions': [{'id': s.id, 'name': s.name} for s in sessions]})

@login_required
def create_card(request):
    #if request.method == 'POST':
        #name = request.POST.get('name')
        # 他の必要なフィールドも処理してカードを作成
        #card = Card.objects.create(name=name, created_by=request.user)
        #return JsonResponse({'success': True, 'card_id': card.id})
    return render(request, 'cardgame/create_card.html')




@login_required
def start_turn(request):
    current_session = request.user.session
    if current_session.is_active:
        current_session.max_mana = min(current_session.max_mana + 1, 10)
        current_session.mana = current_session.max_mana
        current_session.current_turn += 1  # 次のターンに進む
        current_session.save()
        return JsonResponse({'success': True, 'turn': current_session.current_turn})
    return JsonResponse({'success': False, 'error': 'セッションが無効です'})

@login_required
def play_card(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        target_id = request.POST.get('target_id')
        
        current_session = request.user.session
        player = request.user.player  # プレイヤーオブジェクト
        
        card = Card.objects.get(id=card_id)
        
        # マナコストの確認
        if player.mana >= card.cost:
            player.mana -= card.cost
            target = get_object_or_404(Player, id=target_id) if target_id else player  # ターゲット設定
            
            # カードの効果適用
            effects = card.effects.all()  # カードに関連する全ての効果を取得
            for effect in effects:
                if effect.effect_type == 'damage':
                    # ダメージ処理
                    target.health -= effect.value
                elif effect.effect_type == 'heal':
                    # ヒール処理
                    target.health += effect.value
                elif effect.effect_type == 'modify_value':
                    # 特定の変数を変更する処理
                    setattr(player, effect.target_field, effect.value)
            
            target.save()  # ターゲットの更新を保存
            player.save()   # プレイヤーのマナを減算して保存
            
            return JsonResponse({'success': True, 'player_mana': player.mana, 'target_id': target.id, 'effects_applied': True})
        else:
            return JsonResponse({'success': False, 'error': 'マナが不足しています'})

    return JsonResponse({'success': False, 'error': '無効なリクエストです'})



@login_required
def admin_card(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cost = request.POST.get('cost')

        # エラー時の処理
        if not name or not cost:
            return render(request, 'cardgame/admin_card.html', {'error': 'すべてのフィールドを入力してください。'})

        # 複数の効果を処理
        effect_type = request.POST.getlist('effect_type')
        target_type = request.POST.getlist('target_type')
        var = request.POST.getlist('var')

        if len(effect_type) == 0:
            return render(request, 'cardgame/admin_card.html', {'error': '少なくとも1つの効果を追加してください。'})

        card = Card.objects.create(name=name, cost=cost)

        for i in range(len(effect_type)):
            CardEffect.objects.create(
                card=card, 
                effect_type=effect_type[i], 
                target_type=target_type[i], 
                var=var[i]
            )

        return redirect('cardgame:admin_card')

    # カードを全件取得して渡す
    cards = Card.objects.prefetch_related('effects').all()  # Prefetch relatedしてエフェクトを効率的に取得
    return render(request, 'cardgame/admin_card.html', {'cards': cards})



def apply_card_effect(card_id, target):
    card = Card.objects.get(id=card_id)
    effects = card.effects.all()  # カードに関連する全ての効果を取得

    for effect in effects:
        if effect.effect_type == 'damage':
            # ダメージ処理
            pass
        elif effect.effect_type == 'heal':
            # ヒール処理
            pass
        elif effect.effect_type == 'modify_value':
            # 特定の変数を変更する処理
            pass

@login_required
def edit_card(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect('cardgame:admin_card')  # 編集後に管理ページにリダイレクト
    else:
        form = CardForm(instance=card)

    return render(request, 'cardgame/edit_card.html', {'form': form, 'card': card})

@login_required
def delete_card(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    card.delete()
    return redirect('cardgame:admin_card')  # 削除後に管理ページにリダイレクト



# デッキ一覧を表示するビュー
def deck_list(request):
    decks = Deck.objects.filter(player=request.user)
    return render(request, 'deck_list.html', {'decks': decks})

# デッキの詳細ビュー
def deck_detail(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id, player=request.user)
    cards_in_deck = CardDeck.objects.filter(deck=deck)
    available_cards = Card.objects.exclude(id__in=cards_in_deck.values('card_id'))
    return render(request, 'deck_detail.html', {
        'deck': deck,
        'cards_in_deck': cards_in_deck,
        'available_cards': available_cards
    })

# デッキ作成ビュー
def deck_create(request):
    if request.method == 'POST':
        form = DeckForm(request.POST)
        if form.is_valid():
            deck = form.save(commit=False)
            deck.player = request.user
            deck.save()
            return redirect('cardgame:deck_detail', deck_id=deck.id)
    else:
        form = DeckForm()
    return render(request, 'deck_form.html', {'form': form})

# デッキ編集ビュー
def deck_edit(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id, player=request.user)
    if request.method == 'POST':
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            form.save()
            return redirect('cardgame:deck_list')
    else:
        form = DeckForm(instance=deck)
    return render(request, 'deck_form.html', {'form': form})

@login_required
def add_card_to_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, player=request.user)
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card = get_object_or_404(Card, id=card_id)
        # CardDeckを作成してカードをデッキに登録
        CardDeck.objects.create(deck=deck, card=card)
        return redirect('cardgame:deck_detail', deck_id=deck.id)
    return JsonResponse({'success': False, 'error': '無効なリクエストです'})

@login_required
def delete_deck(request, deck_id):
    deck = get_object_or_404(Deck, id=deck_id, player=request.user)
    deck.delete()  # デッキを削除
    return redirect('cardgame:deck_list')




@login_required
def lobby_view(request):
    """ロビー画面を表示する"""
    active_sessions = Session.objects.filter(is_active=True)
    return render(request, 'lobby.html', {'sessions': active_sessions})

@login_required
def create_session(request):
    """新しいセッションを作成する"""
    if request.method == "POST":
        name = request.POST.get("name", "New Session")
        session = Session.objects.create(name=name, created_by=request.user, is_active=True)
        return JsonResponse({"success": True, "session_id": session.id})
    return JsonResponse({"success": False, "message": "Invalid request."})

@login_required
def join_session(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(Session, id=session_id, is_active=True)

        # 既に参加している場合はダッシュボードのURLを返す
        if Player.objects.filter(user=request.user, session=session).exists():
            return JsonResponse({
                "success": True,
                "message": "Already joined.",
                "redirect_url": reverse("cardgame:session_dashboard", args=[session.id])
            })

        # 新しいプレイヤーとして参加
        Player.objects.create(user=request.user, session=session)
        return JsonResponse({
            "success": True,
            "message": "Successfully joined.",
            "redirect_url": reverse("cardgame:session_dashboard", args=[session.id])
        })

    return JsonResponse({"success": False, "message": "Invalid request."})

def start_game_if_ready(session):
    players = session.get_players()
    if players.count() == 2:
        session.current_turn = 0
        session.turn_player = players.first()
        session.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"session_{session.id}",
            {
                "type": "game_start",
                "message": "Game has started!",
                "turn_player": session.turn_player.user.username,
            }
        )

@login_required
def session_dashboard(request, session_id):
    session = get_object_or_404(Session, id=session_id, is_active=True)
    players = Player.objects.filter(session=session)
    is_player = players.filter(user=request.user).exists()
    decks = Deck.objects.filter(player=request.user)
    if not is_player:
        Player.objects.create(user=request.user, session=session, is_active=False)  # 観戦者として追加

    if players.count() == 2:
        start_game_if_ready(session)

    context = {
        "session": session,
        "players": players,
        "decks": decks,
        "current_user": request.user,
    }
    return render(request, "cardgame/session_dashboard.html", context)

@login_required
def check_session_status(request):
    player = Player.objects.filter(user=request.user).first()

    if player and player.session.is_active:
        return JsonResponse({
            "is_session_active": True,
            "session_id": player.session.id,
            "redirect_url": reverse("cardgame:session_dashboard", args=[player.session.id])
        })

    return JsonResponse({"is_session_active": False})

@login_required
def session_deck_choice(request, session_id, deck_id):
    session = get_object_or_404(Session, id=session_id, is_active=True)
    if session==None:
        return render(request, "cardgame/session_dashboard.html")
    players = Player.objects.filter(session=session)
    is_player = players.filter(user=request.user).exists()
    decks = Deck.objects.filter(player=request.user)
    deck = get_object_or_404(Deck, pk=deck_id, player=request.user)
    cards_in_deck = CardDeck.objects.filter(deck=deck)
    available_cards = Card.objects.exclude(id__in=cards_in_deck.values('card_id'))
    card_effect = CardEffect.objects.all()
    current_player = Player.objects.get(user=request.user)
    if not is_player:
        return render(request, "cardgame/not_in_session.html", {"message": "You are not part of this session."})

    context = {
        "session": session,
        "players": players,
        "decks": decks,
        "deck": deck,
        "cards_in_deck": cards_in_deck,
        "available_cards": available_cards,
        "current_user": request.user,
        "card_effect": card_effect,
        "current_player": current_player,
    }
    return render(request, "cardgame/session_dashboard.html", context)


def get_session_data(request, session_id):
    session = get_object_or_404(Session, id=session_id, is_active=True)
    players = Player.objects.filter(session=session)
    is_player = players.filter(user=request.user).exists()
    decks = Deck.objects.filter(player=request.user)
    
    # Playerがセッションに参加しているか確認
    if not is_player:
        return JsonResponse({"error": "You are not part of this session."}, status=403)

    deck_id = request.GET.get('deck_id')  # URLパラメータとして渡されたdeck_idを取得
    deck = get_object_or_404(Deck, pk=deck_id, player=request.user)
    cards_in_deck = CardDeck.objects.filter(deck=deck)
    available_cards = Card.objects.exclude(id__in=cards_in_deck.values('card_id'))

    # 必要なデータをJSON形式で返す
    data = {
        "session": session.name,
        "players": list(players.values('user__username')),
        "decks": list(decks.values('id', 'name')),
        "deck": deck.name,
        "cards_in_deck": list(cards_in_deck.values('card__name')),
        "available_cards": list(available_cards.values('name')),
        "current_user": request.user.username
    }
    return JsonResponse(data)
