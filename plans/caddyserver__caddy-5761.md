# Plan Name: Analyze Caddy Server Bug Report and Create Fix Plan

## Tasks

### 1. Implement escape-aware `<<` detection (do not start heredoc on `\<<`) (Epic: Fix Caddyfile lexer heredoc edge-cases (escaped markers; avoid false `<EOF` heredoc start))

#### Description

Update lexer logic around reading `<`/`<<` so an immediately preceding escape (`\`) prevents heredoc start.

Acceptance criteria (testable):
- Given input containing `\<<` in a token context (e.g. `escaped-heredoc \\<< >>`), the lexer produces a `<<` token (literal) and does NOT switch to heredoc-reading state.
- Escape handling matches existing lexer conventions: the backslash is not emitted as part of token unless current rules already do so for other escaped punctuation.

Implementation notes:
- Identify the code path that currently branches into heredoc mode when seeing `<<`.
- Add a check for "is escaped" based on previous rune/byte or lexer escape state.
- Be careful to not break valid cases where `<<` appears inside quoted strings (if lexer treats those differently).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Implement escape-aware `<<` detection (do not start heredoc on `\<<`) <-
    - upcoming (not yet): Tighten heredoc start recognition to avoid false start on `<EOF`
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Fix the Caddyfile lexer so an escaped heredoc introducer `\<<` is treated as a literal `<<` token and never starts heredoc mode.

##### Technical Specs
- **Area**: `caddyconfig/caddyfile` lexer (likely `lexer.go` or equivalent).
- **Behavior change**: heredoc mode may only start on an **unescaped** `<<`.
- **Escaping rule**: if the lexer sees `<<` and the *immediately preceding* character is a backslash used as an escape in the current lexing context, treat the sequence as literal text (tokenize `<<` like normal punctuation) and do not transition into heredoc-reading state.
- **Quoted strings**: do not alter the existing behavior for `<<` that occurs inside quoted strings (unless tests explicitly require it). Escapes inside quotes must keep following existing conventions.

##### Implementation Checklist
- [ ] Locate the exact branch where the lexer switches into heredoc mode when encountering `<<`.
- [ ] Add an “is escaped” guard so heredoc-start detection is bypassed when `<<` is immediately preceded by an escape `\` (using the lexer’s existing escape tracking / previous-rune tracking).
- [ ] Ensure token emission matches existing escape conventions:
  - the backslash should **not** become part of the emitted token unless the lexer already emits backslashes for other escaped punctuation in similar contexts.
- [ ] Confirm no changes to token boundaries, whitespace handling, comments, or position tracking beyond what is required for this fix.

##### Success Criteria
- [ ] The updated/new lexer test covering `escaped-heredoc \\<< >>` passes: tokens include `escaped-heredoc`, `<<`, `>>`, and lexer never enters heredoc mode for that `<<`.
- [ ] All existing lexer tests remain green (no regressions around normal heredocs, quoting, comments, or escapes).

##### Files to Read
- `caddyconfig/caddyfile/lexer.go`
- `caddyconfig/caddyfile/lexer_test.go`

##### Files to Modify
- `caddyconfig/caddyfile/lexer.go` (primary)
- Tests only if strictly necessary for determinism/consistency with intended behavior.


### 2. Fix Caddyfile lexer heredoc edge-cases (escaped markers; avoid false `<EOF` heredoc start)

#### Description

Bugfix plan for caddyserver/caddy based on updated tests in `caddyconfig/caddyfile/lexer_test.go`.

Problem summary (from requirements + context):
- Lexer currently mis-detects heredoc starts in two cases:
  1) Escaped heredoc marker: `\<<` should tokenize as a literal `<<` token (no heredoc mode entered).
  2) False heredoc start on `<EOF`: sequences like `<EOF` should be treated as an ordinary token unless they exactly match the lexer’s heredoc-start grammar. When not a real heredoc, lexer must not consume following lines until an `EOF` terminator.

Success criteria:
- Newly added/updated lexer tests pass.
- All existing lexer tests remain green.
- No regression for valid heredocs.

Scope notes:
- Primary change is expected in the Caddyfile lexer (likely `caddyconfig/caddyfile/lexer.go` or equivalent). Parser changes only if lexer cannot express the required disambiguation cleanly.
- This plan assumes tests already exist in the patch; we will only adjust tests if they’re inconsistent with intended behavior or need minor corrections for determinism.


### 3. Tighten heredoc start recognition to avoid false start on `<EOF` (Epic: Fix Caddyfile lexer heredoc edge-cases (escaped markers; avoid false `<EOF` heredoc start))

#### Description

Adjust lexer so `<EOF` does not trigger heredoc mode unless it matches the exact heredoc start pattern (expected to be `<<` + marker token).

Acceptance criteria (testable):
- For an input like:
  - Line 1: `not-a-heredoc <EOF`
  - Line 2: `content`
  the lexer must emit `<EOF` as a normal token (or `<` + `EOF` depending on current tokenization rules), and must NOT consume line 2 as heredoc content.
- Valid heredoc starts (e.g. `<<EOF` or `<< EOF` depending on supported grammar) still enter heredoc mode and stop only at the exact terminator line.

Implementation notes:
- Ensure the lexer only enters heredoc mode after observing unescaped `<<`.
- If lexer currently checks for `<` followed by something that looks like marker, refactor so it requires two consecutive `<` runes.
- Add/adjust lookahead handling carefully so token boundaries and line/column tracking remain correct.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement escape-aware `<<` detection (do not start heredoc on `\<<`)
    - current (in progress task): Tighten heredoc start recognition to avoid false start on `<EOF` <-
    - upcoming (not yet): Run and fix tests: lexer suite + full `go test ./...` regression check
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Tighten heredoc start recognition so `<EOF` (single `<` followed by marker-like text) does **not** trigger heredoc mode; heredoc mode must only start on the lexer’s exact heredoc introducer grammar (expected: unescaped `<<` followed by a marker token).

##### Technical Specs
- **Area**: `caddyconfig/caddyfile` lexer.
- **Behavior change**:
  - `<EOF` must be tokenized as ordinary input (either a single token `<EOF` or tokens `<` and `EOF`, consistent with current lexer rules).
  - The lexer must not consume subsequent lines as heredoc content unless it actually recognized a valid heredoc start (`<<...` per supported grammar).
- **Heredoc introducer rule**: require **two consecutive** `<` characters (`<<`) that are **not escaped** (and not within a context where heredocs are not recognized, e.g., inside quotes if applicable).
- **Lookahead**: any lookahead used to detect heredocs must preserve current token boundaries and line/column accounting.

##### Implementation Checklist
- [ ] Identify current heredoc-start detection logic; verify whether it triggers on `<` + marker-like patterns.
- [ ] Refactor detection so heredoc mode can only be entered after observing an unescaped `<<` sequence.
- [ ] Ensure `<EOF` and similar patterns are treated as non-heredoc tokens and do not alter scanning state.
- [ ] Verify valid heredoc starts still work:
  - `<<EOF` and/or `<< EOF` (whichever the lexer currently supports) must enter heredoc mode.
  - Termination must still require the exact terminator line per existing rules.

##### Success Criteria
- [ ] A test with:
  - line1: `not-a-heredoc <EOF`
  - line2: `content`
  emits `<EOF` as normal token(s) and does **not** consume `content` as heredoc body.
- [ ] All existing heredoc tests continue to pass (no regression for valid heredocs, terminators, whitespace sensitivity, or position tracking).

##### Files to Read
- `caddyconfig/caddyfile/lexer.go`
- `caddyconfig/caddyfile/lexer_test.go`

##### Files to Modify
- `caddyconfig/caddyfile/lexer.go` (primary)


### 4. Run and fix tests: lexer suite + full `go test ./...` regression check (Epic: Fix Caddyfile lexer heredoc edge-cases (escaped markers; avoid false `<EOF` heredoc start))

#### Description

Validate the fix against the updated tests and guard against regressions.

Steps / acceptance criteria:
- Run package tests for `caddyconfig/caddyfile` (or equivalent) and ensure the new heredoc edge-case tests pass.
- Run `go test ./...` and ensure all tests remain green.
- If any failures occur, update lexer logic to maintain existing semantics (line endings, token positions, quoted strings, comment handling) while preserving the two bugfix behaviors.

Deliverable:
- A clean test run that includes the newly added tests in `caddyconfig/caddyfile/lexer_test.go`.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Tighten heredoc start recognition to avoid false start on `<EOF`
    - current (in progress task): Run and fix tests: lexer suite + full `go test ./...` regression check <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run the lexer test suite and full repository test suite to validate the heredoc edge-case fixes, and address any regressions while preserving existing lexer semantics.

##### Technical Specs
- **Test targets**:
  - Package-level tests for `caddyconfig/caddyfile` (focus: `lexer_test.go`).
  - Full suite: `go test ./...` to catch indirect regressions.
- **Allowed changes**:
  - Prefer lexer-only fixes.
  - Parser changes only if strictly necessary to express correct lexing behavior.
  - Test changes only for determinism or if a test contradicts the stated intended behavior.

##### Implementation Checklist
- [ ] Execute package tests for `caddyconfig/caddyfile`; ensure all lexer tests (including newly added heredoc edge cases) pass.
- [ ] Execute `go test ./...`; ensure the full suite passes.
- [ ] If failures occur, adjust lexer logic to fix them without changing established semantics:
  - line endings handling (LF/CRLF)
  - token boundaries and whitespace rules
  - comment handling
  - quoted string behavior
  - token position/line-column reporting
- [ ] Keep changes minimal and directly tied to heredoc disambiguation (escaped `<<`, and strict `<<` requirement vs `<EOF`).

##### Success Criteria
- [ ] `caddyconfig/caddyfile` tests pass, including the new/updated heredoc edge-case tests in `lexer_test.go`.
- [ ] `go test ./...` passes with no new failures.
- [ ] Review confirms no regressions in valid heredoc behavior and no unintended changes to tokenization rules outside the targeted cases.

##### Files to Read
- `caddyconfig/caddyfile/lexer_test.go`
- `caddyconfig/caddyfile/lexer.go`

##### Files to Modify
- `caddyconfig/caddyfile/lexer.go` (as needed to fix failures)
- `caddyconfig/caddyfile/lexer_test.go` (only if required for determinism or correction)
