"""Tests for match type configurations."""

import pytest

from pytennisscorer.configs import create_match_config
from pytennisscorer.models import MatchType


@pytest.mark.unit
def test_create_singles_grandslam_config() -> None:
    """Test creating configuration for Singles Grand Slam."""
    config = create_match_config(MatchType.SINGLES_GRANDSLAM)

    assert config.match_type == MatchType.SINGLES_GRANDSLAM
    assert config.rules.best_of == 5
    assert config.rules.final_set_match_tiebreak is False
    assert config.rules.deciding_point is False
    assert config.rules.regular_tiebreak_points == 7
    assert config.rules.match_tiebreak_points == 10


@pytest.mark.unit
def test_create_singles_atp_finals_config() -> None:
    """Test creating configuration for Singles ATP Finals."""
    config = create_match_config(MatchType.SINGLES_ATP_FINALS)

    assert config.match_type == MatchType.SINGLES_ATP_FINALS
    assert config.rules.best_of == 3
    assert config.rules.final_set_match_tiebreak is False
    assert config.rules.deciding_point is False


@pytest.mark.unit
def test_create_doubles_daviscup_config() -> None:
    """Test creating configuration for Doubles Davis Cup."""
    config = create_match_config(MatchType.DOUBLES_DAVISCUP)

    assert config.match_type == MatchType.DOUBLES_DAVISCUP
    assert config.rules.best_of == 3
    assert config.rules.final_set_match_tiebreak is False
    assert config.rules.deciding_point is False


@pytest.mark.unit
def test_create_doubles_atptour_config() -> None:
    """Test creating configuration for Doubles ATP Tour."""
    config = create_match_config(MatchType.DOUBLES_ATPTOUR)

    assert config.match_type == MatchType.DOUBLES_ATPTOUR
    assert config.rules.best_of == 3
    assert config.rules.final_set_match_tiebreak is True
    assert config.rules.deciding_point is True
    assert config.rules.match_tiebreak_points == 10


@pytest.mark.unit
def test_create_doubles_grandslam_config() -> None:
    """Test creating configuration for Doubles Grand Slam."""
    config = create_match_config(MatchType.DOUBLES_GRANDSLAM)

    assert config.match_type == MatchType.DOUBLES_GRANDSLAM
    assert config.rules.best_of == 3
    assert config.rules.final_set_match_tiebreak is True
    assert config.rules.deciding_point is False


@pytest.mark.unit
def test_config_creates_initial_match_state() -> None:
    """Test that config includes an initialized match state."""
    config = create_match_config(MatchType.DOUBLES_DAVISCUP)

    assert config.initial_state.home_score == 0
    assert config.initial_state.away_score == 0
    assert config.initial_state.current_set_index == 0
    assert config.initial_state.is_finished is False
    assert len(config.initial_state.sets) > 0


@pytest.mark.unit
def test_config_creates_correct_number_of_sets() -> None:
    """Test that configs create the correct number of sets."""
    # Best of 5
    config_bo5 = create_match_config(MatchType.SINGLES_GRANDSLAM)
    assert len(config_bo5.initial_state.sets) == 5

    # Best of 3
    config_bo3 = create_match_config(MatchType.DOUBLES_DAVISCUP)
    assert len(config_bo3.initial_state.sets) == 3
