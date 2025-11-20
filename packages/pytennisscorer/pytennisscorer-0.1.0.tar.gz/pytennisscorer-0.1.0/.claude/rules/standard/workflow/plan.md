# PLAN MODE: Six-Phase Planning Discovery Process

## Extending Existing Plans

**When adding tasks to existing plan:**

1. Load existing plan: `Read(file_path="docs/plans/...")`
2. Parse structure (architecture, completed tasks, pending tasks)
3. Check git status for partially completed work
4. Verify new tasks are compatible with existing architecture
5. Check total: If original + new > 12 tasks, suggest splitting
6. Mark new tasks with `[NEW]` prefix
7. Update total count: `Total Tasks: X (Originally: Y)`
8. Add extension history: `> Extended [Date]: Tasks X-Y for [feature]`

## Creating New Plans

### Phase 0: Research and Discovery

**Always start with:**
1. Query Cipher: `mcp__cipher__ask_cipher("What do we know about <feature>? Past implementations?")`
2. Search codebase: `mcp__claude-context__search_code(path="/workspaces/...", query="related features")`
3. Query relevant MCP servers for external systems

**Goals:**
- Understand existing patterns and architecture
- Find similar implementations to learn from
- Identify reusable components
- Learn from past decisions and gotchas

### Phase 1: Requirements Definition with EARS

**Generate formal requirements using EARS syntax:**
- Transform user request into User Stories with acceptance criteria
- Use EARS keywords: WHEN, THEN, IF, WHILE, WHERE, SHALL
- Be comprehensive - include edge cases and error conditions
- Don't ask multiple clarifying questions before first draft

**Required Format:**
```markdown
### Requirement 1
**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria
1. WHEN [event] THEN the system SHALL [response]
2. IF [precondition] THEN the system SHALL [response]
3. WHERE [state] the system SHALL [behavior]
4. WHILE [ongoing condition] the system SHALL [maintain behavior]
```

**After generating requirements:**
- Present draft and ask: "Do the requirements look good? If so, we can move on to the design phase."
- MUST receive explicit approval (yes/approved/looks good) before proceeding
- Iterate based on feedback until approved

### Phase 2: Exploration

**Propose 2-3 architectural approaches:**
- Use **AskUserQuestion tool** to present options
- Each approach should have:
  - Brief description (2-3 sentences)
  - Key benefits
  - Trade-offs or limitations

**Example:**
```
Option A: Client-side filtering (Fast, no server load, limited scalability)
Option B: Server-side filtering (Scalable, secure, requires API changes)
Option C: Hybrid approach (Best of both, more complex)
```

Let the user choose the direction based on their priorities.

### Phase 3: Design Validation

**Present the chosen design in sections:**
- Keep each section 200-300 words
- Cover:
  - Architecture overview
  - Component breakdown
  - Data flow
  - Error handling strategy
  - Testing approach

**After each section:** Ask "Does this approach work for your needs?"
- Adjust based on feedback
- Don't proceed until design is validated

### Phase 4: Implementation Planning with Definition of Done

**CRITICAL: Task Count Limit**
- **Maximum: 10-12 tasks per plan**
- If initial breakdown exceeds 12 tasks, STOP
- Ask user to split into multiple features

**Enhanced Task Structure:**
```markdown
### Task N: [Component Name]

**Objective:** [1-2 sentences describing what to build]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/to/test.py`

**Implementation Steps:**
1. Write failing test - Define expected behavior
2. Implement minimal code - Make test pass
3. Verify execution - Run actual program
4. Integration test - Test with other components

**Definition of Done:**
- [ ] All tests pass (unit, integration if applicable)
- [ ] No diagnostics errors (linting, type checking)
- [ ] Code functions correctly with real data
- [ ] Edge cases handled appropriately
- [ ] Error messages are clear and actionable

**Requirements Traceability:**
- Satisfies: Requirement 1.2, 1.3 (reference to EARS requirements)
```

**Zero-context assumption:**
- Assume implementer knows nothing about codebase
- Provide exact file paths
- Explain domain concepts
- List integration points
- Reference similar patterns in codebase

### Phase 5: Documentation

**Save plan to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Required plan header:**
```markdown
# [Feature Name] Implementation Plan

> **IMPORTANT:** Start with fresh context. Run `/clear` before `/implement`.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Context for Implementer:**
- [Key codebase convention or pattern]
- [Domain knowledge needed]
- [Integration points or dependencies]

## Progress Tracking
- [ ] Task 1: [Brief summary]
- [ ] Task 2: [Brief summary]

**Total Tasks:** [Number] (Max: 12)
```

### Phase 6: Implementation Handoff

**After saving plan:**
1. Store in Cipher: `mcp__cipher__ask_cipher("Store this implementation plan for <feature>")`
2. Inform user: "✅ Plan saved to docs/plans/YYYY-MM-DD-<feature>.md"
3. Provide next steps: "Ready for implementation. Run `/clear` then `/implement <plan-path>`"
