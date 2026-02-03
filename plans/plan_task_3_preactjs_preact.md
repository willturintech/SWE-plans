# Plan Name: Identify and Plan Bug Fix from Preact CSV File

## Tasks

### 1. Reproduce crash + capture failing code path (Epic: Fix contentEditable prop removal (true → undefined/null) without crash; match React semantics)

#### Description

Pin down where the throw originates when toggling `contentEditable` from `true` → `undefined`/`null`.

Implementation steps:
- Run the browser test suite (or targeted test) that includes the new regression case (#2926).
- Confirm the exception message and stack trace.
- Identify the code path applying/removing props for DOM elements (commonly `setAccessor` / `setProperty` in `src/diff/props.js` or equivalent).

Acceptance criteria:
- You can point to the exact function/branch that throws when `contentEditable` becomes `null`/`undefined`.
- Notes added (as code comments or in PR description) describing why the crash occurs.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Reproduce crash + capture failing code path <-
    - upcoming (not yet): Implement safe unsetting behavior for contentEditable
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Reproduce the `contentEditable` crash and document the exact failing code path in Preact’s DOM prop diffing.

##### Technical Specs
- **Target behavior under investigation:** updating an existing DOM node from `contentEditable={true}` to `contentEditable={undefined}` and `contentEditable={null}`.
- **Likely area of code:** DOM props/attributes application & removal (commonly `src/diff/props.js` and helpers such as `setAccessor`, `setProperty`, or equivalent).

##### Implementation Checklist
- [ ] Run the browser test suite (or a targeted run) that includes the new regression case for #2926 in `test/browser/render.test.js`.
- [ ] Capture the thrown exception details:
  - exact error message
  - full stack trace
  - the DOM element type involved (e.g., `div`)
  - the old/new prop values in the failing transition (`true -> undefined`, `true -> null`)
- [ ] Identify the precise function and branch where the exception occurs:
  - name the function (e.g., `setAccessor`)
  - point to the conditional branch (e.g., “property assignment path when value is null/undefined”)
  - note whether it is failing on property assignment, attribute removal, or normalization/conversion logic
- [ ] Add concise notes explaining *why* the crash occurs:
  - either as a short code comment at the relevant branch, or
  - as PR description notes (keep them technical and directly tied to the stack trace and DOM semantics)

##### Success Criteria
- [ ] The failing test reliably reproduces the crash before the fix (no flakiness, no timing dependence introduced).
- [ ] The exact throwing function and branch are identified and can be referenced for the fix work.
- [ ] A clear explanation exists (comment or PR notes) describing the root cause (e.g., invalid assignment/removal semantics for `contentEditable` when transitioning from boolean to unset).

##### Files to Read
- `test/browser/render.test.js`
- DOM props diffing implementation (commonly `src/diff/props.js` and related helpers)

---


### 2. user query

#### Description

Locate task_3_preactjs_preact.csv and create a plan to fix the bug described inside.


### 3. Fix contentEditable prop removal (true → undefined/null) without crash; match React semantics (Epic: user query)

#### Description

Implement a fix in Preact DOM property/attribute diffing so that updating `contentEditable` from `true` to `undefined`/`null` does not throw and resets to the default state. Must satisfy new regression test in `test/browser/render.test.js` (#2926): rerender with `contentEditable={undefined}` and `{null}` should not throw and resulting DOM should have `element.contentEditable === 'inherit'`.

Notes:
- Bug likely occurs in the props application/removal path (commonly `setProperty`/`setAccessor`/diff props) when handling `null`/`undefined` for properties that are *string-ish* but accept booleans in HTML.
- React behavior: removing `contentEditable` reverts to default, which the DOM exposes as `'inherit'`.
- This ticket is scoped to implementation and tests only (no external configuration required).


### 4. Add/verify regression test coverage for contentEditable removal (true → undefined/null) (Epic: user query)

#### Description

Ensure the regression test in `test/browser/render.test.js` exists and correctly captures the expected behavior:
- Start with an element rendered with `contentEditable={true}`.
- Rerender same element with `contentEditable={undefined}` and assert: no exception and `element.contentEditable === 'inherit'`.
- Repeat with `contentEditable={null}`.

If test already exists (per task statement), confirm it is stable and aligned with expected behavior across browsers in the test environment.

Deliverable: test passes in CI/local test run once fix is applied.


### 5. Implement safe unsetting behavior for contentEditable (Epic: Fix contentEditable prop removal (true → undefined/null) without crash; match React semantics)

#### Description

Change prop application/removal so unsetting `contentEditable` does not throw and restores default behavior.

Implementation guidance (keep minimal and targeted):
- Detect when prop name is `contentEditable` and new value is `null`/`undefined`.
- Ensure the DOM ends up in the same state as React when the prop is removed:
  - no exception during diff
  - resulting `element.contentEditable === 'inherit'`
- Prefer removing the attribute and/or setting the property to the correct default in a way that works across browsers supported by Preact tests.

Acceptance criteria:
- Rerendering with `contentEditable={undefined}` and `{null}` does not throw.
- `element.contentEditable` reads as `'inherit'` after rerender.
- No regressions in other prop removal behavior (e.g., boolean/string attributes).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Reproduce crash + capture failing code path
    - current (in progress task): Implement safe unsetting behavior for contentEditable <-
    - upcoming (not yet): Add focused unit/regression assertions if needed (beyond #2926)
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement a minimal, targeted fix so that unsetting `contentEditable` (transition from `true` to `undefined`/`null`) does not throw and matches React’s semantics (DOM reads `element.contentEditable === 'inherit'`).

##### Technical Specs
- **Scope:** Preact DOM prop application/removal logic only.
- **Required semantics:** when `contentEditable` is removed (set to `undefined` or `null`), the element must revert to default behavior such that `element.contentEditable` reports `'inherit'`.
- **Safety constraint:** avoid broad changes to generic prop removal that could affect other attributes/properties; prefer a targeted handling for `contentEditable`.

##### Implementation Checklist
- [ ] Locate the prop diffing/removal code path used when a prop is updated on an existing element (where the crash was observed in task (4)).
- [ ] Add targeted handling for the `contentEditable` prop when the *new value* is `null` or `undefined`:
  - ensure no exception is thrown during the update
  - ensure the DOM ends in the expected state (React-like reset)
- [ ] Prefer an approach that is stable across the browsers/environments used by the test runner:
  - remove the attribute and/or set the property to a default value that results in `'inherit'` being reported
  - keep logic localized to `contentEditable` (do not change normalization rules for unrelated props unless strictly necessary)
- [ ] Ensure both transitions are covered by the fix:
  - `true -> undefined`
  - `true -> null`
- [ ] Keep behavior consistent for other `contentEditable` values (e.g., `true`, `false`, string values) unless the existing behavior is already incorrect and directly implicated by the crash.

##### Success Criteria
- [ ] Rerendering with `contentEditable={undefined}` does not throw.
- [ ] Rerendering with `contentEditable={null}` does not throw.
- [ ] After each rerender, `element.contentEditable === 'inherit'` (as asserted by the regression test).
- [ ] No regressions in other prop/attribute removal behaviors (spot-check by running existing render tests; changes remain narrowly scoped to `contentEditable`).

##### Files to Modify
- DOM props diffing implementation (commonly `src/diff/props.js` or the module identified in task (4))

---


### 6. Add focused unit/regression assertions if needed (beyond #2926) (Epic: Fix contentEditable prop removal (true → undefined/null) without crash; match React semantics)

#### Description

If the existing regression test is too coarse or flakes across environments, add a focused assertion nearby to lock in the expected DOM behavior.

Scope:
- Keep additions within `test/browser/render.test.js`.
- Avoid browser-specific assumptions other than `element.contentEditable` resolving to `'inherit'` after unsetting.

Acceptance criteria:
- Tests are deterministic in the existing test runner.
- The regression precisely covers `true -> undefined` and `true -> null` transitions.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement safe unsetting behavior for contentEditable
    - current (in progress task): Add focused unit/regression assertions if needed (beyond #2926) <-
    - upcoming (not yet): Run full relevant test suite and confirm no collateral failures
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Harden the regression coverage in `test/browser/render.test.js` only if the existing #2926 test is too coarse or shows flakiness across environments; ensure deterministic assertions for `contentEditable` unsetting.

##### Technical Specs
- **Test file scope constraint:** all additions must remain in `test/browser/render.test.js`.
- **Allowed browser assumption:** after unsetting, `element.contentEditable` resolves to `'inherit'`.
- **Prohibited patterns:** timing-based assertions, reliance on async scheduling unless the surrounding suite already does so.

##### Implementation Checklist
- [ ] Evaluate the current #2926 test behavior in the local runner:
  - verify it deterministically fails pre-fix and passes post-fix
  - check for environment-specific differences (e.g., attribute vs property reflection timing)
- [ ] If needed, add focused assertions to precisely lock in the transition semantics:
  - start from `contentEditable={true}` on an element
  - rerender the *same element* with `contentEditable={undefined}` and assert:
    - rerender does not throw
    - `element.contentEditable === 'inherit'`
  - repeat for `contentEditable={null}`
- [ ] Use existing test helpers/patterns in `render.test.js` (scratch container setup, rerender mechanism, assertion style).
- [ ] Avoid over-specifying DOM internals (e.g., avoid asserting exact attribute presence/absence if it varies); the primary invariant is the property value `'inherit'` and lack of exceptions.

##### Success Criteria
- [ ] Tests are deterministic in the existing test runner (no flaky timing dependencies).
- [ ] The regression precisely covers both transitions:
  - `true -> undefined`
  - `true -> null`
- [ ] The test suite clearly distinguishes pre-fix failure from post-fix success.

##### Files to Modify
- `test/browser/render.test.js`

---


### 7. Run full relevant test suite and confirm no collateral failures (Epic: Fix contentEditable prop removal (true → undefined/null) without crash; match React semantics)

#### Description

Validate the fix against the broader test suite to ensure prop diffing changes didn’t break other behaviors.

Implementation steps:
- Run the full browser render tests (or full test suite if that is the project norm).
- If failures occur, adjust fix to be more targeted to `contentEditable` only.

Acceptance criteria:
- All existing tests pass locally.
- Regression test #2926 passes.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add focused unit/regression assertions if needed (beyond #2926)
    - current (in progress task): Run full relevant test suite and confirm no collateral failures <-
    - upcoming (not yet): Confirm/land test case for contentEditable removal
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run the relevant test suite(s) to validate that the `contentEditable` fix does not introduce collateral regressions in prop diffing, and adjust the fix to be more targeted if any failures appear.

##### Technical Specs
- **Goal:** confirm no unintended behavior changes outside `contentEditable` unsetting.
- **Priority:** correctness and compatibility with existing tests over refactoring.

##### Implementation Checklist
- [ ] Run the full browser render tests (or the project’s standard full test suite for DOM rendering changes).
- [ ] Confirm #2926 regression coverage passes as part of the run.
- [ ] If any unrelated tests fail:
  - identify whether the failure is caused by generalized prop removal logic changes
  - narrow the implementation so only `contentEditable` unsetting behavior is special-cased
  - rerun the failing subset and then the broader suite
- [ ] Ensure no new warnings/errors are introduced during test execution (where the test runner captures console output).

##### Success Criteria
- [ ] All existing tests pass locally (according to project norms for “green”).
- [ ] Regression test #2926 passes.
- [ ] Any adjustments made are targeted (no broad semantic changes to unrelated props/attributes).


### 8. Confirm/land test case for contentEditable removal (Epic: Add/verify regression test coverage for contentEditable removal (true → undefined/null))

#### Description

Work in `test/browser/render.test.js` to ensure the regression test for #2926 is present and correct.

Implementation steps:
- Locate (or add) a test that renders an element with `contentEditable={true}`.
- Rerender the same element with `contentEditable={undefined}` and assert:
  - rerender does not throw
  - `element.contentEditable === 'inherit'`
- Repeat for `contentEditable={null}`.
- Keep the assertions consistent with other render tests (e.g., use existing helpers/scratch DOM setup).

Acceptance criteria:
- This subtest fails on the buggy behavior and passes after the fix.
- No flakiness (no reliance on timing/async unless the suite already does).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Run full relevant test suite and confirm no collateral failures
    - current (in progress task): Confirm/land test case for contentEditable removal <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Quickly ensure a deterministic regression test exists in `test/browser/render.test.js` for Preact issue **#2926**: updating an element’s `contentEditable` prop from `true` to `undefined`/`null` must **not throw** and must reset the DOM state so `element.contentEditable === 'inherit'`.

##### Technical Specs

###### Test location
- Update **only**: `test/browser/render.test.js`
- Place the test near other prop-diff / DOM property update tests for consistency.

###### Test behavior to cover
- Initial render: an element with `contentEditable={true}`
- Rerender same element (same DOM node) with:
  1) `contentEditable={undefined}`
  2) `contentEditable={null}`
- For each rerender, assert:
  - rerender does **not throw**
  - `element.contentEditable === 'inherit'`

###### Consistency requirements
- Use the existing test harness patterns in this file:
  - same render/rerender API used elsewhere (no custom mounting logic)
  - same scratch container setup/teardown helpers
  - same assertion library and style as surrounding tests

##### Implementation Checklist
- [ ] Locate an existing test for `contentEditable` prop updates/removal; if present, verify it matches the required transitions (`true → undefined` and `true → null`) and assertions.
- [ ] If no suitable test exists, add a new `it(...)` test case with a clear name referencing `contentEditable` removal and/or `#2926`.
- [ ] Ensure the test reuses the *same element instance* across rerenders (verify by holding a DOM reference and checking it remains the same node after rerender, if that’s consistent with local test conventions).
- [ ] Wrap rerender calls in an assertion that guarantees “does not throw” using the suite’s existing pattern (avoid ad-hoc try/catch if the file uses a standard helper).
- [ ] Add the two required DOM assertions after rerender:
  - `element.contentEditable` equals `'inherit'` after setting `undefined`
  - `element.contentEditable` equals `'inherit'` after setting `null`
- [ ] Avoid timing/async constructs (no `setTimeout`, no waiting for microtasks) unless the surrounding tests already require it for rerender semantics.

##### Success Criteria
- [ ] The test is present in `test/browser/render.test.js` and is easy to understand/review.
- [ ] On the **buggy** implementation, the test reproduces the issue (fails due to thrown error and/or incorrect `contentEditable` value).
- [ ] After the fix in the implementation ticket, the test passes reliably.
- [ ] No flakiness: the test is deterministic and does not depend on browser timing or environment-specific behavior beyond the expected `'inherit'` value.

##### Notes / Guardrails
- Treat `element.contentEditable` as the canonical observable (per requirements). Do not replace this with attribute-only checks unless the file’s conventions require both; the required assertion remains `=== 'inherit'`.
- Keep the scope limited to this regression. Do not add broader refactors or unrelated assertions.

##### Files to Modify
- `test/browser/render.test.js`
