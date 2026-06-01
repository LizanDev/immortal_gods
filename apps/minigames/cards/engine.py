"""Card game engine — board operations, flip resolution, AI."""

import logging

from apps.minigames.cards.constants import GRID_SIZE

logger = logging.getLogger(__name__)


def make_empty_board() -> list:
    """Create a 3x3 empty board grid."""
    return [[None] * GRID_SIZE for _ in range(GRID_SIZE)]


def _get_opposite(side: str) -> str:
    """Return the opposite direction of a card side."""
    opposites = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}
    return opposites[side]


def resolve_flips(
    board: list, row: int, col: int, owner: str, values: dict
) -> list[dict]:
    """Check 4 adjacent cells and return which opponent cards would flip.

    Does NOT modify the board. Caller must apply flips explicitly.

    Args:
        board: 3x3 grid of cell data or None.
        row: Row index of the placed card.
        col: Column index of the placed card.
        owner: "player" or "ai".
        values: Dict with top/right/bottom/left card values.

    Returns:
        List of flip dicts with keys: row, col, card.
    """
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
                    flips.append({"row": r, "col": c, "card": cell})
    return flips


def apply_flips(flips: list[dict], owner: str) -> None:
    """Apply ownership changes to flipped cells.

    Args:
        flips: List of flip dicts from resolve_flips.
        owner: New owner ("player" or "ai").
    """
    for flip in flips:
        flip["card"]["owner"] = owner


def ai_choose_move(board: list, ai_hand: list) -> tuple[int, int, int] | None:
    """AI picks the best card and position.

    Evaluates all unused cards against all empty cells.
    Scores by number of flips, with center preference as tiebreaker.

    Args:
        board: 3x3 grid of cell data or None.
        ai_hand: List of AI card dicts.

    Returns:
        Tuple of (card_index, row, col) or None if no move.
    """
    best_score = -1
    best_move = None

    for ci, card in enumerate(ai_hand):
        if card.get("used"):
            continue
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] is not None:
                    continue
                flips = resolve_flips(board, r, c, "ai", card["values"])
                score = len(flips)
                if score == 0:
                    if (r, c) == (1, 1):
                        score = 1
                    elif (r, c) in {(0, 0), (0, 2), (2, 0), (2, 2)}:
                        score = 0
                if score > best_score:
                    best_score = score
                    best_move = (ci, r, c)

    return best_move
