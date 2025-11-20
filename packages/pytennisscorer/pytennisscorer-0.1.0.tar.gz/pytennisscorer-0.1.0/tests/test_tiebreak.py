"""Tests for tiebreak scoring logic."""

import pytest

from pytennisscorer.models import GameState
from pytennisscorer.scoring import is_game_finished, score_tiebreak_point


@pytest.mark.unit
def test_score_tiebreak_point_from_zero_zero_home_wins() -> None:
    """Test scoring first point in tiebreak for home player."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=True, tiebreak_points=7)
    assert new_game.home_score == 1
    assert new_game.away_score == 0


@pytest.mark.unit
def test_score_tiebreak_point_from_zero_zero_away_wins() -> None:
    """Test scoring first point in tiebreak for away player."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=False, tiebreak_points=7)
    assert new_game.home_score == 0
    assert new_game.away_score == 1


@pytest.mark.unit
def test_score_tiebreak_point_regular_tiebreak_wins_at_7_0() -> None:
    """Test that 7-0 wins in regular tiebreak."""
    game = GameState(home_score=6, away_score=0, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=True, tiebreak_points=7)
    assert new_game.home_score == 7
    assert is_game_finished(new_game, deciding_point=False, tiebreak_points=7) is True


@pytest.mark.unit
def test_score_tiebreak_point_regular_tiebreak_wins_at_7_5() -> None:
    """Test that 7-5 wins in regular tiebreak (2-point margin)."""
    game = GameState(home_score=6, away_score=5, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=True, tiebreak_points=7)
    assert new_game.home_score == 7
    assert is_game_finished(new_game, deciding_point=False, tiebreak_points=7) is True


@pytest.mark.unit
def test_score_tiebreak_point_regular_tiebreak_continues_at_7_6() -> None:
    """Test that 7-6 does not win (needs 2-point margin)."""
    game = GameState(home_score=7, away_score=6, is_tiebreak=True)
    assert is_game_finished(game, deciding_point=False, tiebreak_points=7) is False


@pytest.mark.unit
def test_score_tiebreak_point_regular_tiebreak_wins_at_8_6() -> None:
    """Test that 8-6 wins in regular tiebreak (2-point margin)."""
    game = GameState(home_score=8, away_score=6, is_tiebreak=True)
    assert is_game_finished(game, deciding_point=False, tiebreak_points=7) is True


@pytest.mark.unit
def test_score_tiebreak_point_match_tiebreak_wins_at_10_0() -> None:
    """Test that 10-0 wins in match tiebreak."""
    game = GameState(home_score=9, away_score=0, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=True, tiebreak_points=10)
    assert new_game.home_score == 10
    assert is_game_finished(new_game, deciding_point=False, tiebreak_points=10) is True


@pytest.mark.unit
def test_score_tiebreak_point_match_tiebreak_wins_at_10_8() -> None:
    """Test that 10-8 wins in match tiebreak (2-point margin)."""
    game = GameState(home_score=9, away_score=8, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=True, tiebreak_points=10)
    assert new_game.home_score == 10
    assert is_game_finished(new_game, deciding_point=False, tiebreak_points=10) is True


@pytest.mark.unit
def test_score_tiebreak_point_match_tiebreak_continues_at_10_9() -> None:
    """Test that 10-9 does not win (needs 2-point margin)."""
    game = GameState(home_score=10, away_score=9, is_tiebreak=True)
    assert is_game_finished(game, deciding_point=False, tiebreak_points=10) is False


@pytest.mark.unit
def test_score_tiebreak_point_match_tiebreak_wins_at_11_9() -> None:
    """Test that 11-9 wins in match tiebreak (2-point margin)."""
    game = GameState(home_score=11, away_score=9, is_tiebreak=True)
    assert is_game_finished(game, deciding_point=False, tiebreak_points=10) is True


@pytest.mark.unit
def test_score_tiebreak_point_does_not_modify_finished_tiebreak() -> None:
    """Test that scoring on a finished tiebreak returns same state."""
    game = GameState(home_score=7, away_score=5, is_tiebreak=True)
    new_game = score_tiebreak_point(game, is_home=True, tiebreak_points=7)
    # Should not change since tiebreak is already finished
    assert new_game == game


@pytest.mark.unit
def test_is_game_finished_tiebreak_requires_tiebreak_points_parameter() -> None:
    """Test that is_game_finished works correctly for tiebreaks."""
    # Regular tiebreak
    game = GameState(home_score=7, away_score=5, is_tiebreak=True)
    assert is_game_finished(game, deciding_point=False, tiebreak_points=7) is True

    # Match tiebreak
    game = GameState(home_score=10, away_score=8, is_tiebreak=True)
    assert is_game_finished(game, deciding_point=False, tiebreak_points=10) is True
