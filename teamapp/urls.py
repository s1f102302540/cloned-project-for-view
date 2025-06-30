from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('', views.index, name='index'),  # URLパターンにビューを紐づける
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/menu/'), name='logout'),
    path('register/', views.register, name='register'),

    # ヒットアンドブロー
    path('hit_and_blow_home/', views.hit_and_blow_home, name='hit_and_blow_home'),
    path('hit_and_blow_game/', views.hit_and_blow_game, name='hit_and_blow_game'),
    path('hit_and_blow_ranking/', views.hit_and_blow_ranking, name='hit_and_blow_ranking'),
    path('hit_and_blow/ranking/api/', views.ranking_api, name='hit_and_blow_ranking_api'),  # ランキング更新API

    # オセロ
    path('othello_index/<str:room_name>/', views.othello, name='othello_game'),
    path('othello_index/', views.othello_index, name="othello_index"),

    # すごろく
    path('sugoroku/', views.sugoroku_index, name='sugoroku_home'),  # すごろくのホーム画面へのパス
    path('sugoroku_index/', views.sugoroku_index, name='sugoroku_index'),
    path('create_room/', views.create_room, name='create_room'),
    path('join_room/', views.join_room, name='join_room'),
    path('game/<str:room_name>/', views.game_view, name='sugoroku_game')
]
