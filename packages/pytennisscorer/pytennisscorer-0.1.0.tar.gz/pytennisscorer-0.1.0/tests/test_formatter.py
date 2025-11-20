"""Tests for score formatting and parsing."""

import pytest

from pytennisscorer.formatter import format_game_score, format_match_score
from pytennisscorer.models import GameState, MatchState, MatchType, ScoringRules, SetState


@pytest.mark.unit
def test_format_game_score_love_all() -> None:
    """Test formatting 0-0 as love-all."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    assert format_game_score(game) == "0:0"


@pytest.mark.unit
def test_format_game_score_15_love() -> None:
    """Test formatting 15-0."""
    game = GameState(home_score=1, away_score=0, is_tiebreak=False)
    assert format_game_score(game) == "15:0"


@pytest.mark.unit
def test_format_game_score_30_15() -> None:
    """Test formatting 30-15."""
    game = GameState(home_score=2, away_score=1, is_tiebreak=False)
    assert format_game_score(game) == "30:15"


@pytest.mark.unit
def test_format_game_score_40_30() -> None:
    """Test formatting 40-30."""
    game = GameState(home_score=3, away_score=2, is_tiebreak=False)
    assert format_game_score(game) == "40:30"


@pytest.mark.unit
def test_format_game_score_deuce() -> None:
    """Test formatting deuce (40-40)."""
    game = GameState(home_score=3, away_score=3, is_tiebreak=False)
    assert format_game_score(game) == "40:40"


@pytest.mark.unit
def test_format_game_score_advantage_home() -> None:
    """Test formatting advantage for home."""
    game = GameState(home_score=4, away_score=3, is_tiebreak=False)
    assert format_game_score(game) == "Ad:40"


@pytest.mark.unit
def test_format_game_score_advantage_away() -> None:
    """Test formatting advantage for away."""
    game = GameState(home_score=3, away_score=4, is_tiebreak=False)
    assert format_game_score(game) == "40:Ad"


@pytest.mark.unit
def test_format_game_score_tiebreak() -> None:
    """Test formatting tiebreak scores as numbers."""
    game = GameState(home_score=5, away_score=3, is_tiebreak=True)
    assert format_game_score(game) == "5:3"


@pytest.mark.unit
def test_format_match_score_start_of_match() -> None:
    """Test formatting score at start of match."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=0, away_score=0, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    match = MatchState(
        home_score=0,
        away_score=0,
        current_set_index=0,
        sets=[set_state],
        is_finished=False,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    assert format_match_score(match) == "0:0-0:0"


@pytest.mark.unit
def test_format_match_score_during_first_set() -> None:
    """Test formatting score during first set."""
    game = GameState(home_score=2, away_score=1, is_tiebreak=False)
    set_state = SetState(home_score=3, away_score=2, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    match = MatchState(
        home_score=0,
        away_score=0,
        current_set_index=0,
        sets=[set_state],
        is_finished=False,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    assert format_match_score(match) == "3:2-30:15"


@pytest.mark.unit
def test_format_match_score_multiple_sets() -> None:
    """Test formatting score across multiple sets."""
    game1 = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set1 = SetState(home_score=6, away_score=4, current_game=game1, games=[])

    game2 = GameState(home_score=1, away_score=2, is_tiebreak=False)
    set2 = SetState(home_score=2, away_score=3, current_game=game2, games=[])

    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    match = MatchState(
        home_score=1,
        away_score=0,
        current_set_index=1,
        sets=[set1, set2],
        is_finished=False,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    assert format_match_score(match) == "6:4;2:3-15:30"


@pytest.mark.unit
def test_format_match_score_finished_match() -> None:
    """Test formatting score for finished match."""
    game1 = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set1 = SetState(home_score=6, away_score=4, current_game=game1, games=[])

    game2 = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set2 = SetState(home_score=6, away_score=2, current_game=game2, games=[])

    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    match = MatchState(
        home_score=2,
        away_score=0,
        current_set_index=1,
        sets=[set1, set2],
        is_finished=True,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    # Finished match shows only set scores
    assert format_match_score(match) == "6:4;6:2"
