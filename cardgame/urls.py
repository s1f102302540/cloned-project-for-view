from django.urls import path
from . import views

app_name = 'cardgame'

urlpatterns = [
    path('', views.index, name='index'),
    path('create_card/', views.create_card, name='create_card'),
    path('start_turn/', views.start_turn, name='start_turn'),  # ターン開始エンドポイント
    path('play_card/', views.play_card, name='play_card'),     # カード使用エンドポイント
    path('admin_card/', views.admin_card, name='admin_card'),  # 管理者向けのカード管理ページ
    path('edit_card/<int:card_id>/', views.edit_card, name='edit_card'), #(未実装)一般ユーザー用カード作成ページ
    path('delete_card/<int:card_id>/', views.delete_card, name='delete_card'), #カードの削除
    path('deck/', views.deck_list, name='deck_list'), #デッキ管理系
    path('deck/<int:deck_id>/', views.deck_detail, name='deck_detail'),
    path('deck/<int:deck_id>/edit/', views.deck_edit, name='deck_edit'),
    path('deck/create/', views.deck_create, name='deck_create'),
    path('deck/<int:deck_id>/add_card/', views.add_card_to_deck, name='add_card_to_deck'),
    path('deck/<int:deck_id>/delete/', views.delete_deck, name='delete_deck'),

    path('lobby/', views.lobby_view, name='lobby'),
    path('session/create/', views.create_session, name='create_session'),
    path('session/join/<int:session_id>/', views.join_session, name='join_session'),
    path("session/<int:session_id>/dashboard/", views.session_dashboard, name="session_dashboard"),
    path("session/<int:session_id>/dashboard/<int:deck_id>/", views.session_deck_choice, name="session_dashboard_choice_deck"),

]
