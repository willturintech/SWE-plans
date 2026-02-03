# Plan Name: Debug CaddyServer CSV Bug and Create Fix Plan

## Tasks

### 1. Update/extend heredoc lexer tests to codify expected token text (Epic: Fix Caddyfile lexer heredoc trailing newline tokenization (task_3_caddyserver_caddy))

#### Description

Apply the test expectations described in task_3 so they fail on current behavior and pass with the fix.

Acceptance criteria:
- Tests assert heredoc token text does NOT include the final newline immediately preceding the end marker.
- Tests include a case with an extra blank line (or multiple newlines) before the end marker to ensure trimming is correct.

Implementation outline:
- Find existing lexer tests covering heredocs (commonly `caddyconfig/caddyfile/lexer_test.go` or similar).
- Modify expected heredoc content token(s) to remove the unwanted trailing `\n`.
- Add a new heredoc fixture with an extra newline immediately before the end marker; assert that only that final delimiter-adjacent newline is excluded (other blank lines remain).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Update/extend heredoc lexer tests to codify expected token text <-
    - upcoming (not yet): Implement lexer change: exclude newline immediately before heredoc end marker from token text
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Update and extend the Caddyfile lexer heredoc tests to codify the corrected token text behavior (heredoc content must not include the final newline immediately preceding the end marker).

##### Technical Specs
- **Scope**: Tests only (no lexer logic changes in this ticket).
- **Location**: Caddy upstream path `caddyconfig/caddyfile` (likely `lexer_test.go`, but use whatever file currently covers lexer token expectations).
- **Behavior under test**:
  - Heredoc content token text excludes the delimiter-adjacent newline (the newline directly before the marker line).
  - Blank lines that are part of heredoc content remain intact (i.e., do not “over-trim”).

##### Implementation Checklist
- [ ] Locate existing lexer/heredoc tests and understand how tokens are asserted (golden strings vs explicit token arrays).
- [ ] Update existing heredoc expectations to remove the unwanted trailing `\n` in the heredoc content token text.
- [ ] Add a new regression test case where heredoc content ends with one or more blank lines *before* the end marker; assert:
  - only the final newline immediately preceding the marker is excluded from token text,
  - earlier blank lines/newlines are preserved.
- [ ] Keep tests narrowly focused on heredoc token text (avoid changing unrelated token expectations).

##### Success Criteria
- [ ] New/updated tests fail against the pre-fix lexer behavior (extra trailing newline present).
- [ ] Tests pass once the lexer fix is applied.
- [ ] No changes in expected tokenization outside heredoc scenarios within the modified tests.

##### Notes / Guardrails
- Preserve coverage for edge cases if already present (e.g., empty heredoc `<<EOF` followed immediately by `EOF` should yield empty token text).
- Avoid asserting brittle details unrelated to this bug (e.g., internal offsets) unless existing tests already do so.

---


### 2. Fix Caddyfile lexer heredoc trailing newline tokenization (task_3_caddyserver_caddy)

#### Description

Implement the bugfix described in `tasks/task_3_caddyserver_caddy.csv`: the Caddyfile lexer’s heredoc parsing currently includes an extra trailing newline in the heredoc token text immediately before the heredoc end marker. Update the lexer so heredoc token text matches expected semantics (no extra newline before end marker), and update/add tests per the patch referenced in task_3.

Outcome: token text for heredoc content is stable and matches tests, including cases with additional blank lines before the end marker.

Constraints:
- Preserve existing tokenization semantics outside heredocs.
- Ensure error handling (unterminated heredoc, mismatched marker) remains intact.

Notes:
- This repo appears to be a task/spec artifact collection; implementation will be in the upstream Caddy repo path `caddyconfig/caddyfile` (lexer + tests). This plan assumes we’re applying the change in that codebase.


### 3. Implement lexer change: exclude newline immediately before heredoc end marker from token text (Epic: Fix Caddyfile lexer heredoc trailing newline tokenization (task_3_caddyserver_caddy))

#### Description

Modify the heredoc scanning logic so the token text for heredoc content excludes the newline that directly precedes the end marker line.

Implementation notes (to be validated in code):
- Heredoc is typically parsed by reading lines until a line equals the marker. The lexer often appends each read line plus `\n` into a buffer.
- The bug indicates the final content buffer ends with an extra `\n` that corresponds to the line break before the marker.
- Adjust so when the end marker is detected, the lexer does not include the separator newline immediately before it.

Concrete approaches (pick the least invasive once code is inspected):
- Buffering approach: only append `\n` after lines that are confirmed as content lines (i.e., append newline when you append the line; if next line is marker, you never appended anything for it).
- Trimming approach: when marker is detected, trim exactly one trailing `\n` from the buffer, but only if that `\n` was added as the line separator immediately before the marker.

Edge cases to preserve:
- Empty heredoc (`<<EOF` then immediate `EOF`) => empty token text.
- Heredoc with intentional blank lines => preserved, except the delimiter-adjacent newline.
- Unterminated heredoc / mismatched marker => same error behavior as before.

Acceptance criteria:
- Updated heredoc tests pass.
- Non-heredoc tokenization unchanged.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Update/extend heredoc lexer tests to codify expected token text
    - current (in progress task): Implement lexer change: exclude newline immediately before heredoc end marker from token text <-
    - upcoming (not yet): Run lexer/package tests and confirm no regressions
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement the lexer bugfix so heredoc token text excludes the newline immediately preceding the heredoc end marker, while preserving all non-heredoc tokenization semantics and existing error handling.

##### Technical Specs
- **Scope**: Lexer heredoc scanning logic in `caddyconfig/caddyfile` (the lexer implementation file(s) used by existing tests).
- **Required behavior change**:
  - When a heredoc end marker line is encountered, the heredoc token’s text must not include the newline separator that directly precedes that marker line.
- **Must preserve**:
  - All tokenization behavior outside heredocs.
  - Error handling for unterminated heredocs and mismatched markers (same error types/messages/positions as current behavior, unless tests explicitly require otherwise).

##### Implementation Checklist
- [ ] Identify the heredoc parsing path in the lexer (where it reads lines until the marker).
- [ ] Choose the least invasive fix that matches existing style:
  - **Preferred**: adjust buffering so `\n` is only appended for confirmed content lines (never for the marker line boundary), **or**
  - **Alternative**: on detecting the marker, remove exactly one trailing `\n` from the accumulated buffer *only if present* and only as part of the heredoc termination path.
- [ ] Ensure the fix does not remove intentional trailing newlines that are not delimiter-adjacent (e.g., multiple blank lines before marker should remain represented appropriately except for the final delimiter-adjacent newline).
- [ ] Validate edge cases in code behavior:
  - Empty heredoc (`<<EOF` then immediate `EOF`) => empty token text.
  - Heredoc with blank lines => preserved, except delimiter-adjacent newline.
  - Unterminated heredoc => unchanged error path.

##### Success Criteria
- [ ] Updated heredoc tests (from task (2)) pass.
- [ ] No diffs in tokenization for non-heredoc inputs (verify by running the existing lexer tests suite and ensuring only the heredoc expectations changed).
- [ ] Unterminated/mismatched marker error behavior remains intact (confirmed by existing tests or by adding/adjusting tests only if necessary to lock behavior).

##### Reviewability Requirements
- [ ] The change is localized to heredoc termination logic and is easy to reason about (avoid broad refactors).
- [ ] Add a short code comment if needed to explain why exactly one newline is excluded at marker detection.

---


### 4. Run lexer/package tests and confirm no regressions (Epic: Fix Caddyfile lexer heredoc trailing newline tokenization (task_3_caddyserver_caddy))

#### Description

Validate the change with a broader test run.

Acceptance criteria:
- `go test` for the `caddyconfig/caddyfile` package passes.
- Any repository-wide test run that includes lexer behavior passes (if available in the working tree).
- No unintended diffs beyond heredoc newline semantics.

Implementation outline:
- Run package tests; if failures occur, adjust implementation/tests.
- Add an additional focused regression assertion if a failure reveals ambiguous semantics (e.g., ensure only one newline is removed).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement lexer change: exclude newline immediately before heredoc end marker from token text
    - current (in progress task): Run lexer/package tests and confirm no regressions <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run package-level and (if available) wider test suites to confirm the heredoc newline fix introduces no regressions, and ensure the change set is limited strictly to intended heredoc semantics.

##### Technical Specs
- **Test execution**:
  - Run `go test` for `caddyconfig/caddyfile`.
  - If the working tree includes broader Go packages, run the repository’s standard Go test invocation as feasible (e.g., `go test ./...`) to catch unintended fallout.

##### Implementation Checklist
- [ ] Execute `go test ./caddyconfig/caddyfile` (or equivalent) and ensure it passes.
- [ ] If available and reasonable in this environment, execute `go test ./...` and ensure it passes.
- [ ] Inspect git diff to confirm changes are limited to:
  - heredoc lexer logic for the delimiter-adjacent newline,
  - the associated tests.
- [ ] If any failures indicate ambiguous heredoc semantics, add one focused regression assertion/test that disambiguates expected behavior (ensure it is directly tied to the newline-before-marker rule, not unrelated formatting).

##### Success Criteria
- [ ] `go test` for the `caddyconfig/caddyfile` package passes.
- [ ] Wider test run (if performed) passes with no new failures attributable to the change.
- [ ] No unintended diffs beyond heredoc newline semantics (confirmed via diff review).
