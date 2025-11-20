# Python Tennis Scorer Package Implementation Plan

> **IMPORTANT:** Start with fresh context. Run `/clear` before `/implement`.

**Goal:** Create a pip-installable Python package for tennis match scoring with comprehensive match format support.

**Architecture:** Functional approach using immutable dataclasses for state management and pure functions for logic, ensuring testability and following Python best practices.

**Tech Stack:** Python 3.9+, uv package manager, pytest, mypy, ruff, dataclasses, Jupyter

**Context for Implementer:**
- Based on existing TypeScript implementation with OOP design - translate to functional Python style
- Use immutable state transitions - each scoring action returns new state
- Follow TDD - write failing tests first for every feature
- Support 5 match types: Grand Slam singles/doubles, ATP Finals, Davis Cup, ATP Tour doubles

## Progress Tracking
- [ ] Task 1: Project Setup and Structure
- [ ] Task 2: Core Data Models
- [ ] Task 3: Point Scoring Logic
- [ ] Task 4: Tiebreak Scoring
- [ ] Task 5: Set and Match Progression
- [ ] Task 6: Score Formatting and Parsing
- [ ] Task 7: Main API Implementation
- [ ] Task 8: Match Type Configurations
- [ ] Task 9: Error Handling and Validation
- [ ] Task 10: Documentation and Examples

**Total Tasks:** 10

## Requirements Summary

The package must support:
1. **Match Formats**: 5 different tennis match types with specific rules
2. **Scoring**: Standard tennis points (0, 15, 30, 40, Ad), games, sets, matches
3. **Tiebreaks**: Regular (to 7) and match tiebreaks (to 10)
4. **State Management**: Immutable state with undo functionality
5. **Score Notation**: Parse and format standard tennis score strings
6. **Testing**: >90% coverage with TDD approach
7. **Distribution**: pip-installable package with examples

## Task Details

### Task 1: Project Setup and Structure

**Objective:** Initialize the Python package with uv, configure tools, and create the basic structure.

**Files:**
- Create: `pyproject.toml`
- Create: `src/pytennisscorer/__init__.py`
- Create: `.gitignore`
- Create: `README.md`
- Create: `ruff.toml`

**Implementation Steps:**
1. Initialize project with uv and Python 3.9+
2. Configure ruff for linting and formatting
3. Set up mypy for type checking
4. Add essential dependencies (pytest, jupyter, hypothesis)

**Definition of Done:**
- [ ] Project initialized with uv
- [ ] All configuration files created
- [ ] Dependencies installable via `uv pip install -e .`
- [ ] Linting and type checking configured

**Requirements Traceability:**
- Satisfies: Package distribution, testing infrastructure

---

### Task 2: Core Data Models

**Objective:** Create immutable dataclasses for state representation.

**Files:**
- Create: `src/pytennisscorer/models.py`
- Create: `tests/test_models.py`

**Implementation Steps:**
1. Write failing tests for model creation and validation
2. Implement `MatchType` enum and `ScoringRules` dataclass
3. Implement `GameState`, `SetState`, and `MatchState` dataclasses
4. Add validation and default values

**Definition of Done:**
- [ ] All tests pass for model creation
- [ ] Type hints complete
- [ ] Models are immutable (frozen=True)
- [ ] No mypy errors

**Requirements Traceability:**
- Satisfies: Match types, state representation

---

### Task 3: Point Scoring Logic

**Objective:** Implement pure functions for scoring points within games.

**Files:**
- Create: `src/pytennisscorer/scoring.py`
- Create: `tests/test_scoring.py`

**Implementation Steps:**
1. Write failing tests for point scoring scenarios (0-15-30-40-Game)
2. Implement `score_game_point()` function with deuce handling
3. Handle advantage scoring and deciding points
4. Test edge cases (deuce, advantage, deciding point)

**Definition of Done:**
- [ ] All game scoring tests pass
- [ ] Deuce and advantage logic correct
- [ ] Deciding point rule implemented
- [ ] Pure functions with no side effects

**Requirements Traceability:**
- Satisfies: Tennis point scoring, deuce/advantage rules

---

### Task 4: Tiebreak Scoring

**Objective:** Implement tiebreak scoring logic (regular and match tiebreaks).

**Files:**
- Modify: `src/pytennisscorer/scoring.py`
- Create: `tests/test_tiebreak.py`

**Implementation Steps:**
1. Write failing tests for 7-point and 10-point tiebreaks
2. Implement `score_tiebreak_point()` function
3. Handle minimum 2-point margin requirement
4. Test tiebreak completion scenarios

**Definition of Done:**
- [ ] Regular tiebreak (to 7) tests pass
- [ ] Match tiebreak (to 10) tests pass
- [ ] 2-point margin enforced
- [ ] Functions remain pure and stateless

**Requirements Traceability:**
- Satisfies: Tiebreak rules for different match types

---

### Task 5: Set and Match Progression

**Objective:** Implement logic for progressing through sets and determining match completion.

**Files:**
- Create: `src/pytennisscorer/progression.py`
- Create: `tests/test_progression.py`

**Implementation Steps:**
1. Write failing tests for set completion scenarios
2. Implement `progress_set()` for set transitions
3. Implement `check_match_complete()` for match ending
4. Handle different match formats (best of 3/5)

**Definition of Done:**
- [ ] Set progression tests pass
- [ ] Match completion correctly detected
- [ ] Winner determination accurate
- [ ] All match types supported

**Requirements Traceability:**
- Satisfies: Set rules, match completion, winner detection

---

### Task 6: Score Formatting and Parsing

**Objective:** Convert between internal state and human-readable tennis notation.

**Files:**
- Create: `src/pytennisscorer/formatter.py`
- Create: `tests/test_formatter.py`

**Implementation Steps:**
1. Write failing tests for score formatting (0, 15, 30, 40, Ad)
2. Implement `format_score()` for state to string conversion
3. Implement `parse_score()` for string to state conversion
4. Handle all score formats and edge cases

**Definition of Done:**
- [ ] Format produces correct tennis notation
- [ ] Parse handles all valid input formats
- [ ] Invalid formats raise appropriate errors
- [ ] Round-trip formatting/parsing works

**Requirements Traceability:**
- Satisfies: Score notation and display requirements

---

### Task 7: Main API Implementation

**Objective:** Create the high-level API that combines all components.

**Files:**
- Create: `src/pytennisscorer/scorer.py`
- Create: `tests/test_scorer.py`

**Implementation Steps:**
1. Write failing tests for public API methods
2. Implement `TennisScorer` class with functional core
3. Add `increase_score()`, `undo()`, `get_score()` methods
4. Implement state history for undo functionality

**Definition of Done:**
- [ ] Public API tests pass
- [ ] Undo functionality works correctly
- [ ] State immutability maintained
- [ ] Clean interface for users

**Requirements Traceability:**
- Satisfies: Main scoring operations, undo functionality

---

### Task 8: Match Type Configurations

**Objective:** Implement predefined configurations for different match formats.

**Files:**
- Create: `src/pytennisscorer/configs.py`
- Create: `tests/test_configs.py`

**Implementation Steps:**
1. Write tests for each match type configuration
2. Define configurations for all 5 match types
3. Implement factory functions for easy initialization
4. Validate configuration consistency

**Definition of Done:**
- [ ] All 5 match types configured correctly
- [ ] Configuration tests pass
- [ ] Easy initialization for users
- [ ] Rules properly enforced per type

**Requirements Traceability:**
- Satisfies: Support for all required match formats

---

### Task 9: Error Handling and Validation

**Objective:** Implement comprehensive error handling and input validation.

**Files:**
- Create: `src/pytennisscorer/exceptions.py`
- Modify: All existing modules for error handling
- Create: `tests/test_exceptions.py`

**Implementation Steps:**
1. Write tests for error conditions
2. Create custom exception classes
3. Add validation to all public functions
4. Ensure graceful error messages

**Definition of Done:**
- [ ] Custom exceptions defined
- [ ] Input validation complete
- [ ] Clear error messages
- [ ] All error paths tested

**Requirements Traceability:**
- Satisfies: Error handling and robustness

---

### Task 10: Documentation and Examples

**Objective:** Create comprehensive documentation and Jupyter notebook examples.

**Files:**
- Create: `notebooks/tennis_scorer_examples.ipynb`
- Modify: `README.md` with full documentation
- Create: `docs/API.md`

**Implementation Steps:**
1. Write Jupyter notebook with usage examples
2. Document all public APIs with docstrings
3. Create README with installation and quick start
4. Add interactive examples in notebook

**Definition of Done:**
- [ ] Jupyter notebook runs without errors
- [ ] All functions have docstrings
- [ ] README is comprehensive
- [ ] Examples cover all major features

**Requirements Traceability:**
- Satisfies: Documentation and example requirements

## Implementation Notes

**Key Design Decisions:**
1. Use frozen dataclasses for immutable state
2. Pure functions for all state transitions
3. Separate scoring logic from state management
4. Factory pattern for match type configurations
5. History list for undo functionality

**Testing Strategy:**
1. TDD approach - write tests first
2. Use pytest parametrize for match type variations
3. Property-based testing with Hypothesis for edge cases
4. Separate test files per module
5. Integration tests for complete match scenarios

**Code Quality Standards:**
1. Type hints on all functions
2. Docstrings following Google style
3. Ruff for formatting (line length 100)
4. Mypy in strict mode
5. >90% test coverage requirement