"""Pure functions for formatting and parsing tennis scores."""

from pytennisscorer.models import GameState, MatchState

# Mapping for displaying game points in tennis notation
GAME_POINT_DISPLAY = {
    0: "0",
    1: "15",
    2: "30",
    3: "40",
    4: "Ad",
}


def format_game_score(game: GameState) -> str:
    """
    Format a game score in tennis notation.

    Args:
        game: Current game state

    Returns:
        Formatted score string (e.g., "30:15", "40:Ad", "5:3" for tiebreak)
    """
    if game.is_tiebreak:
        # Tiebreak uses numeric scoring
        return f"{game.home_score}:{game.away_score}"

    # Regular game uses tennis notation
    home_display = GAME_POINT_DISPLAY.get(game.home_score, str(game.home_score))
    away_display = GAME_POINT_DISPLAY.get(game.away_score, str(game.away_score))

    return f"{home_display}:{away_display}"


def format_match_score(match: MatchState) -> str:
    """
    Format a complete match score.

    Format: "SetScore;SetScore-GameScore" or just "SetScore;SetScore" if finished

    Args:
        match: Current match state

    Returns:
        Formatted match score string (e.g., "6:4;3:6;2:2-30:15")
    """
    set_scores = []

    # Format each set up to and including current set
    for i, set_state in enumerate(match.sets):
        if i > match.current_set_index:
            break

        set_score = f"{set_state.home_score}:{set_state.away_score}"
        set_scores.append(set_score)

    # Join all set scores
    result = ";".join(set_scores)

    # If match is not finished, append current game score
    if not match.is_finished:
        current_set = match.sets[match.current_set_index]
        game_score = format_game_score(current_set.current_game)
        result = f"{result}-{game_score}"

    return result
