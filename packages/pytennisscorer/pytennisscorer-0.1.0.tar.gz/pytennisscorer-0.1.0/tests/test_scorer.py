"""Tests for main TennisScorer API."""

import pytest

from pytennisscorer.models import MatchType
from pytennisscorer.scorer import TennisScorer


@pytest.mark.unit
def test_tennis_scorer_initialization() -> None:
    """Test that TennisScorer can be initialized with a match type."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)
    assert scorer.get_score() == "0:0-0:0"


@pytest.mark.unit
def test_increase_score_home_player() -> None:
    """Test scoring a point for home player."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)
    scorer.increase_score(is_home=True)
    assert scorer.get_score() == "0:0-15:0"


@pytest.mark.unit
def test_increase_score_away_player() -> None:
    """Test scoring a point for away player."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)
    scorer.increase_score(is_home=False)
    assert scorer.get_score() == "0:0-0:15"


@pytest.mark.unit
def test_increase_score_progresses_through_game() -> None:
    """Test that scoring progresses through a complete game."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)

    # Score 4 points for home to win game
    for _ in range(4):
        scorer.increase_score(is_home=True)

    # Should be 1-0 in games, 0-0 in new game
    assert scorer.get_score() == "1:0-0:0"


@pytest.mark.unit
def test_increase_score_progresses_through_set() -> None:
    """Test that scoring progresses through a complete set."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)

    # Win 6 games for home (4 points each)
    for _ in range(6):
        for _ in range(4):
            scorer.increase_score(is_home=True)

    # Should be in second set
    assert scorer.get_score() == "6:0;0:0-0:0"


@pytest.mark.unit
def test_get_winner_returns_none_when_not_finished() -> None:
    """Test that get_winner returns None when match is ongoing."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)
    assert scorer.get_winner() is None


@pytest.mark.unit
def test_get_winner_returns_home_when_home_wins() -> None:
    """Test that get_winner returns 'home' when home wins."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)

    # Win 2 sets for home (best of 3)
    for _ in range(2):
        for _ in range(6):
            for _ in range(4):
                scorer.increase_score(is_home=True)

    assert scorer.get_winner() == "home"


@pytest.mark.unit
def test_undo_reverts_last_point() -> None:
    """Test that undo reverts the last scored point."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)

    scorer.increase_score(is_home=True)
    assert scorer.get_score() == "0:0-15:0"

    scorer.undo()
    assert scorer.get_score() == "0:0-0:0"


@pytest.mark.unit
def test_undo_returns_false_at_match_start() -> None:
    """Test that undo returns False when there's no history."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)
    result = scorer.undo()
    assert result is False


@pytest.mark.unit
def test_undo_returns_true_when_successful() -> None:
    """Test that undo returns True when successful."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)
    scorer.increase_score(is_home=True)
    result = scorer.undo()
    assert result is True


@pytest.mark.unit
def test_cannot_score_on_finished_match() -> None:
    """Test that scoring on a finished match does nothing."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)

    # Win 2 sets for home
    for _ in range(2):
        for _ in range(6):
            for _ in range(4):
                scorer.increase_score(is_home=True)

    final_score = scorer.get_score()

    # Try to score another point
    scorer.increase_score(is_home=True)

    # Score should remain unchanged
    assert scorer.get_score() == final_score


@pytest.mark.unit
def test_singles_grandslam_uses_best_of_5() -> None:
    """Test that Singles Grand Slam requires 3 sets to win."""
    scorer = TennisScorer(MatchType.SINGLES_GRANDSLAM)

    # Win 2 sets - should not be finished yet
    for _ in range(2):
        for _ in range(6):
            for _ in range(4):
                scorer.increase_score(is_home=True)

    assert scorer.get_winner() is None

    # Win 3rd set - now should be finished
    for _ in range(6):
        for _ in range(4):
            scorer.increase_score(is_home=True)

    assert scorer.get_winner() == "home"


@pytest.mark.unit
def test_tiebreak_scoring() -> None:
    """Test that tiebreak is triggered at 6-6."""
    scorer = TennisScorer(MatchType.DOUBLES_DAVISCUP)

    # Get to 6-6 in games
    for i in range(12):
        is_home = i % 2 == 0
        for _ in range(4):
            scorer.increase_score(is_home=is_home)

    # Should be at 6-6 in games, 0-0 in tiebreak
    assert scorer.get_score() == "6:6-0:0"

    # Score in tiebreak uses numbers
    scorer.increase_score(is_home=True)
    assert scorer.get_score() == "6:6-1:0"
