"""Tests for set and match progression logic."""

import pytest

from pytennisscorer.models import GameState, MatchState, MatchType, ScoringRules, SetState
from pytennisscorer.progression import (
    check_match_complete,
    get_match_winner,
    is_set_finished,
    progress_to_next_game,
    progress_to_next_set,
)


@pytest.mark.unit
def test_is_set_finished_at_6_0() -> None:
    """Test that 6-0 wins the set."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=6, away_score=0, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert is_set_finished(set_state, rules, is_final_set=False) is True


@pytest.mark.unit
def test_is_set_finished_at_6_4() -> None:
    """Test that 6-4 wins the set (2-game lead)."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=6, away_score=4, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert is_set_finished(set_state, rules, is_final_set=False) is True


@pytest.mark.unit
def test_is_set_finished_not_at_6_5() -> None:
    """Test that 6-5 does not win (needs 2-game lead)."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=6, away_score=5, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert is_set_finished(set_state, rules, is_final_set=False) is False


@pytest.mark.unit
def test_is_set_finished_at_7_5_after_tiebreak() -> None:
    """Test that 7-5 wins the set after tiebreak."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=7, away_score=5, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert is_set_finished(set_state, rules, is_final_set=False) is True


@pytest.mark.unit
def test_is_set_finished_not_at_0_0() -> None:
    """Test that set at 0-0 is not finished."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=0, away_score=0, current_game=game, games=[])
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert is_set_finished(set_state, rules, is_final_set=False) is False


@pytest.mark.unit
def test_progress_to_next_game_creates_new_game() -> None:
    """Test that progressing to next game creates a fresh game."""
    game = GameState(home_score=4, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=0, away_score=0, current_game=game, games=[])
    new_set = progress_to_next_game(set_state, home_won_game=True, deciding_point=False)

    assert new_set.home_score == 1
    assert new_set.away_score == 0
    assert new_set.current_game.home_score == 0
    assert new_set.current_game.away_score == 0
    assert len(new_set.games) == 1


@pytest.mark.unit
def test_progress_to_next_game_creates_tiebreak_at_6_6() -> None:
    """Test that at 6-6, next game is a tiebreak."""
    game = GameState(home_score=4, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=6, away_score=5, current_game=game, games=[])
    new_set = progress_to_next_game(set_state, home_won_game=False, deciding_point=False)

    assert new_set.home_score == 6
    assert new_set.away_score == 6
    assert new_set.current_game.is_tiebreak is True


@pytest.mark.unit
def test_check_match_complete_best_of_3_at_2_0() -> None:
    """Test that best of 3 match is complete at 2-0."""
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert check_match_complete(home_sets_won=2, away_sets_won=0, rules=rules) is True


@pytest.mark.unit
def test_check_match_complete_best_of_3_at_2_1() -> None:
    """Test that best of 3 match is complete at 2-1."""
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert check_match_complete(home_sets_won=2, away_sets_won=1, rules=rules) is True


@pytest.mark.unit
def test_check_match_complete_best_of_3_not_at_1_1() -> None:
    """Test that best of 3 match is not complete at 1-1."""
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert check_match_complete(home_sets_won=1, away_sets_won=1, rules=rules) is False


@pytest.mark.unit
def test_check_match_complete_best_of_5_at_3_0() -> None:
    """Test that best of 5 match is complete at 3-0."""
    rules = ScoringRules(
        best_of=5,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert check_match_complete(home_sets_won=3, away_sets_won=0, rules=rules) is True


@pytest.mark.unit
def test_check_match_complete_best_of_5_at_3_2() -> None:
    """Test that best of 5 match is complete at 3-2."""
    rules = ScoringRules(
        best_of=5,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert check_match_complete(home_sets_won=3, away_sets_won=2, rules=rules) is True


@pytest.mark.unit
def test_check_match_complete_best_of_5_not_at_2_2() -> None:
    """Test that best of 5 match is not complete at 2-2."""
    rules = ScoringRules(
        best_of=5,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert check_match_complete(home_sets_won=2, away_sets_won=2, rules=rules) is False


@pytest.mark.unit
def test_get_match_winner_home_wins() -> None:
    """Test getting winner when home wins."""
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
        home_score=2,
        away_score=0,
        current_set_index=0,
        sets=[set_state],
        is_finished=True,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    assert get_match_winner(match) == "home"


@pytest.mark.unit
def test_get_match_winner_away_wins() -> None:
    """Test getting winner when away wins."""
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
        away_score=2,
        current_set_index=0,
        sets=[set_state],
        is_finished=True,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    assert get_match_winner(match) == "away"


@pytest.mark.unit
def test_get_match_winner_returns_none_when_not_finished() -> None:
    """Test that winner is None when match is not finished."""
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
        home_score=1,
        away_score=1,
        current_set_index=0,
        sets=[set_state],
        is_finished=False,
        match_type=MatchType.DOUBLES_DAVISCUP,
        rules=rules,
    )

    assert get_match_winner(match) is None


@pytest.mark.unit
def test_progress_to_next_set_creates_new_set() -> None:
    """Test that progressing to next set creates a fresh set."""
    new_set = progress_to_next_set(deciding_point=False)

    assert new_set.home_score == 0
    assert new_set.away_score == 0
    assert new_set.current_game.home_score == 0
    assert new_set.current_game.away_score == 0
    assert new_set.current_game.is_tiebreak is False
    assert len(new_set.games) == 0
