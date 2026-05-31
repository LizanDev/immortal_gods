"""Minigames views."""

import json
import random
from typing import TypedDict

from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from apps.gods.models import God

from .models import CardGameSession, DailyWheelSpin, MemoryGameSession

MEMORY_PAIR_COUNT = 8

UNAVAILABLE = {"status": "error", "message": "Database unavailable"}


class WheelSegment(TypedDict):
    """Single wheel segment definition."""

    label: str
    type: str
    amount: int
    weight: int


WHEEL_SEGMENTS: list[WheelSegment] = [
    {"label": "100 💎", "type": "gems", "amount": 100, "weight": 5},
    {"label": "50 💎", "type": "gems", "amount": 50, "weight": 15},
    {"label": "20 💎", "type": "gems", "amount": 20, "weight": 25},
    {"label": "500 🪙", "type": "gold", "amount": 500, "weight": 20},
    {"label": "200 🪙", "type": "gold", "amount": 200, "weight": 25},
    {"label": "Suerte 🍀", "type": "nothing", "amount": 0, "weight": 10},
]


def _pick_wheel_reward() -> WheelSegment:
    """Pick a weighted random reward from wheel segments."""
    total = sum(s["weight"] for s in WHEEL_SEGMENTS)
    r = random.randint(1, total)
    cumulative = 0
    for segment in WHEEL_SEGMENTS:
        cumulative += segment["weight"]
        if r <= cumulative:
            return segment
    return WHEEL_SEGMENTS[0]


@login_required
def index(request):
    """Hub page for all minigames."""
    profile = request.user.profile

    try:
        today_memory = MemoryGameSession.objects.filter(
            player=profile, played_date=timezone.now().date(), completed=True
        ).first()
        today_wheel = DailyWheelSpin.objects.filter(
            player=profile, spun_date=timezone.now().date()
        ).first()
        today_cards = CardGameSession.objects.filter(
            player=profile, played_date=timezone.now().date(), completed=True
        ).first()
        best_score = (
            MemoryGameSession.objects.filter(player=profile, completed=True)
            .order_by("moves")
            .first()
        )
    except DatabaseError:
        today_memory = None
        today_wheel = None
        today_cards = None
        best_score = None

    return render(
        request,
        "minigames/index.html",
        {
            "profile": profile,
            "today_memory": today_memory,
            "memory_available": not today_memory or not today_memory.reward_claimed,
            "today_wheel": today_wheel,
            "wheel_available": not today_wheel,
            "today_cards": today_cards,
            "cards_available": not today_cards or not today_cards.reward_claimed,
            "best_score": best_score.moves if best_score else None,
        },
    )


@login_required
def memory_game(request):
    """Memory of Gods game page."""
    profile = request.user.profile

    try:
        today_session = MemoryGameSession.objects.filter(
            player=profile, played_date=timezone.now().date()
        ).first()
    except DatabaseError:
        today_session = None

    if today_session and today_session.reward_claimed:
        return render(
            request,
            "minigames/memory.html",
            {"session": today_session, "finished": True, "gods": []},
        )

    try:
        picked_gods = list(God.objects.order_by("?")[:MEMORY_PAIR_COUNT])
    except DatabaseError:
        picked_gods = []

    gods_data = []
    for god in picked_gods:
        card = {"id": god.id, "name": god.name, "image_url": god.image_url}
        gods_data.append(card)
        gods_data.append(card.copy())

    random.shuffle(gods_data)

    return render(
        request,
        "minigames/memory.html",
        {
            "gods": gods_data,
            "total_pairs": MEMORY_PAIR_COUNT,
            "session": today_session,
            "finished": bool(today_session and today_session.completed),
        },
    )


@login_required
def memory_save(request):
    """Save a completed memory game result."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        existing = MemoryGameSession.objects.filter(
            player=profile, played_date=timezone.now().date(), completed=True
        ).first()
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if existing:
        return JsonResponse({"status": "already_completed"})

    try:
        data = json.loads(request.body)
        moves = int(data.get("moves", 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

    if moves < 8:
        return JsonResponse({"status": "error", "message": "Invalid moves"}, status=400)

    try:
        session, _ = MemoryGameSession.objects.get_or_create(
            player=profile,
            played_date=timezone.now().date(),
            defaults={
                "pairs_total": MEMORY_PAIR_COUNT,
                "moves": moves,
                "completed": True,
            },
        )
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if not session.completed:
        session.moves = moves
        session.completed = True
        session.save(update_fields=["moves", "completed"])

    return JsonResponse(
        {
            "status": "ok",
            "moves": session.moves,
            "reward_gems": session.reward_gems,
        }
    )


@login_required
def memory_claim(request):
    """Claim the memory game reward."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        session = MemoryGameSession.objects.filter(
            player=profile, played_date=timezone.now().date(), completed=True
        ).first()
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if not session:
        return JsonResponse({"status": "no_session"}, status=404)

    gems = session.claim_reward()
    if gems == 0:
        return JsonResponse({"status": "already_claimed"})

    return JsonResponse({"status": "ok", "gems": gems})


@login_required
def wheel_of_fortune(request):
    """Wheel of Fortune page."""
    profile = request.user.profile
    try:
        today_spin = DailyWheelSpin.objects.filter(
            player=profile, spun_date=timezone.now().date()
        ).first()
    except DatabaseError:
        today_spin = None

    segments_json = json.dumps(
        [
            {"label": s["label"], "type": s["type"], "amount": s["amount"]}
            for s in WHEEL_SEGMENTS
        ]
    )

    return render(
        request,
        "minigames/wheel.html",
        {
            "profile": profile,
            "today_spin": today_spin,
            "can_spin": not today_spin,
            "segments": segments_json,
            "segments_parsed": WHEEL_SEGMENTS,
        },
    )


@login_required
def wheel_spin(request):
    """Execute a wheel spin."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        existing = DailyWheelSpin.objects.filter(
            player=profile, spun_date=timezone.now().date()
        ).first()
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if existing:
        return JsonResponse({"status": "already_spun"})

    reward = _pick_wheel_reward()

    try:
        spin = DailyWheelSpin.objects.create(
            player=profile,
            reward_type=reward["type"],
            reward_amount=reward["amount"],
            spun_date=timezone.now().date(),
        )
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    try:
        if reward["type"] == "gems":
            profile.add_gems(reward["amount"])
        elif reward["type"] == "gold":
            profile.add_gold(reward["amount"])
    except DatabaseError:
        pass

    segments_json = [
        {"label": s["label"], "type": s["type"], "amount": s["amount"]}
        for s in WHEEL_SEGMENTS
    ]

    reward_index = WHEEL_SEGMENTS.index(reward)

    return JsonResponse(
        {
            "status": "ok",
            "reward_type": spin.reward_type,
            "reward_amount": spin.reward_amount,
            "reward_label": reward["label"],
            "reward_index": reward_index,
            "segments": segments_json,
        }
    )


# ─── Card Duel (Triple Triad-style) ────────────────────────────────

CARD_HAND_SIZE = 5
GRID_SIZE = 3


def _stat_to_card_value(raw: int, divisor: int, max_val: int = 9) -> int:
    return max(1, min(max_val, raw // divisor))


def _god_to_card(pg) -> dict:
    """Convert a PlayerGod to a card dict with 4 directional values."""
    return {
        "name": pg.god.name,
        "image_url": pg.god.image_url,
        "values": {
            "top": _stat_to_card_value(pg.total_attack, 50),
            "right": _stat_to_card_value(pg.total_defense, 50),
            "bottom": _stat_to_card_value(pg.total_speed, 20),
            "left": _stat_to_card_value(pg.total_hp, 300),
        },
    }


def _random_ai_card() -> dict:
    """Generate a random AI card with values 1-9."""
    values = {
        "top": random.randint(1, 9),
        "right": random.randint(1, 9),
        "bottom": random.randint(1, 9),
        "left": random.randint(1, 9),
    }
    names = [
        "Soldado Oscuro", "Bestia Salvaje", "Espíritu del Caos",
        "Guardián Maldito", "Aprendiz de Brujo", "Gólem de Roca",
        "Sombra Letal", "Demonio Menor", "Lobo de Guerra",
        "Centinela del Abismo", "Arquero Espectral", "Caballero Oscuro",
    ]
    return {
        "name": random.choice(names),
        "image_url": "",
        "values": values,
    }


def _make_empty_board() -> list:
    return [[None] * GRID_SIZE for _ in range(GRID_SIZE)]


def _get_opposite(side: str) -> str:
    opposites = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}
    return opposites[side]


def _resolve_flips(
    board: list, row: int, col: int, owner: str, values: dict
) -> list[dict]:
    """Check all 4 adjacent cells and flip opponent cards where applicable.
    Returns list of flip descriptions."""
    flips: list[dict] = []
    adjacents = [
        (row - 1, col, "top", "bottom"),
        (row + 1, col, "bottom", "top"),
        (row, col - 1, "left", "right"),
        (row, col + 1, "right", "left"),
    ]
    for r, c, my_side, their_side in adjacents:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            cell = board[r][c]
            if cell and cell["owner"] != owner:
                if values[my_side] > cell["values"][their_side]:
                    cell["owner"] = owner
                    flips.append({"row": r, "col": c, "card": cell})
    return flips


def _ai_choose_move(
    board: list, ai_hand: list
) -> tuple[int, int, int] | None:
    """AI picks the best card and position. Returns (card_index, row, col) or None."""
    best_score = -1
    best_move = None

    for ci, card in enumerate(ai_hand):
        if card.get("used"):
            continue
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] is not None:
                    continue
                flips = _resolve_flips(board, r, c, "ai", card["values"])
                score = len(flips)
                # Prefer center > corners > edges when no flip available
                if score == 0:
                    if (r, c) == (1, 1):
                        score = 1
                    elif (r, c) in {(0, 0), (0, 2), (2, 0), (2, 2)}:
                        score = 0
                if score > best_score:
                    best_score = score
                    best_move = (ci, r, c)

    return best_move


@login_required
def card_game(request):
    """Card duel game page - start or resume today's session."""
    profile = request.user.profile
    today = timezone.now().date()

    try:
        session = CardGameSession.objects.filter(
            player=profile, played_date=today
        ).first()
    except DatabaseError:
        session = None

    if session and session.completed:
        return render(
            request,
            "minigames/card.html",
            {
                "session": session,
                "board": session.board_state,
                "player_hand": session.player_hand,
                "finished": True,
                "won": session.won,
            },
        )

    if not session:
        gods_qs = list(
            profile.gods.select_related("god").filter(god__isnull=False)
        )
        random.shuffle(gods_qs)
        picked = gods_qs[:CARD_HAND_SIZE]

        if len(picked) < CARD_HAND_SIZE:
            return render(
                request,
                "minigames/card.html",
                {
                    "error": (
                        f"Necesitas al menos {CARD_HAND_SIZE} dioses"
                        " para jugar al Duelo de Cartas."
                    ),
                },
            )

        player_hand = [_god_to_card(pg) for pg in picked]
        ai_hand = [_random_ai_card() for _ in range(CARD_HAND_SIZE)]

        try:
            session = CardGameSession.objects.create(
                player=profile,
                played_date=today,
                board_state=_make_empty_board(),
                player_hand=player_hand,
                ai_hand=ai_hand,
            )
        except DatabaseError:
            return render(
                request,
                "minigames/card.html",
                {"error": "Error de base de datos. Intenta de nuevo."},
            )

    return render(
        request,
        "minigames/card.html",
        {
            "session": session,
            "board": session.board_state,
            "player_hand": session.player_hand,
            "current_turn": session.current_turn,
            "finished": False,
        },
    )


@login_required
def card_place(request):
    """Place a card on the board (player turn), then AI responds."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile
    today = timezone.now().date()

    try:
        session = CardGameSession.objects.filter(
            player=profile, played_date=today, completed=False
        ).first()
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if not session:
        return JsonResponse({"status": "no_session"}, status=404)

    if session.current_turn != "player":
        return JsonResponse({"status": "not_your_turn"}, status=400)

    try:
        data = json.loads(request.body)
        card_index = int(data.get("card_index", -1))
        row = int(data.get("row", -1))
        col = int(data.get("col", -1))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

    board = session.board_state

    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return JsonResponse(
            {"status": "error", "message": "Invalid position"}, status=400
        )

    if board[row][col] is not None:
        return JsonResponse({"status": "error", "message": "Cell occupied"}, status=400)

    player_hand = session.player_hand
    if not (0 <= card_index < len(player_hand)):
        return JsonResponse({"status": "error", "message": "Invalid card"}, status=400)

    card = player_hand[card_index]
    if card.get("used"):
        return JsonResponse(
            {"status": "error", "message": "Card already used"}, status=400
        )

    card["used"] = True
    placed = {
        "owner": "player",
        "values": card["values"],
        "name": card["name"],
        "image_url": card.get("image_url", ""),
    }
    board[row][col] = placed

    player_flips = _resolve_flips(board, row, col, "player", card["values"])

    session.moves += 1
    player_card_count = sum(
        1 for r in board for c in r if c and c["owner"] == "player"
    )

    if player_card_count >= CARD_HAND_SIZE:
        session.completed = True
        ai_card_count = sum(
            1 for r in board for c in r if c and c["owner"] == "ai"
        )
        session.won = player_card_count > ai_card_count
        session.current_turn = ""
        session.save(
            update_fields=[
                "board_state", "player_hand", "moves",
                "current_turn", "completed", "won",
            ]
        )
        return JsonResponse({
            "status": "game_over",
            "board": board,
            "player_flips": player_flips,
            "player_card_count": player_card_count,
            "ai_card_count": ai_card_count,
            "won": session.won,
            "reward_gems": session.reward_gems,
        })

    # AI turn
    session.current_turn = "ai"
    session.save(
        update_fields=[
            "board_state", "player_hand", "moves", "current_turn",
        ]
    )

    ai_move = _ai_choose_move(board, session.ai_hand)
    ai_flips: list[dict] = []
    ai_ci: int = -1
    ai_row: int = -1
    ai_col: int = -1
    if ai_move:
        ai_ci, ai_row, ai_col = ai_move
        ai_card = session.ai_hand[ai_ci]
        ai_card["used"] = True
        ai_placed = {
            "owner": "ai",
            "values": ai_card["values"],
            "name": ai_card["name"],
            "image_url": ai_card.get("image_url", ""),
        }
        board[ai_row][ai_col] = ai_placed
        ai_flips = _resolve_flips(board, ai_row, ai_col, "ai", ai_card["values"])
        session.moves += 1

    session.current_turn = "player"
    player_card_count = sum(
        1 for r in board for c in r if c and c["owner"] == "player"
    )
    ai_card_count = sum(
        1 for r in board for c in r if c and c["owner"] == "ai"
    )
    total_filled = sum(1 for r in board for c in r if c is not None)

    if total_filled >= GRID_SIZE * GRID_SIZE:
        session.completed = True
        session.won = player_card_count > ai_card_count
        session.current_turn = ""
        session.save(
            update_fields=[
                "board_state", "player_hand", "ai_hand", "moves",
                "current_turn", "completed", "won",
            ]
        )
        return JsonResponse({
            "status": "game_over",
            "board": board,
            "player_flips": player_flips,
            "ai_flips": ai_flips,
            "ai_move": {"card_index": ai_ci, "row": ai_row, "col": ai_col},
            "player_card_count": player_card_count,
            "ai_card_count": ai_card_count,
            "won": session.won,
            "reward_gems": session.reward_gems,
        })

    session.save(
        update_fields=[
            "board_state", "player_hand", "ai_hand", "moves", "current_turn",
        ]
    )

    return JsonResponse({
        "status": "ok",
        "board": board,
        "player_flips": player_flips,
        "ai_flips": ai_flips,
        "ai_move": {"card_index": ai_ci, "row": ai_row, "col": ai_col},
        "player_card_count": player_card_count,
        "ai_card_count": ai_card_count,
        "current_turn": "player",
    })


@login_required
def card_claim(request):
    """Claim the card duel reward."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        session = CardGameSession.objects.filter(
            player=profile, played_date=timezone.now().date(), completed=True
        ).first()
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if not session:
        return JsonResponse({"status": "no_session"}, status=404)

    gems = session.claim_reward()
    if gems == 0:
        return JsonResponse({"status": "already_claimed"})

    return JsonResponse({"status": "ok", "gems": gems})
