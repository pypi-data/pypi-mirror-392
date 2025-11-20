"""Tests for core data models."""

import pytest

from pytennisscorer.models import GameState, MatchState, MatchType, ScoringRules, SetState


@pytest.mark.unit
def test_match_type_enum_has_all_required_types() -> None:
    """Test that MatchType enum contains all required match types."""
    assert MatchType.SINGLES_GRANDSLAM
    assert MatchType.SINGLES_ATP_FINALS
    assert MatchType.DOUBLES_DAVISCUP
    assert MatchType.DOUBLES_ATPTOUR
    assert MatchType.DOUBLES_GRANDSLAM


@pytest.mark.unit
def test_scoring_rules_for_singles_grandslam() -> None:
    """Test that ScoringRules can be created for Singles Grand Slam format."""
    rules = ScoringRules(
        best_of=5,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    assert rules.best_of == 5
    assert rules.final_set_match_tiebreak is False
    assert rules.deciding_point is False


@pytest.mark.unit
def test_scoring_rules_is_immutable() -> None:
    """Test that ScoringRules dataclass is frozen."""
    rules = ScoringRules(
        best_of=3,
        final_set_match_tiebreak=False,
        match_tiebreak_points=10,
        regular_tiebreak_points=7,
        deciding_point=False,
    )
    with pytest.raises(AttributeError):
        rules.best_of = 5  # type: ignore


@pytest.mark.unit
def test_game_state_creation() -> None:
    """Test that GameState can be created with home and away scores."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    assert game.home_score == 0
    assert game.away_score == 0
    assert game.is_tiebreak is False


@pytest.mark.unit
def test_game_state_is_immutable() -> None:
    """Test that GameState dataclass is frozen."""
    game = GameState(home_score=1, away_score=2, is_tiebreak=False)
    with pytest.raises(AttributeError):
        game.home_score = 3  # type: ignore


@pytest.mark.unit
def test_set_state_creation() -> None:
    """Test that SetState can be created with game scores."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=0, away_score=0, current_game=game, games=[game])
    assert set_state.home_score == 0
    assert set_state.away_score == 0
    assert set_state.current_game.home_score == 0
    assert len(set_state.games) == 1


@pytest.mark.unit
def test_set_state_is_immutable() -> None:
    """Test that SetState dataclass is frozen."""
    game = GameState(home_score=0, away_score=0, is_tiebreak=False)
    set_state = SetState(home_score=0, away_score=0, current_game=game, games=[])
    with pytest.raises(AttributeError):
        set_state.home_score = 1  # type: ignore


@pytest.mark.unit
def test_match_state_creation() -> None:
    """Test that MatchState can be created with complete match information."""
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

    assert match.home_score == 0
    assert match.away_score == 0
    assert match.current_set_index == 0
    assert len(match.sets) == 1
    assert match.is_finished is False
    assert match.match_type == MatchType.DOUBLES_DAVISCUP


@pytest.mark.unit
def test_match_state_is_immutable() -> None:
    """Test that MatchState dataclass is frozen."""
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

    with pytest.raises(AttributeError):
        match.is_finished = True  # type: ignore
