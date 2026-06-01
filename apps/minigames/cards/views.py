"""Card duel views (Triple Triad-style)."""

import json
import logging
import random

from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.gods.models import God
from apps.minigames.card_utils import rarity_card_values
from apps.minigames.cards.constants import CARD_HAND_SIZE, GRID_SIZE, UNAVAILABLE
from apps.minigames.cards.engine import (
    ai_choose_move,
    apply_flips,
    make_empty_board,
    resolve_flips,
)
from apps.minigames.cards.utils import god_to_ai_card, god_to_player_card
from apps.minigames.models import CardGameSession

logger = logging.getLogger(__name__)


@login_required
def card_game(request):
    """Card duel game page — always starts a new game (unlimited plays)."""
    profile = request.user.profile
    deck_ids = profile.card_deck
    if not deck_ids:
        return redirect("minigames:card_deck")

    picked = _pick_player_deck(profile, deck_ids)
    if len(picked) < CARD_HAND_SIZE:
        return _render_card_error(request, CARD_HAND_SIZE)

    player_hand = [god_to_player_card(pg) for pg in picked]
    ai_hand = _build_ai_hand()

    try:
        session = CardGameSession.objects.create(
            player=profile,
            played_date=timezone.now().date(),
            board_state=make_empty_board(),
            player_hand=player_hand,
            ai_hand=ai_hand,
        )
    except DatabaseError:
        msg = "Error de base de datos. Intenta de nuevo."
        return render(request, "minigames/card.html", {"error": msg})

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


def _pick_player_deck(profile, deck_ids: list) -> list:
    """Select gods for the player's hand from their deck."""
    if len(deck_ids) >= CARD_HAND_SIZE:
        picked = list(
            profile.gods.select_related("god").filter(
                id__in=deck_ids[:CARD_HAND_SIZE], god__isnull=False
            )
        )
        if len(picked) < CARD_HAND_SIZE:
            picked = list(profile.gods.select_related("god").filter(god__isnull=False))
            random.shuffle(picked)
            picked = picked[:CARD_HAND_SIZE]
    else:
        picked = list(profile.gods.select_related("god").filter(god__isnull=False))
        random.shuffle(picked)
        picked = picked[:CARD_HAND_SIZE]
    return picked


def _build_ai_hand() -> list:
    """Build a random hand of 6 gods for the AI."""
    all_gods = list(God.objects.all())
    random.shuffle(all_gods)
    ai_gods = all_gods[:CARD_HAND_SIZE]
    return [god_to_ai_card(g) for g in ai_gods]


def _render_card_error(request, required: int):
    """Render error page when player lacks enough gods."""
    msg = f"Necesitas al menos {required} dioses para jugar al Duelo de Cartas."
    return render(request, "minigames/card.html", {"error": msg})


@login_required
def card_place(request):
    """Place a card on the board (player turn), then AI responds."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        session = (
            CardGameSession.objects.filter(player=profile, completed=False)
            .order_by("-created_at")
            .first()
        )
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if not session:
        return JsonResponse({"status": "no_session"}, status=404)

    if session.current_turn != "player":
        return JsonResponse({"status": "not_your_turn"}, status=400)

    result = _validate_card_request(request, session)
    if isinstance(result, JsonResponse):
        return result

    board, card_index, row, col = result
    card = session.player_hand[card_index]

    _place_player_card(board, card, row, col)
    player_flips = resolve_flips(board, row, col, "player", card["values"])
    apply_flips(player_flips, "player")
    session.moves += 1

    player_count = _count_owner(board, "player")
    if player_count >= CARD_HAND_SIZE:
        return _finish_game(session, board, player_flips, [])

    session.current_turn = "ai"
    session.save(update_fields=["board_state", "player_hand", "moves", "current_turn"])

    ai_ci, ai_row, ai_col, ai_flips = _process_ai_turn(session, board)

    return _build_turn_response(
        session, board, player_flips, ai_flips, ai_ci, ai_row, ai_col
    )


def _validate_card_request(request, session):
    """Parse and validate card placement request data.

    Returns (board, card_index, row, col) or JsonResponse on error.
    """
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

    if player_hand[card_index].get("used"):
        return JsonResponse(
            {"status": "error", "message": "Card already used"}, status=400
        )

    return board, card_index, row, col


def _place_player_card(board, card, row, col):
    """Place player's card on the board and mark as used."""
    card["used"] = True
    board[row][col] = {
        "owner": "player",
        "values": card["values"],
        "name": card["name"],
        "image_url": card.get("image_url", ""),
    }


def _count_owner(board, owner: str) -> int:
    """Count cells owned by a player on the board."""
    return sum(1 for r in board for c in r if c and c["owner"] == owner)


def _process_ai_turn(session, board):
    """Execute AI turn: choose move, place card, resolve flips.

    Returns (ai_ci, ai_row, ai_col, ai_flips).
    """
    ai_move = ai_choose_move(board, session.ai_hand)
    ai_flips: list[dict] = []
    ai_ci, ai_row, ai_col = -1, -1, -1

    if ai_move:
        ai_ci, ai_row, ai_col = ai_move
        ai_card = session.ai_hand[ai_ci]
        ai_card["used"] = True
        board[ai_row][ai_col] = {
            "owner": "ai",
            "values": ai_card["values"],
            "name": ai_card["name"],
            "image_url": ai_card.get("image_url", ""),
        }
        ai_flips = resolve_flips(board, ai_row, ai_col, "ai", ai_card["values"])
        apply_flips(ai_flips, "ai")
        session.moves += 1

    return ai_ci, ai_row, ai_col, ai_flips


def _finish_game(session, board, player_flips, ai_flips):
    """Mark game as finished and return game over response."""
    session.completed = True
    player_count = _count_owner(board, "player")
    ai_count = _count_owner(board, "ai")
    session.won = player_count > ai_count
    session.current_turn = ""
    session.save(
        update_fields=[
            "board_state",
            "player_hand",
            "moves",
            "current_turn",
            "completed",
            "won",
        ]
    )
    return JsonResponse({
        "status": "game_over",
        "board": board,
        "player_flips": player_flips,
        "player_card_count": player_count,
        "ai_card_count": ai_count,
        "won": session.won,
        "reward_gems": session.reward_gems,
    })


def _build_turn_response(session, board, player_flips, ai_flips, ai_ci, ai_row, ai_col):
    """Build response for a non-final turn."""
    player_count = _count_owner(board, "player")
    ai_count = _count_owner(board, "ai")
    total_filled = sum(1 for r in board for c in r if c is not None)

    if total_filled >= GRID_SIZE * GRID_SIZE:
        return _finish_game(session, board, player_flips, ai_flips)

    session.current_turn = "player"
    session.save(
        update_fields=[
            "board_state",
            "player_hand",
            "ai_hand",
            "moves",
            "current_turn",
        ]
    )

    return JsonResponse({
        "status": "ok",
        "board": board,
        "player_flips": player_flips,
        "ai_flips": ai_flips,
        "ai_move": {"card_index": ai_ci, "row": ai_row, "col": ai_col},
        "player_card_count": player_count,
        "ai_card_count": ai_count,
        "current_turn": "player",
    })


@login_required
def card_claim(request):
    """Claim the card duel reward."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        session = (
            CardGameSession.objects.filter(
                player=profile, completed=True, reward_claimed=False
            )
            .order_by("-created_at")
            .first()
        )
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)

    if not session:
        return JsonResponse({"status": "no_session"}, status=404)

    gems = session.claim_reward()
    if gems == 0:
        return JsonResponse({"status": "already_claimed"})

    return JsonResponse({"status": "ok", "gems": gems})


@login_required
def card_deck(request):
    """Edit the player's card duel deck (select up to 6 gods)."""
    profile = request.user.profile

    if request.method == "POST":
        return _save_deck(request, profile)

    return _render_deck(request, profile)


def _save_deck(request, profile):
    """Handle POST to save deck selection."""
    try:
        data = json.loads(request.body)
        god_ids = data.get("god_ids", [])
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

    if len(god_ids) > CARD_HAND_SIZE:
        return JsonResponse(
            {"status": "error", "message": f"Máximo {CARD_HAND_SIZE} dioses"},
            status=400,
        )

    owned = set(profile.gods.filter(id__in=god_ids).values_list("id", flat=True))
    valid_ids = [gid for gid in god_ids if gid in owned]
    profile.card_deck = valid_ids
    profile.save(update_fields=["card_deck"])
    return JsonResponse({"status": "ok", "deck": valid_ids})


def _render_deck(request, profile):
    """Render deck editor page with god cards and values."""
    owned_gods = list(profile.gods.select_related("god").order_by("-level"))
    deck_ids = list(profile.card_deck)

    gods_with_values = []
    for pg in owned_gods:
        gods_with_values.append({
            "pg": pg,
            "card_values": rarity_card_values(pg.god.rarity, pg.card_bonus),
        })

    return render(
        request,
        "minigames/deck.html",
        {"gods": gods_with_values, "deck_ids": deck_ids, "max_cards": CARD_HAND_SIZE},
    )


@login_required
def card_allocate_bonus(request):
    """Allocate a card bonus point for a specific god's direction."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    profile = request.user.profile

    try:
        data = json.loads(request.body)
        pg_id = data.get("pg_id")
        direction = data.get("direction")
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid data"}, status=400)

    if direction not in ("top", "right", "bottom", "left"):
        return JsonResponse(
            {"status": "error", "message": "Invalid direction"}, status=400
        )

    try:
        pg = profile.gods.select_related("god").get(id=pg_id)
    except DatabaseError:
        return JsonResponse(UNAVAILABLE, status=503)
    except profile.gods.model.DoesNotExist:
        return JsonResponse({"status": "error", "message": "God not found"}, status=404)

    if pg.card_points_available <= 0:
        return JsonResponse(
            {"status": "error", "message": "No points available"}, status=400
        )

    bonus = dict(pg.card_bonus)
    bonus[direction] = bonus.get(direction, 0) + 1
    pg.card_bonus = bonus
    pg.save(update_fields=["card_bonus"])

    new_value = rarity_card_values(pg.god.rarity, bonus)[direction]

    return JsonResponse({
        "status": "ok",
        "new_value": new_value,
        "available": pg.card_points_available,
        "total_bonus": bonus[direction],
    })
