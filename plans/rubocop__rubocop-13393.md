Observed: internal error
# Plan Name: Analyze RuboCop Bug Report and Create Fix Plan

## Tasks

### 1. Helper: collect assigned local var names from condition AST (Epic: Fix Style/GuardClause false positives with conditional-assignment locals)

#### Description

Add a helper method in the cop that returns the set/list of local variable names assigned in an `if` condition.

Done when:
- Returns `[:foo]` for `(foo = bar)`.
- Returns `[:foo, :baz]` for `(foo = bar && baz = qux)`-style conditions.
- Handles nested shapes (`begin`, `and`/`or`, `&&`/`||`).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Helper: collect assigned local var names from condition AST <-
    - upcoming (not yet): Helper: detect reads of those locals in the then-branch
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement a new helper in the upstream RuboCop cop `Style/GuardClause` that extracts **local variable names assigned inside an `if` condition AST**.

##### Scope / Location
- Make changes in upstream `rubocop/rubocop`.
- Implement in (or immediately near) `lib/rubocop/cop/style/guard_clause.rb`.
- Keep changes localized; avoid refactors outside the cop unless strictly necessary.

##### Technical Specs
- Add a helper method (private) that accepts an AST node representing the `if` condition (typically `if_node.condition`) and returns a **unique list/set** of local variable names assigned within it.
- Assignment to detect: `lvasgn` nodes (e.g., `(foo = bar)`).
- Must traverse condition AST robustly, including nested/common shapes:
  - Parenthesized expressions represented as `begin`
  - Boolean composition: `and` / `or` nodes and `&&` / `||` (often represented as `and`/`or` in the AST depending on parser; handle both by walking descendants rather than matching specific node types).
- Return value format:
  - Prefer an `Array<Symbol>` with deterministic order (e.g., first occurrence order) to keep specs/review stable, or a `Set<Symbol>` if the cop already uses sets internally. If returning a set, ensure callers handle it predictably.
- Include only names for **locals assigned in the condition**; ignore:
  - `ivasgn`, `cvasgn`, `gvasgn`
  - assignments occurring outside the condition node
  - reads (`lvar`) without assignment

##### Implementation Checklist
- [ ] Identify the appropriate existing helper patterns in `Style/GuardClause` (or shared mixins) for AST traversal and name extraction; reuse if available.
- [ ] Implement `assigned_lvar_names_in_condition(condition_node)` (name can differ, but must be clear and private).
- [ ] Traverse using `each_descendant(:lvasgn)` / `descendants` patterns (preferred) rather than hard-coding boolean node shapes, so nested `begin`/boolean combinations are covered.
- [ ] Deduplicate names.
- [ ] Add minimal inline comments explaining why the helper exists (guard clause conversion safety).

##### Success Criteria (verifiable)
- [ ] For condition AST representing `(foo = bar)`, helper returns `[:foo]`.
- [ ] For condition AST representing `(foo = bar && baz = qux)` (or `and` equivalent), helper returns `[:foo, :baz]`.
- [ ] Works when assignments are nested under `begin` and boolean operator nodes (verified by adding/adjusting unit-level expectations in the cop spec or by invoking helper through existing spec pathways if direct helper tests are not used in this codebase).
- [ ] No existing `Style/GuardClause` specs regress.

##### Files to modify
- `lib/rubocop/cop/style/guard_clause.rb`


### 2. Add/confirm regression specs for conditional-assignment locals (Epic: Fix Style/GuardClause false positives with conditional-assignment locals)

#### Description

Apply/confirm the spec changes from `tasks/task_3_rubocop_rubocop.csv` patch in upstream `rubocop/rubocop`.

Files:
- `spec/rubocop/cop/style/guard_clause_spec.rb`

Work:
- Add/confirm two `expect_no_offenses` examples:
  1) single conditional assignment in condition and later use in branch (`return foo`).
  2) multiple conditional assignments in condition (via `&&`/`and`) and later uses in branch (`return [foo, baz]`).
- Ensure examples are in the correct describe/context block for `Style/GuardClause` and follow existing style.

Acceptance:
- On current upstream baseline, these examples reproduce the bug (offense currently reported).
- After the cop fix, they pass and remain as regression tests.

Test command:
- `bundle exec rspec spec/rubocop/cop/style/guard_clause_spec.rb`


### 3. Fix Style/GuardClause false positives with conditional-assignment locals (Epic: Bugfix plan: RuboCop Style/GuardClause conditional-assignment locals)

#### Description

Implement bugfix in upstream rubocop/rubocop so `Style/GuardClause` does not register offenses (or attempt autocorrection) when the `if` condition assigns local variables that are later referenced in the `then` branch.

Primary regression cases (from task_3 CSV patch):
- `if (foo = bar)` ... `return foo`
- `if (foo = bar && baz = qux)` ... `return [foo, baz]`

Acceptance:
- New/updated specs in `spec/rubocop/cop/style/guard_clause_spec.rb` pass, especially the two `expect_no_offenses` examples.
- No regressions: existing `Style/GuardClause` spec suite remains green.

Implementation constraints:
- Keep changes localized to `lib/rubocop/cop/style/guard_clause.rb` (and related helpers within the same cop if present).
- Prefer conservative skip behavior when safety is uncertain.

Notes on repo context:
- This repository only contains the task CSV + patch; actual implementation happens in upstream `rubocop/rubocop` repo following file paths referenced above.


### 4. Implement safety check in Style/GuardClause (skip when condition assigns locals used in branch) (Epic: Fix Style/GuardClause false positives with conditional-assignment locals)

#### Description

Modify `Style/GuardClause` cop implementation so it does not register an offense when the `if` condition contains local variable assignments that are later referenced in the `then` branch.

Files (upstream):
- `lib/rubocop/cop/style/guard_clause.rb` (or the current implementation file)

Algorithm (AST-based):
- For each `if` candidate considered convertible to a guard clause:
  1) Collect names of locals assigned within the condition:
     - Traverse `if_node.condition` descendants and gather `lvasgn` nodes.
     - Must work with parentheses (`begin`) and boolean operator nodes (`and`/`or`/`&&`/`||`).
  2) If no assignments: keep existing behavior.
  3) If assignments exist:
     - Traverse the `then` branch body for `lvar` nodes referencing any of those names.
     - If any are found: treat conversion as unsafe -> do not register offense and do not autocorrect.

Acceptance:
- New regression specs pass.
- Existing `Style/GuardClause` specs remain green.


### 5. Run Style/GuardClause specs and ensure no regressions (Epic: Fix Style/GuardClause false positives with conditional-assignment locals)

#### Description

Validate behavior against upstream test suite.

Acceptance:
- `bundle exec rspec spec/rubocop/cop/style/guard_clause_spec.rb` passes including new examples.
- No unexpected behavior changes in existing examples.


### 6. Bugfix plan: RuboCop Style/GuardClause conditional-assignment locals

#### Description

Ticket tree for fixing rubocop/rubocop `Style/GuardClause` so it avoids unsafe/incorrect guard-clause suggestions when the `if` condition assigns locals that are then used in the branch.

This plan is derived from spec coverage described by `tasks/task_3_rubocop_rubocop.csv` in this repo; the CSV content itself is truncated in this environment, so we are explicitly scoping to what the patch implies.

Overall acceptance:
- `bundle exec rspec spec/rubocop/cop/style/guard_clause_spec.rb` passes with the newly added `expect_no_offenses` examples.
- No regression in existing Style/GuardClause behavior (relevant spec suite remains green).


### 7. Helper: detect reads of those locals in the then-branch (Epic: Fix Style/GuardClause false positives with conditional-assignment locals)

#### Description

Add a helper method that checks whether the `then` branch reads (`lvar`) any names assigned in the condition.

Done when:
- True for branch containing `return foo` when `foo` assigned in condition.
- True for `return [foo, baz]` when both names assigned.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Helper: collect assigned local var names from condition AST
    - current (in progress task): Helper: detect reads of those locals in the then-branch <-
    - upcoming (not yet): Integrate safety check into offense registration/autocorrection path
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement a helper in upstream `Style/GuardClause` that determines whether the `then` branch **reads** any local variables that were **assigned in the `if` condition** (to detect unsafe guard-clause transformations).

##### Scope / Location
- Upstream `rubocop/rubocop`.
- Implement in `lib/rubocop/cop/style/guard_clause.rb`, close to the helper from task (12).
- No behavior changes yet to offense logic beyond exposing this helper; integration is task (14).

##### Technical Specs
- Add a helper method (private) that:
  - Inputs:
    - `then_branch_node` (the `if` node’s `body` / `then_branch`)
    - `assigned_names` from task (12) (array/set of symbols)
  - Output:
    - boolean: `true` if any `lvar` node in the then-branch references a name in `assigned_names`, else `false`.
- Traversal details:
  - Must scan the entire then-branch subtree (`then_branch_node.each_descendant(:lvar)` or equivalent).
  - Must handle branch shapes:
    - Single expression (`return foo`)
    - `begin` blocks (multiple statements)
    - nested expressions like arrays/hashes (`return [foo, baz]`)
- Safety behavior:
  - If `then_branch_node` is `nil`, return `false` (no reads).
  - If `assigned_names` empty, return `false`.

##### Implementation Checklist
- [ ] Add helper such as `then_branch_reads_assigned_lvars?(then_branch_node, assigned_names)`.
- [ ] Normalize `assigned_names` to a `Set` internally for O(1) membership checks (without changing external return type of task 12 if it returns an Array).
- [ ] Implement traversal using AST descendant enumeration, not string matching.
- [ ] Ensure the helper only checks `lvar` reads, not assignments (`lvasgn`) in the branch.

##### Success Criteria (verifiable)
- [ ] Returns `true` when condition assigns `foo` and the branch contains `return foo`.
- [ ] Returns `true` when condition assigns `foo` and `baz` and the branch contains `return [foo, baz]`.
- [ ] Returns `false` when branch does not reference any of the assigned names.
- [ ] No existing `Style/GuardClause` specs regress.

##### Files to modify
- `lib/rubocop/cop/style/guard_clause.rb`


### 8. Integrate safety check into offense registration/autocorrection path (Epic: Fix Style/GuardClause false positives with conditional-assignment locals)

#### Description

Wire the new helpers into the cop’s existing logic that decides to add an offense and/or autocorrect.

Done when:
- New regression specs pass.
- Existing specs expecting offenses still get offenses.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Helper: detect reads of those locals in the then-branch
    - current (in progress task): Integrate safety check into offense registration/autocorrection path <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Integrate the conditional-assignment safety check into `Style/GuardClause` so the cop **does not register an offense and does not autocorrect** when converting to a guard clause would be unsafe because the `if` condition assigns locals that are later read in the `then` branch.

##### Scope / Location
- Upstream `rubocop/rubocop`.
- Modify only the `Style/GuardClause` cop implementation and keep the change minimal and conservative.
- Use helpers from tasks (12) and (13).

##### Technical Specs
- Identify where `Style/GuardClause` decides:
  - an `if` node is a candidate for guard clause conversion
  - to `add_offense` and/or to autocorrect
- Before registering an offense / proposing correction, add a safety gate:
  1) Compute `assigned = assigned_lvar_names_in_condition(if_node.condition)`
  2) If `assigned` empty: proceed with existing behavior unchanged
  3) If `assigned` non-empty and `then_branch_reads_assigned_lvars?(if_node.body, assigned)` is `true`:
     - treat as unsafe conversion
     - do **not** add offense
     - do **not** autocorrect
     - do not alter other logic for unrelated cases

##### Implementation Checklist
- [ ] Locate the exact method(s) in `lib/rubocop/cop/style/guard_clause.rb` where offenses are registered (commonly `on_if`, a matcher callback, or a conversion/candidate predicate).
- [ ] Introduce a narrowly-scoped predicate, e.g. `unsafe_due_to_conditional_assignment?(if_node)` that composes the two helpers, to keep `on_if` readable.
- [ ] Ensure the guard applies to both:
  - offense detection (linting)
  - autocorrection path (if separate)
- [ ] Ensure this check runs only for the relevant `if` shape considered convertible to a guard clause; do not broaden scope to all `if`s unnecessarily.

##### Success Criteria (verifiable)
- [ ] The two regression examples added in `spec/rubocop/cop/style/guard_clause_spec.rb` (conditional assignment in condition; later read in branch) pass with `expect_no_offenses`.
- [ ] Existing spec cases that previously expected an offense still receive an offense (no broad suppression).
- [ ] Autocorrect behavior remains unchanged for safe cases (verified by existing autocorrect specs staying green).
- [ ] Running `bundle exec rspec spec/rubocop/cop/style/guard_clause_spec.rb` is green.

##### Files to modify
- `lib/rubocop/cop/style/guard_clause.rb`
