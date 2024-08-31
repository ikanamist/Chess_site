from django.db import models
from django.contrib.auth.models import User
import chess


class Game(models.Model):
    player_white = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="games_as_white"
    )
    player_black = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="games_as_black"
    )
    fen = models.CharField(
        max_length=100, default=chess.Board().fen()
    )  # Начальная позиция
    turn = models.CharField(max_length=5, default="white")  # Текущий ход
    status = models.CharField(
        max_length=20, default="active"
    )  # Статус игры (active, draw, white_won, black_won)

    def __str__(self):
        return f"Game between {self.player_white.username} and {self.player_black.username}"

    def update_fen(self, new_fen):
        self.fen = new_fen
        self.save()

    def end_game(self, result):
        self.status = result
        self.save()


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    from_square = models.CharField(max_length=2)  # Поле, с которого был сделан ход
    to_square = models.CharField(max_length=2)  # Поле, на которое был сделан ход
    move_number = models.IntegerField()  # Номер хода

    def __str__(self):
        return f"Move {self.move_number}: {self.from_square} -> {self.to_square}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1500)  # Начальный рейтинг

    def __str__(self):
        return f"{self.user.username} - Рейтинг: {self.rating}"
