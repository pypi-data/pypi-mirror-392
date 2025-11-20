"""Match type configurations and factory functions."""

from dataclasses import dataclass

from pytennisscorer.models import GameState, MatchState, MatchType, ScoringRules, SetState


@dataclass(frozen=True)
class MatchConfig:
    """Complete configuration for a match type."""

    match_type: MatchType
    rules: ScoringRules
    initial_state: MatchState


def _create_initial_sets(num_sets: int, deciding_point: bool) -> list[SetState]:
    """
    Create initial sets for a match.

    Args:
        num_sets: Number of sets to create
        deciding_point: Whether deciding point rule is in effect

    Returns:
        List of SetState objects initialized to 0-0
    """
    sets = []
    for _ in range(num_sets):
        game = GameState(home_score=0, away_score=0, is_tiebreak=False)
        set_state = SetState(home_score=0, away_score=0, current_game=game, games=[])
        sets.append(set_state)
    return sets


def create_match_config(match_type: MatchType) -> MatchConfig:
    """
    Create a complete match configuration for a given match type.

    Args:
        match_type: Type of tennis match

    Returns:
        MatchConfig with rules and initial state

    Raises:
        ValueError: If match_type is not recognized
    """
    if match_type == MatchType.SINGLES_GRANDSLAM:
        rules = ScoringRules(
            best_of=5,
            final_set_match_tiebreak=False,
            match_tiebreak_points=10,
            regular_tiebreak_points=7,
            deciding_point=False,
        )
        sets = _create_initial_sets(5, deciding_point=False)

    elif match_type == MatchType.SINGLES_ATP_FINALS:
        rules = ScoringRules(
            best_of=3,
            final_set_match_tiebreak=False,
            match_tiebreak_points=10,
            regular_tiebreak_points=7,
            deciding_point=False,
        )
        sets = _create_initial_sets(3, deciding_point=False)

    elif match_type == MatchType.DOUBLES_DAVISCUP:
        rules = ScoringRules(
            best_of=3,
            final_set_match_tiebreak=False,
            match_tiebreak_points=10,
            regular_tiebreak_points=7,
            deciding_point=False,
        )
        sets = _create_initial_sets(3, deciding_point=False)

    elif match_type == MatchType.DOUBLES_ATPTOUR:
        rules = ScoringRules(
            best_of=3,
            final_set_match_tiebreak=True,
            match_tiebreak_points=10,
            regular_tiebreak_points=7,
            deciding_point=True,
        )
        sets = _create_initial_sets(3, deciding_point=True)

    elif match_type == MatchType.DOUBLES_GRANDSLAM:
        rules = ScoringRules(
            best_of=3,
            final_set_match_tiebreak=True,
            match_tiebreak_points=10,
            regular_tiebreak_points=7,
            deciding_point=False,
        )
        sets = _create_initial_sets(3, deciding_point=False)

    else:
        raise ValueError(f"Unknown match type: {match_type}")

    initial_state = MatchState(
        home_score=0,
        away_score=0,
        current_set_index=0,
        sets=sets,
        is_finished=False,
        match_type=match_type,
        rules=rules,
    )

    return MatchConfig(match_type=match_type, rules=rules, initial_state=initial_state)
