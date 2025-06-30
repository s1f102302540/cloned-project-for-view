from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from .models import SugorokuRoom
from .models import Hit_and_blow_PlayerScore

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        """GETリクエストでログアウトを処理"""
        return self.post(request, *args, **kwargs)
    
# Create your views here.
def index(request):
    return render(request, 'index.html')

def menu(request):
    context = {
        'cards': ['制作待ち'] * 3, 
    }
    return render(request, 'menu.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'アカウント {username} が作成されました！ログインしてください。')
            return redirect('login')  # ログインページにリダイレクト
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ヒットアンドブローのviews
def hit_and_blow_home(request):
    return render(request, 'hit_and_blow/home.html')

def hit_and_blow_game(request):
    return render(request, 'hit_and_blow/hit_and_blow.html')

def hit_and_blow_ranking(request):
    top_players = [
        {'username': 'Player1', 'points': 10},
        {'username': 'Player2', 'points': 8},
        {'username': 'Player3', 'points': 7},
    ]
    return render(request, 'hit_and_blow/ranking.html', {'top_players': top_players})

from django.http import JsonResponse

def ranking_api(request):
    # ポイントが高い順でデータを取得
    top_players = Hit_and_blow_PlayerScore.objects.order_by('-points')[:10]
    data = {
        'top_players': [
            {'username': player.username, 'points': player.points}
            for player in top_players
        ]
    }
    return JsonResponse(data)

# ヒットアンドブローここまで


def sugoroku_index(request):
    """双六ゲームのトップ画面"""
    return render(request, "sugoroku/index.html")

def create_room(request):
    """ルーム作成"""
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        password = request.POST.get("password")
        if SugorokuRoom.objects.filter(name=room_name).exists():
            return render(request, "sugoroku/create_room.html", {"error": "ルーム名が既に使用されています。"})
        SugorokuRoom.objects.create(name=room_name, password=password)
        return redirect("sugoroku_game", room_name=room_name)
    return render(request, "sugoroku/create_room.html")

def join_room(request):
    """ルーム参加"""
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        password = request.POST.get("password")
        room = SugorokuRoom.objects.filter(name=room_name, password=password).first()
        if room:
            return redirect("sugoroku_game", room_name=room_name)
        return render(request, "sugoroku/join_room.html", {"error": "ルーム名またはパスワードが間違っています。"})
    return render(request, "sugoroku/join_room.html")

def game_view(request, room_name):
    """ゲーム画面"""
    room = get_object_or_404(SugorokuRoom, name=room_name)
    return render(request, "sugoroku/game.html", {"room_name": room_name})

def othello(request, room_name):
    return render(request, 'othello/othello.html', {"room_name": room_name})

def othello_index(request):
    return render(request, 'othello/othello_index.html')