"""Main TennisScorer API."""

from dataclasses import replace
from typing import Literal, Optional

from pytennisscorer.configs import create_match_config
from pytennisscorer.formatter import format_match_score
from pytennisscorer.models import MatchState, MatchType
from pytennisscorer.progression import (
    check_match_complete,
    get_match_winner,
    is_set_finished,
    progress_to_next_game,
    progress_to_next_set,
)
from pytennisscorer.scoring import (
    is_game_finished,
    score_game_point,
    score_tiebreak_point,
)


class TennisScorer:
    """High-level API for tennis match scoring."""

    def __init__(self, match_type: MatchType) -> None:
        """
        Initialize a tennis scorer with a specific match type.

        Args:
            match_type: Type of tennis match to score
        """
        config = create_match_config(match_type)
        self._state = config.initial_state
        self._history: list[MatchState] = [self._state]

    def increase_score(self, is_home: bool) -> None:
        """
        Score a point for the specified player.

        Args:
            is_home: True to score for home player, False for away player
        """
        # Don't modify if match is finished
        if self._state.is_finished:
            return

        # Save current state to history
        self._history.append(self._state)

        # Get current set and game
        current_set = self._state.sets[self._state.current_set_index]
        current_game = current_set.current_game

        # Score the point in the current game
        if current_game.is_tiebreak:
            new_game = score_tiebreak_point(
                current_game,
                is_home,
                tiebreak_points=self._state.rules.regular_tiebreak_points,
            )
        else:
            new_game = score_game_point(
                current_game, is_home, deciding_point=self._state.rules.deciding_point
            )

        # Update current set with new game
        new_set = replace(current_set, current_game=new_game)

        # Check if game is finished
        if current_game.is_tiebreak:
            game_finished = is_game_finished(
                new_game,
                deciding_point=False,
                tiebreak_points=self._state.rules.regular_tiebreak_points,
            )
        else:
            game_finished = is_game_finished(
                new_game, deciding_point=self._state.rules.deciding_point
            )

        if game_finished:
            # Progress to next game
            home_won_game = new_game.home_score > new_game.away_score
            new_set = progress_to_next_game(
                new_set, home_won_game, deciding_point=self._state.rules.deciding_point
            )

            # Check if set is finished
            is_final_set = self._state.current_set_index == len(self._state.sets) - 1
            if is_set_finished(new_set, self._state.rules, is_final_set):
                # Update match score
                home_won_set = new_set.home_score > new_set.away_score
                new_home_score = self._state.home_score + (1 if home_won_set else 0)
                new_away_score = self._state.away_score + (0 if home_won_set else 1)

                # Check if match is complete
                is_match_finished = check_match_complete(
                    new_home_score, new_away_score, self._state.rules
                )

                # Update sets list
                new_sets = list(self._state.sets)
                new_sets[self._state.current_set_index] = new_set

                # Create new set if match not finished and not at last set
                if (
                    not is_match_finished
                    and self._state.current_set_index < len(self._state.sets) - 1
                ):
                    new_set_index = self._state.current_set_index + 1
                    new_sets[new_set_index] = progress_to_next_set(
                        deciding_point=self._state.rules.deciding_point
                    )
                else:
                    new_set_index = self._state.current_set_index

                self._state = replace(
                    self._state,
                    home_score=new_home_score,
                    away_score=new_away_score,
                    current_set_index=new_set_index,
                    sets=new_sets,
                    is_finished=is_match_finished,
                )
            else:
                # Set not finished, just update the set
                new_sets = list(self._state.sets)
                new_sets[self._state.current_set_index] = new_set
                self._state = replace(self._state, sets=new_sets)
        else:
            # Game not finished, just update the game in the set
            new_sets = list(self._state.sets)
            new_sets[self._state.current_set_index] = new_set
            self._state = replace(self._state, sets=new_sets)

    def undo(self) -> bool:
        """
        Undo the last scored point.

        Returns:
            True if undo was successful, False if no history to undo
        """
        if len(self._history) <= 1:
            return False

        # Remove current state and restore previous
        self._history.pop()
        self._state = self._history[-1]
        return True

    def get_score(self) -> str:
        """
        Get the current match score in tennis notation.

        Returns:
            Score string (e.g., "6:4;3:6;2:2-30:15")
        """
        return format_match_score(self._state)

    def get_winner(self) -> Optional[Literal["home", "away"]]:
        """
        Get the winner of the match.

        Returns:
            "home" if home won, "away" if away won, None if match not finished
        """
        return get_match_winner(self._state)
