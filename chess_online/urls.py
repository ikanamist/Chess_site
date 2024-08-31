from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import search_view

urlpatterns = [
    path("", views.home, name="home"),
    path("game/<int:game_id>/", views.game_detail, name="game_detail"),
    path("new_game/", views.new_game, name="new_game"),
    path("make_move/<int:game_id>/", views.make_move, name="make_move"),
    path("register/", views.register, name="register"),
    path("active_games/", views.active_games, name="active_games"),  # Активные игры
    path("game_history/", views.game_history, name="game_history"),  # История игр
    path("leaders/", views.leaders, name="leaders"),  # Вкладка лидеров рейтинга
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("search/", search_view, name="search"),
]
