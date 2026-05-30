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

from .models import DailyWheelSpin, MemoryGameSession

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
        best_score = (
            MemoryGameSession.objects.filter(player=profile, completed=True)
            .order_by("moves")
            .first()
        )
    except DatabaseError:
        today_memory = None
        today_wheel = None
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
