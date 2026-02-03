# Plan Name: Debug PreactJS CSV File: Locate and Fix task_5_preactjs_preact.csv

## Tasks

### 1. Run full suite and confirm no prop/attr regressions (Epic: Run full test suite and add guard checks for regressions in prop/attr handling)

#### Description

Execute the repository’s full test suite (or CI-equivalent) after the tabIndex fix lands.

Validate specifically:
- No failures in other prop/attribute tests.
- Boolean attribute removal behavior remains unchanged.
- Numeric property updates (including 0) still behave as expected.

Acceptance:
- Full suite green.
- If any failures occur, add one narrowly-scoped regression test and adjust fix with minimal blast radius.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Run full suite and confirm no prop/attr regressions <-
    - upcoming (not yet): Reproduce regression and identify current prop removal behavior for tabIndex/tabindex
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Execute the repository’s full automated test coverage after the `tabIndex` null/undefined reset fix has landed, and confirm there are no regressions in prop/attribute diffing behavior.

##### Technical Specs
- **Test execution**
  - Run the full suite used by the repo (CI-equivalent). If the repo distinguishes tiers, run at minimum browser/render tests plus the default `npm test`/`pnpm test` pipeline used in CI.
- **Targeted validations (must explicitly verify)**
  - **Prop/attr suite health:** no new failures in tests covering attribute/property application/removal.
  - **Boolean attribute removal:** ensure behavior for boolean attributes remains unchanged (e.g., setting to `false`/`null`/`undefined` should not leave stale attributes or stringify values).
  - **Numeric property updates:** ensure numeric props still handle `0` correctly (e.g., `0 -> other number -> 0` and `0 -> null/undefined` behavior remains consistent with prior expectations outside `tabIndex`).

##### Implementation Checklist
- [ ] Pull the branch/commit that includes the `tabIndex` fix and the regression test.
- [ ] Run the full test suite locally (or the same commands CI uses).
- [ ] If failures occur, classify them:
  - pre-existing flakes vs. deterministic regressions introduced by the fix
  - failures in prop/attr handling tests vs. unrelated areas
- [ ] For deterministic regressions related to the fix:
  - add **one narrowly-scoped regression test** that captures the prior correct behavior (avoid broad snapshots)
  - adjust the fix with minimal blast radius (do not introduce generic null/undefined normalization)

##### Success Criteria
- [ ] Full suite completes successfully (green).
- [ ] No new failures in prop/attribute related tests.
- [ ] Boolean attribute removal behavior unchanged.
- [ ] Numeric property updates (including `0`) behave as expected.
- [ ] If a regression is found, it is fixed with a minimal change and protected by a narrow regression test.

---


### 2. Fix tabIndex reset on null/undefined during rerender (preactjs/preact) (Epic: user query)

#### Description

Implement and validate a fix in Preact DOM prop diffing/patching so that rerendering an element with `tabIndex={undefined}` or `tabIndex={null}` (and lowercase `tabindex`) resets/removes the DOM `tabIndex` property to its default value (`-1`), instead of leaving it at `0`.

Context / failing regression test:
- Test added in `test/browser/render.test.js`: "should reset tabindex on undefined/null" (#3060)
- Scenario:
  1) render `<div tabIndex={0} />` => expect `el.tabIndex === 0`
  2) rerender with `{ tabIndex: undefined }` then `{ tabIndex: null }` => expect `el.tabIndex === -1`
  3) repeat with lowercase prop `tabindex`

Constraints:
- Preserve existing behavior for other props/attributes (no broad normalization changes).
- Avoid regressions in attribute vs property handling, especially for numeric/boolean/reflected props.

Deliverables:
- Internal patch to DOM property setting/unsetting logic.
- Test suite passes including new regression.



### 3. Run full test suite and add guard checks for regressions in prop/attr handling (Epic: user query)

#### Description

Validate the fix does not regress related behavior.

Work items:
- Run the browser/render tests (at minimum) and the full test suite used by the repo.
- Add at least one targeted assertion (or confirm existing coverage) around:
  - boolean attribute removal behavior still correct
  - numeric property handling still correct when set to 0 and then to another number
  - property-vs-attribute distinction remains unchanged for other known special props

Acceptance checks:
- All tests pass.
- No additional failures introduced in other attribute/property tests.



### 4. user query

#### Description

locate task_5_preactjs_preact.csv and create a plan to fix the bug contained inside.


### 5. Ensure plan contains executable subtasks (no-op structural fix) (Epic: user query)

#### Description

This ticket exists only to satisfy planning requirements that STAGE 3 includes at least one explicit subtask in the plan tree.

Work items:
- Confirm at least one TASK in this plan has SUBTASK children.
- If not, add 2–4 SUBTASKs under the most appropriate TASK to ensure work is runnable and testable.

Acceptance checks:
- Plan renders with at least one SUBTASK node present.
- No duplicate/conflicting tickets are introduced.


### 6. Locate and update DOM prop patching path for tabIndex/tabindex removal semantics (Epic: user query)

#### Description

Identify where Preact applies prop diffs to DOM elements and specifically how it currently handles:
- camelCase `tabIndex` as a DOM property vs HTML attribute
- lowercase `tabindex`
- transitions from a defined numeric value (0) to `undefined` or `null`

Then implement a minimal, targeted change so that when the next vnode prop value is `null` or `undefined`:
- the DOM `tabIndex` property is reset to default (`-1`) OR otherwise restored to the platform default behavior
- the corresponding attribute (if it is being used) is removed

Implementation notes (keep scope tight):
- Prefer a tabIndex-specific fix only if generic `null/undefined` removal would be risky.
- If the code uses a helper like `setProperty`/`setAccessor`/`setAttribute`, patch at the narrowest layer that reliably handles both `tabIndex` and `tabindex`.
- Ensure the fix works across rerenders and does not break initial mount behavior.

Acceptance checks:
- Local reproduction using the regression test steps yields `-1` after setting to null/undefined.
- Verify no behavior change for `tabIndex={0}` and for other numeric props.



### 7. Add/adjust tests to cover tabIndex reset behavior (camelCase + lowercase) (Epic: user query)

#### Description

Ensure the test suite includes coverage for both `tabIndex` and `tabindex` prop keys across rerenders.

Work items:
- Confirm the added regression test "should reset tabindex on undefined/null" is present in `test/browser/render.test.js` and correctly asserts:
  - after `tabIndex={0}`, rerender with `undefined` => `.tabIndex === -1`
  - rerender with `null` => `.tabIndex === -1`
  - repeat for lowercase `tabindex`
- If the implementation fix is generic and may affect attribute removal, add a focused test asserting that when a prop becomes null/undefined, the attribute is removed (not set to string "null"/"undefined"). Keep this very limited to avoid changing existing expectations.

Acceptance checks:
- Test fails on current behavior and passes with the implementation change.
- No unrelated snapshot/output changes.



### 8. Reproduce regression and identify current prop removal behavior for tabIndex/tabindex (Epic: Locate and update DOM prop patching path for tabIndex/tabindex removal semantics)

#### Description

Run the newly added test `should reset tabindex on undefined/null` (in `test/browser/render.test.js`) against the current code to confirm it fails. Then trace the DOM prop application path used for `tabIndex`/`tabindex` during rerender (the setter/remove logic) and note what happens when next value is `undefined`/`null`.

Acceptance:
- You can point to the exact function/module responsible for applying/removing `tabIndex`.
- You can explain why `.tabIndex` remains `0` after rerender today.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Run full suite and confirm no prop/attr regressions
    - current (in progress task): Reproduce regression and identify current prop removal behavior for tabIndex/tabindex <-
    - upcoming (not yet): Patch DOM prop setter to reset .tabIndex to default (-1) on null/undefined
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Reproduce the failing behavior for `tabIndex` reset on `null`/`undefined` and trace the exact DOM prop diffing/patching path responsible for applying/removing `tabIndex`/`tabindex` during rerender.

##### Technical Specs
- **Entry point**
  - Use the newly added browser test: `test/browser/render.test.js` → `"should reset tabindex on undefined/null"`.
- **What to trace**
  - The rerender path that compares previous vnode props to next vnode props.
  - The exact function(s) that:
    - decide “property vs attribute” for `tabIndex` and lowercase `tabindex`
    - handle removal when next value is `null` or `undefined`
    - set DOM properties (e.g., `el.tabIndex = ...`) and/or remove attributes (e.g., `removeAttribute('tabindex')`)

##### Implementation Checklist
- [ ] Run the single failing test (or the smallest browser/render test subset that includes it) to confirm current failure.
- [ ] Observe and record the actual DOM outcomes after rerender:
  - `.tabIndex` value after setting `tabIndex={0}` then rerendering with `undefined` and `null`
  - whether the `tabindex` attribute exists and what its string value is (e.g., `null`, `undefined`, `"0"`, or absent)
  - repeat for lowercase `tabindex`
- [ ] Trace code execution for the update:
  - identify the module/file where DOM props are diffed and applied
  - identify the helper responsible for setting/removing props/attributes (often a “setProperty/setAccessor” style function)
- [ ] Document the root cause in concrete terms:
  - why `.tabIndex` remains `0` (e.g., removal path skips property reset, or removal uses attribute removal only, or `null/undefined` is treated as “no-op” for this prop)

##### Success Criteria
- [ ] The test is confirmed failing on current/broken behavior.
- [ ] The exact function/module responsible for applying/removing `tabIndex` is identified.
- [ ] A precise explanation exists for why `.tabIndex` stays `0` after rerender with `null/undefined` today (based on traced logic, not guesswork).

---


### 9. Patch DOM prop setter to reset .tabIndex to default (-1) on null/undefined (Epic: Locate and update DOM prop patching path for tabIndex/tabindex removal semantics)

#### Description

Implement a minimal, targeted change in the DOM prop diffing/patching code so that when `tabIndex` (or `tabindex`) transitions from a defined value to `null` or `undefined`, the DOM ends in the default state:
- remove the `tabindex` attribute (if present/used)
- set the `tabIndex` property to `-1` (platform default) so it no longer retains prior value `0`

Acceptance:
- Regression test passes for both `tabIndex` and `tabindex`.
- Other prop handling logic is unchanged (no broad null/undefined normalization).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Reproduce regression and identify current prop removal behavior for tabIndex/tabindex
    - current (in progress task): Patch DOM prop setter to reset .tabIndex to default (-1) on null/undefined <-
    - upcoming (not yet): Add/confirm narrow test assertions to prevent attribute stringification
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement a minimal, targeted patch in the DOM prop setter/diffing logic so that when `tabIndex` (camelCase) or `tabindex` (lowercase) transitions to `null` or `undefined` during rerender, the DOM ends in the default state: `.tabIndex === -1` and no stale `tabindex` attribute remains.

##### Technical Specs
- **Behavior to implement**
  - On rerender when next prop value is `null` or `undefined`:
    - remove the `tabindex` attribute if it is used/present
    - ensure the DOM property `element.tabIndex` resets to the platform default `-1` (does not retain prior `0`)
- **Scope constraints**
  - Keep changes narrowly targeted to `tabIndex`/`tabindex` handling.
  - Do **not** introduce broad “all props null/undefined removal resets property” logic unless proven safe and already consistent with existing semantics.
  - Preserve existing attribute vs property behavior for other known special props (numeric/boolean/reflected).

##### Implementation Checklist
- [ ] Apply the fix at the narrowest reliable layer that handles both spellings:
  - either a tabIndex-specific branch in the prop setter
  - or a very limited condition in a shared setter that triggers only for tabIndex keys
- [ ] Ensure both flows are covered:
  - `tabIndex={0} -> tabIndex={undefined} -> tabIndex={null}`
  - `tabindex={0} -> tabindex={undefined} -> tabindex={null}`
- [ ] Ensure removal does not stringify:
  - `tabindex` attribute must not become `"null"` or `"undefined"`
- [ ] Run the targeted regression test and the relevant browser/render test subset.

##### Success Criteria
- [ ] The regression test `"should reset tabindex on undefined/null"` passes for both `tabIndex` and `tabindex`.
- [ ] DOM ends in default state after removal: `.tabIndex === -1`.
- [ ] `tabindex` attribute is removed (not set to `"null"`/`"undefined"`).
- [ ] No unrelated prop handling logic changes (reviewable diff; no broad normalization).

---


### 10. Add/confirm narrow test assertions to prevent attribute stringification (Epic: Locate and update DOM prop patching path for tabIndex/tabindex removal semantics)

#### Description

If your implementation touches generic remove/set paths, ensure there’s a narrow assertion that `tabindex` is not set to string values like "null"/"undefined" and is removed when the prop becomes `null`/`undefined`.

Acceptance:
- Test suite asserts attribute removal semantics for this case only.
- No unrelated snapshots/expectations change.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Patch DOM prop setter to reset .tabIndex to default (-1) on null/undefined
    - current (in progress task): Add/confirm narrow test assertions to prevent attribute stringification <-
    - upcoming (not yet): Run full suite and validate no regressions in attribute/property handling
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add or confirm narrowly-scoped test coverage that prevents accidental attribute stringification for `tabindex` when the prop becomes `null`/`undefined`, ensuring the attribute is removed (not set to `"null"`/`"undefined"`). Keep this coverage limited to this case to avoid altering existing expectations.

##### Technical Specs
- **Test location**
  - Extend `test/browser/render.test.js` near the existing `"should reset tabindex on undefined/null"` test, or confirm that test already asserts attribute removal semantics.
- **Assertions required**
  - After rerender with `tabIndex={undefined}` and `tabIndex={null}` (and likewise lowercase `tabindex`):
    - `el.getAttribute('tabindex') === null` (attribute absent), or equivalent absence check
    - explicitly ensure it is not `"null"` and not `"undefined"` if the testing helpers expose raw attribute values

##### Implementation Checklist
- [ ] Review the existing regression test:
  - if it only checks `.tabIndex`, add minimal checks for attribute removal on the same element
- [ ] Ensure assertions are stable and DOM-accurate:
  - prefer `getAttribute('tabindex')` absence checks over serialized HTML snapshots
- [ ] Keep the test narrowly focused:
  - do not introduce generalized expectations for other props/attributes
- [ ] Confirm the new/updated test fails on the broken behavior (if applicable) and passes with the fix.

##### Success Criteria
- [ ] The suite includes an explicit assertion that `tabindex` is removed (absent) when the prop becomes `null`/`undefined`.
- [ ] The suite ensures `tabindex` is not stringified to `"null"`/`"undefined"`.
- [ ] No unrelated snapshots/expectations change; only minimal, targeted assertions are added.


### 11. Run full suite and validate no regressions in attribute/property handling (Epic: Locate and update DOM prop patching path for tabIndex/tabindex removal semantics)

#### Description

Run the full test suite (or CI-equivalent). If any failures occur, adjust with minimal blast-radius changes and, if needed, add one narrow regression test to lock in prior behavior for another prop category impacted by the change.

Acceptance:
- Full suite green.
- No new failures in boolean attribute removal or numeric property update tests.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add/confirm narrow test assertions to prevent attribute stringification
    - current (in progress task): Run full suite and validate no regressions in attribute/property handling <-
    - upcoming (not yet): Verify regression test is present and asserts reset to -1 for both prop spellings
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Execute the repository’s full automated test suite after the `tabIndex` null/undefined reset fix has landed, and validate there are no regressions in DOM property vs attribute behavior.

##### Technical Specs
- **Test execution**
  - Run the browser/render test subset (at minimum) and then the full suite (CI-equivalent locally).
  - Capture failing test names and logs for any regressions introduced by the `tabIndex` patch.
- **Regression focus areas**
  - **Boolean attribute removal** remains correct (attributes are removed, not set to `"false"`/`"null"`/`"undefined"`; behavior for known boolean attrs unchanged).
  - **Numeric property updates** remain correct, especially transitions involving `0` (e.g., `0 -> 1`, `1 -> 0`, `0 -> null/undefined` where applicable).
  - **Property-vs-attribute distinction** for other special props remains unchanged (no broad “null/undefined normalization” side effects).

##### Implementation Checklist
- [ ] Run `test/browser/render.test.js` (or equivalent browser/render suite) and confirm the new regression test passes.
- [ ] Run the full test suite used by the repo (same commands CI uses, if available).
- [ ] If failures occur:
  - [ ] Triage whether the failure is due to unintended changes in generic prop/attr set/remove logic.
  - [ ] Adjust the fix with **minimal blast radius** (prefer tabIndex-specific handling over generic changes unless clearly safe).
  - [ ] Add **one narrowly-scoped regression test** only when needed to preserve preexisting behavior for the failing prop category (keep assertions minimal and targeted).
- [ ] Re-run affected suites until green.

##### Success Criteria
- [ ] Full suite is green (CI-equivalent locally).
- [ ] No new failures introduced in existing prop/attribute tests.
- [ ] Explicitly confirm (via existing tests or a narrowly-scoped new one, if required) that:
  - [ ] boolean attribute removal behavior is unchanged
  - [ ] numeric property handling (including `0`) remains correct

##### Files to Read (reference)
- `test/browser/render.test.js` (new `tabIndex` regression coverage)
- Any existing tests covering boolean attributes / numeric props (search in `test/` for related cases)

##### Notes / Constraints
- Keep any additional regression tests tightly scoped to avoid shifting unrelated expectations or snapshots.
- Prefer verifying existing coverage before adding new tests.


### 12. Verify regression test is present and asserts reset to -1 for both prop spellings (Epic: Add/adjust tests to cover tabIndex reset behavior (camelCase + lowercase))

#### Description

Confirm `test/browser/render.test.js` contains "should reset tabindex on undefined/null" and that it:
- renders `<div tabIndex={0} />` then rerenders with `tabIndex={undefined}` and `tabIndex={null}`, asserting `el.tabIndex === -1`
- repeats the same flow using lowercase `tabindex`

Acceptance:
- Test is present, deterministic, and fails on current broken behavior.
- Test passes after implementation fix without changing other expectations.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Run full suite and validate no regressions in attribute/property handling
    - current (in progress task): Verify regression test is present and asserts reset to -1 for both prop spellings <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify the presence and correctness of the newly added regression test for `tabIndex` removal/reset behavior, ensuring it covers both camelCase and lowercase prop spellings and is deterministic.

##### Technical Specs
- **Target file:** `test/browser/render.test.js`
- **Target test name:** `should reset tabindex on undefined/null`
- **Required behavior asserted by the test**
  - Render `<div tabIndex={0} />` and assert `el.tabIndex === 0`
  - Rerender with `{ tabIndex: undefined }` and assert `el.tabIndex === -1`
  - Rerender with `{ tabIndex: null }` and assert `el.tabIndex === -1`
  - Repeat the same sequence using lowercase prop key `{ tabindex: ... }`

##### Implementation Checklist
- [ ] Locate `should reset tabindex on undefined/null` in `test/browser/render.test.js`.
- [ ] Confirm it includes:
  - [ ] an initial render with `tabIndex={0}` and assertion for `0`
  - [ ] a rerender to `undefined` and assertion for `-1`
  - [ ] a rerender to `null` and assertion for `-1`
  - [ ] the same flow for lowercase `tabindex`
- [ ] Confirm the test is deterministic:
  - [ ] uses fresh DOM nodes or properly resets between cases
  - [ ] does not depend on test execution order or shared global state
- [ ] Validate expected failure/pass behavior:
  - [ ] On the broken baseline (pre-fix), the test should fail because `.tabIndex` remains `0`
  - [ ] After the implementation fix, the test should pass without modifying unrelated expectations

##### Success Criteria
- [ ] Test exists in the specified file with the exact intended assertions for both `tabIndex` and `tabindex`.
- [ ] Test fails against the known broken behavior and passes after the fix.
- [ ] No unrelated snapshot/output/expectation changes are required to make it pass.

##### Constraints
- Do not broaden the test into generic prop/attr semantics; keep it focused on the `tabIndex` reset behavior and both prop spellings.
