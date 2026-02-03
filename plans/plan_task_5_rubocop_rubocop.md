# Plan Name: Debug Fix Planning for RuboCop CSV Task

## Tasks

### 1. Update Style/SafeNavigation specs for new no-offense example and regression coverage (Epic: Fix Style/SafeNavigation autocorrect to avoid violating Lint/SafeNavigationChain)

#### Description

In `spec/rubocop/cop/style/safe_navigation_spec.rb`:

1) Add the new no-offense example from the task patch:
- Input: `var && var.one.two.three&.four`
- Expectation: `expect_no_offenses` (Style/SafeNavigation must not flag this pattern).

2) Add a regression spec demonstrating the problematic interaction:
- Use an input that Style/SafeNavigation would normally autocorrect, but where the resulting code would be an overlong safe-navigation chain, e.g. starting from a guard form that, if converted, becomes `foo&.bar&.abc&.xyz&.name`.
- Expectation: Style/SafeNavigation registers an offense but produces **no correction** (`expect_no_corrections`), or marks it as not autocorrectable per RuboCop spec conventions.

Acceptance:
- Spec file passes when run in isolation.
- Regression spec fails on the buggy behavior (baseline) and passes with the fix.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Update Style/SafeNavigation specs for new no-offense example and regression coverage <-
    - upcoming (not yet): Locate the exact autocorrect path in Style/SafeNavigation and chain-length rules in Lint/SafeNavigationChain
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Update `spec/rubocop/cop/style/safe_navigation_spec.rb` to cover (a) a newly allowed pattern that must not be flagged and (b) a regression where Style/SafeNavigation must not autocorrect because it would create an overlong safe-navigation chain.

##### Technical Specs
- **Area:** RSpec cop specs for `RuboCop::Cop::Style::SafeNavigation`
- **File:** `spec/rubocop/cop/style/safe_navigation_spec.rb`
- **New coverage required:**
  1) **No-offense example**
     - Input Ruby: `var && var.one.two.three&.four`
     - Expectation: `expect_no_offenses` (Style/SafeNavigation must not register an offense)
  2) **Regression: offense but no correction**
     - Choose a guard-form input that Style/SafeNavigation would normally autocorrect into a long `&.` chain (e.g. would become `foo&.bar&.abc&.xyz&.name`).
     - Expectation: offense is registered, but **no autocorrection is produced** (`expect_no_corrections` / “not autocorrectable” per existing spec conventions in this file).

##### Implementation Checklist
- [ ] Add an `expect_no_offenses` example for `var && var.one.two.three&.four`.
- [ ] Add a regression example that:
  - [ ] Asserts an offense is detected by Style/SafeNavigation (use `expect_offense` with clear caret/annotation as in existing specs).
  - [ ] Asserts no correction is applied (`expect_no_corrections`), ensuring the cop does not rewrite into an overlong `&.` chain.
- [ ] Keep spec style consistent with surrounding contexts (e.g., `context 'when ...'` blocks and existing helper methods).

##### Success Criteria
- [ ] `bundle exec rspec spec/rubocop/cop/style/safe_navigation_spec.rb` passes.
- [ ] Regression spec would fail against the buggy behavior (i.e., when autocorrect incorrectly produces the long chain), and passes once the fix is implemented.

##### Notes
- The regression should be minimal and deterministic: use a single expression whose autocorrect output would exceed the safe-navigation chain length limit enforced elsewhere (do not rely on external config changes).

---


### 2. Fix Style/SafeNavigation autocorrect to avoid violating Lint/SafeNavigationChain

#### Description

RuboCop ~1.68.0 introduced/strengthened safe navigation chain rules (Lint/SafeNavigationChain). Style/SafeNavigation’s autocorrect can now produce a long `&.` chain (e.g., `foo&.bar&.abc&.xyz&.name`) that triggers the chain-length cop, effectively introducing new offenses.

Goal: update Style/SafeNavigation autocorrect so that it does not introduce a navigation-chain-length offense. Preferred behavior: if the correction would create a too-long safe-navigation chain, do not autocorrect that offense (leave original guard-form). Add/adjust specs in `spec/rubocop/cop/style/safe_navigation_spec.rb` (as per the provided patch) and add regression coverage for the long-chain case.

Non-goals: changing default config for chain-length cop; complex refactors (temp vars/guard clauses) unless required by existing RuboCop patterns.


### 3. Locate the exact autocorrect path in Style/SafeNavigation and chain-length rules in Lint/SafeNavigationChain (Epic: Fix Style/SafeNavigation autocorrect to avoid violating Lint/SafeNavigationChain)

#### Description

In the RuboCop codebase (rubocop/rubocop):

- Locate the cop implementation files:
  - `RuboCop::Cop::Style::SafeNavigation` (autocorrect logic that transforms `obj && obj.foo` into `obj&.foo`).
  - `RuboCop::Cop::Lint::SafeNavigationChain` (or whichever cop enforces chain length in the target version).

- Determine:
  - How Lint/SafeNavigationChain computes chain length (AST traversal rules).
  - The default maximum chain length and whether it is configurable.
  - What exact chain pattern triggers the offense (counting only `&.` segments vs all segments, etc.).

- Identify where in Style/SafeNavigation autocorrect the `&.` is introduced and what node represents the full call chain being modified.

Acceptance:
- A short note in code comments or commit message-quality description mapping “input pattern -> corrected output -> chain-length evaluation”.
- The implementation point for adding a pre-correction guard is clear.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Update Style/SafeNavigation specs for new no-offense example and regression coverage
    - current (in progress task): Locate the exact autocorrect path in Style/SafeNavigation and chain-length rules in Lint/SafeNavigationChain <-
    - upcoming (not yet): Implement a conservative autocorrect guard to avoid producing overlong safe-navigation chains
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate and document the exact autocorrect path in `RuboCop::Cop::Style::SafeNavigation` and the chain-length enforcement logic in the relevant chain-length cop (expected: `RuboCop::Cop::Lint::SafeNavigationChain`) to enable a safe pre-autocorrect guard.

##### Technical Specs
- **Targets to locate:**
  - `RuboCop::Cop::Style::SafeNavigation`
    - Identify where the cop:
      - detects the guard pattern (e.g., `obj && obj.foo`)
      - builds the corrected safe-nav form (`obj&.foo`)
      - applies autocorrection (corrector usage / node replacement)
  - `RuboCop::Cop::Lint::SafeNavigationChain` (or the actual cop name in this version)
    - Identify:
      - how it traverses the AST to compute chain length
      - what exactly is counted (only `csend` / `&.` segments vs all call segments)
      - default maximum allowed chain length and whether it’s configurable (and config key name)
      - what shape of node triggers the offense (e.g., `csend` chaining, mix of `send` and `csend`, parentheses, blocks)

##### Implementation Checklist
- [ ] Find the implementation files for both cops in the repository.
- [ ] Write a short, reviewable note (commit-message quality) that maps:
  - [ ] an example guard-form input
  - [ ] the exact autocorrected output Style/SafeNavigation would produce
  - [ ] how the chain-length cop evaluates that output and why it becomes an offense
- [ ] Identify the precise insertion point for a pre-correction guard in Style/SafeNavigation (method name + what node is available there).

##### Success Criteria
- [ ] A concise code comment or internal note exists (in the cop file or adjacent documentation) that captures “input -> corrected output -> chain-length evaluation”.
- [ ] The implementation point for adding the guard is unambiguous (method + node/AST shape to inspect).

##### Non-goals
- Do not implement behavior changes in this task; focus on traceability and clarity for the subsequent fix.

---


### 4. Implement a conservative autocorrect guard to avoid producing overlong safe-navigation chains (Epic: Fix Style/SafeNavigation autocorrect to avoid violating Lint/SafeNavigationChain)

#### Description

Modify Style/SafeNavigation autocorrect to skip correction when it would cause the corrected expression to violate the chain-length rules.

Implementation approach:
- Before applying autocorrection, compute the *resulting* safe-navigation chain length for the would-be corrected node.
- If it would exceed the max allowed by Lint/SafeNavigationChain, do not register an autocorrection (leave original code unchanged).

Guidelines:
- Prefer reusing helper methods from Lint/SafeNavigationChain if accessible (shared logic / modules). If not accessible, implement a small helper in Style/SafeNavigation that mirrors the chain counting semantics.
- The guard should be narrowly applied so that normal conversions (short chains) still autocorrect as before.

Acceptance:
- Running autocorrect for Style/SafeNavigation on the regression input produces no correction.
- No new failures in existing Style/SafeNavigation autocorrect specs.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate the exact autocorrect path in Style/SafeNavigation and chain-length rules in Lint/SafeNavigationChain
    - current (in progress task): Implement a conservative autocorrect guard to avoid producing overlong safe-navigation chains <-
    - upcoming (not yet): Add targeted edge-case tests and run relevant spec suite
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement a conservative safeguard in `RuboCop::Cop::Style::SafeNavigation` autocorrect so that it does not introduce a chain-length offense (e.g., under `Lint/SafeNavigationChain`). If applying autocorrect would produce an overlong safe-navigation chain, the cop must leave the original guard-form code unchanged.

##### Technical Specs
- **Area:** `RuboCop::Cop::Style::SafeNavigation` autocorrection logic
- **Behavioral requirement:**
  - Before performing an autocorrection, compute the safe-navigation chain length of the *resulting* corrected expression.
  - If the resulting chain length would exceed the maximum allowed by the chain-length cop, skip autocorrection for that offense.
- **Implementation guidance:**
  - Prefer reusing chain-length computation logic from the chain-length cop if it’s accessible/shared.
  - Otherwise, implement a small helper local to Style/SafeNavigation that mirrors the chain-length cop’s semantics exactly (avoid “almost the same” counting rules).

##### Implementation Checklist
- [ ] Identify the autocorrect method/path that constructs the replacement source (or replacement node) for `obj && obj.foo`.
- [ ] Add a “preflight” step:
  - [ ] derive/construct the would-be corrected node or source
  - [ ] compute the resulting safe-navigation chain length as the chain-length cop would
  - [ ] compare against the chain-length maximum (including config/defaults used by the chain-length cop)
- [ ] If it would exceed the limit:
  - [ ] ensure the cop still registers the offense (as per spec) but does **not** provide an autocorrection
  - [ ] ensure no partial edits are applied
- [ ] If it does not exceed the limit:
  - [ ] preserve existing autocorrect behavior
- [ ] Keep the guard narrowly scoped to this interaction; avoid changing unrelated matching/correction cases.

##### Success Criteria
- [ ] The regression spec from task (3) observes **no correction** for the long-chain case.
- [ ] Existing Style/SafeNavigation autocorrect specs continue to pass (no behavior regressions for short/normal chains).
- [ ] The guard’s chain-length counting matches the chain-length cop’s counting rules (reviewable via code comparison or shared helper usage).

##### Non-goals
- Do not introduce complex rewrites (temp variables, refactoring guard clauses) as alternative corrections unless consistent with existing RuboCop patterns and strictly required.

---


### 5. Add targeted edge-case tests and run relevant spec suite (Epic: Fix Style/SafeNavigation autocorrect to avoid violating Lint/SafeNavigationChain)

#### Description

Add 1–2 targeted tests (only if needed after implementing the guard) to ensure the guard doesn’t over-block valid autocorrections.

Suggested edge cases:
- Mixed dot and safe-nav where only the last call is safe-nav (`a.b.c&.d`) must not be rewritten into multiple `&.` segments.
- Parentheses / blocks that affect call chain parsing.

Then run:
- `bundle exec rspec spec/rubocop/cop/style/safe_navigation_spec.rb`
- Any directly relevant Lint/SafeNavigationChain spec files if impacted.

Acceptance:
- All added/modified tests pass.
- The fix demonstrably prevents Style/SafeNavigation from introducing a new Lint/SafeNavigationChain offense via autocorrect.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement a conservative autocorrect guard to avoid producing overlong safe-navigation chains
    - current (in progress task): Add targeted edge-case tests and run relevant spec suite <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add 1–2 targeted edge-case specs (only if needed) to ensure the new “skip autocorrect if it would exceed chain length” guard is not overly broad, and verify the relevant spec suite passes.

##### Technical Specs
- **Primary file:** `spec/rubocop/cop/style/safe_navigation_spec.rb`
- **Edge cases to consider (choose 1–2 that best validate guard precision):**
  - Mixed dot + safe-nav where only the last call is safe-nav: `a.b.c&.d`
    - Ensure Style/SafeNavigation does not rewrite into multiple `&.` segments or otherwise change semantics.
  - Parentheses and/or blocks that affect chain parsing:
    - e.g., chained calls with parentheses, or a call with a block in the chain (only if Style/SafeNavigation supports matching/correcting in such forms).

##### Implementation Checklist
- [ ] Add 1–2 focused spec examples that:
  - [ ] would be autocorrected normally and should still be autocorrected after the change, **or**
  - [ ] should not be corrected and must remain uncorrected, but for reasons other than chain-length (ensuring the new guard isn’t the cause)
- [ ] Ensure the examples explicitly assert correction/no-correction using existing spec helpers (`expect_correction`, `expect_no_corrections`, etc.).
- [ ] Run:
  - [ ] `bundle exec rspec spec/rubocop/cop/style/safe_navigation_spec.rb`
  - [ ] any directly related specs for the chain-length cop if the change touched shared logic or behavior (only if impacted).

##### Success Criteria
- [ ] All added/modified tests pass locally.
- [ ] Added tests demonstrate the new guard does not block valid/short safe-navigation autocorrections.
- [ ] Overall behavior confirms Style/SafeNavigation autocorrect no longer introduces a new chain-length offense.
