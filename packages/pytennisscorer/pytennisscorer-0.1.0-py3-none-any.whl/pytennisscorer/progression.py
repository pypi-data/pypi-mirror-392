"""Pure functions for set and match progression logic."""

from typing import Literal, Optional

from pytennisscorer.models import GameState, MatchState, ScoringRules, SetState


def is_set_finished(set_state: SetState, rules: ScoringRules, is_final_set: bool) -> bool:
    """
    Check if a set is finished.

    Args:
        set_state: Current set state
        rules: Scoring rules for the match
        is_final_set: Whether this is the final set of the match

    Returns:
        True if the set is finished, False otherwise
    """
    max_score = max(set_state.home_score, set_state.away_score)
    min_score = min(set_state.home_score, set_state.away_score)
    score_diff = max_score - min_score

    # Win at 7-5 (after tiebreak)
    if max_score == 7:
        return True

    # Win at 6 games with 2-game lead
    if max_score >= 6 and score_diff >= 2:
        return True

    return False


def progress_to_next_game(
    set_state: SetState, home_won_game: bool, deciding_point: bool
) -> SetState:
    """
    Progress to the next game in the set.

    Args:
        set_state: Current set state
        home_won_game: Whether home player won the game
        deciding_point: Whether deciding point rule is in effect

    Returns:
        New SetState with updated scores and new game
    """
    # Update set score
    new_home_score = set_state.home_score + (1 if home_won_game else 0)
    new_away_score = set_state.away_score + (0 if home_won_game else 1)

    # Check if next game should be a tiebreak (at 6-6)
    is_tiebreak = new_home_score == 6 and new_away_score == 6

    # Create new game
    new_game = GameState(home_score=0, away_score=0, is_tiebreak=is_tiebreak)

    # Add current game to games history
    new_games = list(set_state.games) + [set_state.current_game]

    return SetState(
        home_score=new_home_score,
        away_score=new_away_score,
        current_game=new_game,
        games=new_games,
    )


def progress_to_next_set(deciding_point: bool) -> SetState:
    """
    Create a new set.

    Args:
        deciding_point: Whether deciding point rule is in effect

    Returns:
        New SetState at 0-0
    """
    new_game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    return SetState(home_score=0, away_score=0, current_game=new_game, games=[])


def check_match_complete(home_sets_won: int, away_sets_won: int, rules: ScoringRules) -> bool:
    """
    Check if a match is complete.

    Args:
        home_sets_won: Number of sets won by home player
        away_sets_won: Number of sets won by away player
        rules: Scoring rules for the match

    Returns:
        True if the match is complete, False otherwise
    """
    max_sets = max(home_sets_won, away_sets_won)
    needed_sets = (rules.best_of + 1) // 2  # Ceiling division

    return max_sets >= needed_sets


def get_match_winner(match: MatchState) -> Optional[Literal["home", "away"]]:
    """
    Get the winner of a match.

    Args:
        match: Current match state

    Returns:
        "home" if home player won, "away" if away player won, None if match not finished
    """
    if not match.is_finished:
        return None

    if match.home_score > match.away_score:
        return "home"
    return "away"
