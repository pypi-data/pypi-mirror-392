"""Pure functions for tennis point scoring logic."""

from dataclasses import replace
from typing import Optional

from pytennisscorer.models import GameState


def is_game_finished(
    game: GameState, deciding_point: bool, tiebreak_points: Optional[int] = None
) -> bool:
    """
    Check if a game is finished.

    Args:
        game: Current game state
        deciding_point: Whether deciding point rule is in effect
        tiebreak_points: Points required to win tiebreak (7 or 10), required if is_tiebreak

    Returns:
        True if the game is finished, False otherwise
    """
    if game.is_tiebreak:
        if tiebreak_points is None:
            raise ValueError("tiebreak_points required when game.is_tiebreak is True")

        max_score = max(game.home_score, game.away_score)
        min_score = min(game.home_score, game.away_score)
        score_diff = max_score - min_score

        # Win tiebreak with score >= tiebreak_points and 2-point lead
        if max_score >= tiebreak_points and score_diff >= 2:
            return True
        return False

    max_score = max(game.home_score, game.away_score)
    min_score = min(game.home_score, game.away_score)
    score_diff = max_score - min_score

    # Win with 2-point lead when score >= 4
    if max_score >= 4 and score_diff >= 2:
        return True

    # Deciding point: win at 40-Ad (score 4 when opponent at 3)
    if deciding_point and max_score == 4 and min_score == 3:
        return True

    return False


def score_game_point(game: GameState, is_home: bool, deciding_point: bool) -> GameState:
    """
    Score a point in a game and return new game state.

    Internal score mapping:
    - 0 = 0 (love)
    - 1 = 15
    - 2 = 30
    - 3 = 40
    - 4 = Advantage (or game if conditions met)
    - 5 = Game won

    Args:
        game: Current game state
        is_home: True if home player scores, False if away player scores
        deciding_point: Whether deciding point rule is in effect

    Returns:
        New GameState with updated scores
    """
    # Don't modify if game is already finished
    if is_game_finished(game, deciding_point):
        return game

    if is_home:
        new_home_score = game.home_score + 1
        new_away_score = game.away_score
    else:
        new_home_score = game.home_score
        new_away_score = game.away_score + 1

    # Handle advantage/deuce logic (when both reach 40 or Ad)
    if new_home_score == 4 and new_away_score == 4:
        # Both at advantage - reset to deuce
        new_home_score = 3
        new_away_score = 3

    return replace(game, home_score=new_home_score, away_score=new_away_score)


def score_tiebreak_point(game: GameState, is_home: bool, tiebreak_points: int) -> GameState:
    """
    Score a point in a tiebreak and return new game state.

    Args:
        game: Current game state (must have is_tiebreak=True)
        is_home: True if home player scores, False if away player scores
        tiebreak_points: Points required to win tiebreak (7 for regular, 10 for match)

    Returns:
        New GameState with updated scores
    """
    # Don't modify if tiebreak is already finished
    if is_game_finished(game, deciding_point=False, tiebreak_points=tiebreak_points):
        return game

    if is_home:
        new_home_score = game.home_score + 1
        new_away_score = game.away_score
    else:
        new_home_score = game.home_score
        new_away_score = game.away_score + 1

    return replace(game, home_score=new_home_score, away_score=new_away_score)
