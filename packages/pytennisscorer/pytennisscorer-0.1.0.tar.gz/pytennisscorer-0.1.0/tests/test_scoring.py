"""Tests for point scoring logic."""

import pytest

from pytennisscorer.models import GameState
from pytennisscorer.scoring import is_game_finished, score_game_point


@pytest.mark.unit
def test_score_game_point_from_love_all_home_wins() -> None:
    """Test scoring first point for home player from 0-0."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    new_game = score_game_point(game, is_home=True, deciding_point=False)
    assert new_game.home_score == 1
    assert new_game.away_score == 0


@pytest.mark.unit
def test_score_game_point_from_love_all_away_wins() -> None:
    """Test scoring first point for away player from 0-0."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    new_game = score_game_point(game, is_home=False, deciding_point=False)
    assert new_game.home_score == 0
    assert new_game.away_score == 1


@pytest.mark.unit
def test_score_game_point_progression_to_40() -> None:
    """Test standard progression: 0->15->30->40."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)

    # Home: 0 -> 15
    game = score_game_point(game, is_home=True, deciding_point=False)
    assert game.home_score == 1  # Internal: 1 = 15

    # Home: 15 -> 30
    game = score_game_point(game, is_home=True, deciding_point=False)
    assert game.home_score == 2  # Internal: 2 = 30

    # Home: 30 -> 40
    game = score_game_point(game, is_home=True, deciding_point=False)
    assert game.home_score == 3  # Internal: 3 = 40


@pytest.mark.unit
def test_score_game_point_wins_at_40_love() -> None:
    """Test that scoring at 40-0 wins the game."""
    game = GameState(home_score=3, away_score=0, is_tiebreak=False)
    new_game = score_game_point(game, is_home=True, deciding_point=False)
    assert new_game.home_score == 4  # Internal: 4 = Game won
    assert is_game_finished(new_game, deciding_point=False) is True


@pytest.mark.unit
def test_score_game_point_deuce_at_40_40() -> None:
    """Test that 40-40 is deuce (both at 3)."""
    game = GameState(home_score=3, away_score=3, is_tiebreak=False)
    assert is_game_finished(game, deciding_point=False) is False


@pytest.mark.unit
def test_score_game_point_from_deuce_to_advantage() -> None:
    """Test scoring from deuce (40-40) gives advantage."""
    game = GameState(home_score=3, away_score=3, is_tiebreak=False)
    new_game = score_game_point(game, is_home=True, deciding_point=False)
    assert new_game.home_score == 4  # Internal: 4 = Advantage
    assert new_game.away_score == 3
    assert is_game_finished(new_game, deciding_point=False) is False


@pytest.mark.unit
def test_score_game_point_advantage_to_game() -> None:
    """Test winning from advantage."""
    game = GameState(home_score=4, away_score=3, is_tiebreak=False)
    new_game = score_game_point(game, is_home=True, deciding_point=False)
    assert new_game.home_score == 5  # Internal: 5 = Game won
    assert is_game_finished(new_game, deciding_point=False) is True


@pytest.mark.unit
def test_score_game_point_advantage_back_to_deuce() -> None:
    """Test that losing advantage returns to deuce."""
    game = GameState(home_score=4, away_score=3, is_tiebreak=False)
    new_game = score_game_point(game, is_home=False, deciding_point=False)
    assert new_game.home_score == 3  # Back to deuce
    assert new_game.away_score == 3


@pytest.mark.unit
def test_score_game_point_deciding_point_wins_at_deuce() -> None:
    """Test that with deciding point rule, deuce immediately wins on next point."""
    game = GameState(home_score=3, away_score=3, is_tiebreak=False)
    new_game = score_game_point(game, is_home=True, deciding_point=True)
    assert new_game.home_score == 4
    assert is_game_finished(new_game, deciding_point=True) is True


@pytest.mark.unit
def test_is_game_finished_at_love() -> None:
    """Test that game at 0-0 is not finished."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    assert is_game_finished(game, deciding_point=False) is False


@pytest.mark.unit
def test_is_game_finished_with_2_point_lead() -> None:
    """Test game is won with score >= 4 and 2-point lead."""
    # 4-2 should be finished
    game = GameState(home_score=4, away_score=2, is_tiebreak=False)
    assert is_game_finished(game, deciding_point=False) is True

    # 5-3 should be finished
    game = GameState(home_score=5, away_score=3, is_tiebreak=False)
    assert is_game_finished(game, deciding_point=False) is True


@pytest.mark.unit
def test_score_game_point_does_not_modify_finished_game() -> None:
    """Test that scoring a point on a finished game returns the same state."""
    game = GameState(home_score=4, away_score=0, is_tiebreak=False)
    new_game = score_game_point(game, is_home=True, deciding_point=False)
    # Should not change since game is already finished
    assert new_game == game
