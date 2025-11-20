"""Core data models for tennis scoring."""

from dataclasses import dataclass
from enum import Enum


class MatchType(str, Enum):
    """Enum representing different tennis match types."""

    SINGLES_GRANDSLAM = "SINGLES_GRANDSLAM"
    SINGLES_ATP_FINALS = "SINGLES_ATP_FINALS"
    DOUBLES_DAVISCUP = "DOUBLES_DAVISCUP"
    DOUBLES_ATPTOUR = "DOUBLES_ATPTOUR"
    DOUBLES_GRANDSLAM = "DOUBLES_GRANDSLAM"


@dataclass(frozen=True)
class ScoringRules:
    """Immutable scoring rules for a tennis match."""

    best_of: int
    final_set_match_tiebreak: bool
    match_tiebreak_points: int
    regular_tiebreak_points: int
    deciding_point: bool


@dataclass(frozen=True)
class GameState:
    """Immutable state for a single game within a set."""

    home_score: int
    away_score: int
    is_tiebreak: bool


@dataclass(frozen=True)
class SetState:
    """Immutable state for a set within a match."""

    home_score: int
    away_score: int
    current_game: GameState
    games: list[GameState]


@dataclass(frozen=True)
class MatchState:
    """Immutable state for a complete tennis match."""

    home_score: int
    away_score: int
    current_set_index: int
    sets: list[SetState]
    is_finished: bool
    match_type: MatchType
    rules: ScoringRules
