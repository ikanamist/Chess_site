from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Game, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import UserRegisterForm
import chess
from django.db.models import Q
from django.contrib import messages


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect("home")  # Перенаправление на home
    else:
        form = UserRegisterForm()
    return render(request, "chess/register.html", {"form": form})


@login_required
def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    board = chess.Board(game.fen)

    piece_unicode = {
        "P": "♙",
        "R": "♖",
        "N": "♘",
        "B": "♗",
        "Q": "♕",
        "K": "♔",
        "p": "♟",
        "r": "♜",
        "n": "♞",
        "b": "♝",
        "q": "♛",
        "k": "♚",
    }

    board_representation = []
    for row in range(8):
        board_row = []
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            board_row.append(
                {
                    "piece": piece_unicode[piece.symbol()] if piece else None,
                    "color": "dark" if (row + col) % 2 != 0 else "light",
                }
            )
        board_representation.append(
            (8 - row, board_row)
        )  # Добавляем номер строки и ряд

    return render(
        request, "chess/game_detail.html", {"game": game, "board": board_representation}
    )


@login_required
def new_game(request):
    opponent_id = request.GET.get("opponent_id")

    if opponent_id:
        opponent = get_object_or_404(User, id=opponent_id)

        # Проверка на наличие уже существующей активной игры между пользователями
        existing_game = Game.objects.filter(
            (
                Q(player_white=request.user) & Q(player_black=opponent)
                | Q(player_white=opponent) & Q(player_black=request.user)
            )
            & Q(status="active")
        ).first()

        if existing_game:
            # Если существует активная игра, перенаправляем на существующую игру
            return redirect("game_detail", game_id=existing_game.id)

        # Если активной игры нет, создаем новую
        game = Game.objects.create(player_white=request.user, player_black=opponent)
        return redirect("game_detail", game_id=game.id)

    return redirect("home")


@login_required
def make_move(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    # Проверка, что игра активна
    if game.status != "active":
        messages.error(request, "The game is no longer active.")
        return redirect("game_detail", game_id=game.id)

    # Проверка, что это ход текущего игрока
    if (game.turn == "white" and request.user != game.player_white) or (
        game.turn == "black" and request.user != game.player_black
    ):
        messages.error(request, "It's not your turn to move.")
        return redirect("game_detail", game_id=game.id)

    # Обработка POST-запроса для выполнения хода
    if request.method == "POST":
        from_square = request.POST.get("from_square")
        to_square = request.POST.get("to_square")

        if not from_square or not to_square:
            messages.error(request, "Both 'from' and 'to' squares must be specified.")
            return redirect("game_detail", game_id=game.id)

        board = chess.Board(game.fen)

        try:
            move = chess.Move.from_uci(from_square + to_square)
        except ValueError:
            messages.error(
                request, "Invalid move format. Please use a valid move notation."
            )
            return redirect("game_detail", game_id=game.id)

        if move in board.legal_moves:
            board.push(move)
            game.fen = board.fen()
            game.turn = "black" if game.turn == "white" else "white"
            game.save()

            if board.is_checkmate():
                game.status = "white_won" if game.turn == "black" else "black_won"
                game.save()
                adjust_ratings(game)
                messages.success(
                    request,
                    f"Checkmate! {'White' if game.status == 'white_won' else 'Black'} wins!",
                )
            elif board.is_stalemate() or board.is_insufficient_material():
                game.status = "draw"
                game.save()
                messages.info(request, "The game is a draw.")

        else:
            messages.error(request, "Invalid move. Please try again.")
            return redirect("game_detail", game_id=game.id)

        return redirect("game_detail", game_id=game.id)

    return redirect("game_detail", game_id=game.id)


@login_required
def active_games(request):
    games = Game.objects.filter(
        (Q(player_white=request.user) | Q(player_black=request.user))
        & Q(status="active")
    )
    return render(request, "chess/active_games.html", {"games": games})


@login_required
def game_history(request):
    games = Game.objects.filter(
        (Q(player_white=request.user) | Q(player_black=request.user))
        & ~Q(status="active")
    )
    return render(request, "chess/game_history.html", {"games": games})


@login_required
def home(request):
    query = request.GET.get(
        "q", ""
    )  # Получаем поисковый запрос, если есть, или пустую строку по умолчанию
    if query:
        opponents = (
            User.objects.filter(username__icontains=query)
            .exclude(id=request.user.id)
            .exclude(is_superuser=True)
        )
    else:
        opponents = []  # Пустой список по умолчанию

    user_profile = request.user.userprofile  # Получаем профиль текущего пользователя

    return render(
        request,
        "chess/home.html",
        {
            "user_profile": user_profile,
            "opponents": opponents,
            "query": query,
        },
    )


def adjust_ratings(game):
    white_player_profile = game.player_white.userprofile
    black_player_profile = game.player_black.userprofile

    if game.status == "white_won":
        white_player_profile.rating += 25
        black_player_profile.rating -= 25
    elif game.status == "black_won":
        white_player_profile.rating -= 25
        black_player_profile.rating += 25
    elif game.status == "draw":
        pass  # Рейтинг не изменяется

    white_player_profile.save()
    black_player_profile.save()


@login_required
def leaders(request):
    top_players = UserProfile.objects.order_by("-rating")[:10]
    return render(request, "chess/leaders.html", {"top_players": top_players})


@login_required
def search_view(request):
    query = request.GET.get("q", "")
    opponents = User.objects.filter(username__icontains=query)

    # Получаем данные профиля пользователя
    user_profile = request.user.userprofile

    # Список активных игр между текущим пользователем и найденными оппонентами
    active_games = {}
    for opponent in opponents:
        existing_game = Game.objects.filter(
            (
                (Q(player_white=request.user) & Q(player_black=opponent))
                | (Q(player_white=opponent) & Q(player_black=request.user))
            )
            & Q(status="active")
        ).first()
        if existing_game:
            active_games[opponent.id] = existing_game

    return render(
        request,
        "chess/home.html",
        {
            "opponents": opponents,
            "query": query,
            "user_profile": user_profile,
            "active_games": active_games,  # Передаем активные игры в шаблон
        },
    )
