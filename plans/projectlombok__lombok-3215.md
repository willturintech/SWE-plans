# Plan Name: Analyze and Plan Bug Fix for Project Lombok CSV Task

## Tasks

### 1. Implement reserved-name detection for extends/implements referenced types (Epic: Fix @SuperBuilder builder generic name collision with referenced types in extends/implements clauses)

#### Description

Change the SuperBuilder code path that decides builder type parameter identifiers so it accounts for simple-name clashes with types referenced in the annotated type’s `extends` and `implements` clauses.

Implementation outline (Java AST based):
- Locate the handler/transformer that builds the generated builder class signature for @SuperBuilder (javac and/or eclipse implementation; implement in both if both exist in repo).
- When computing candidate generic parameter names (e.g., `C`, `B`, or inferred names), build a `Set<String> reserved` consisting of:
  - existing type parameter names on the annotated type
  - builder and builderImpl class simple names
  - *simple names referenced in extends/implements clauses*, including nested type references (`B2.B4` → reserve `B4`, and also reserve intermediate identifiers if they can appear unqualified in the generated scope).
- Add a helper that traverses the type reference AST nodes for `extends` and `implements` lists, collecting identifier tokens / simple names used.
- Ensure reserved-name collection handles parameterized types and arrays (e.g., `Foo<Bar.Baz>` should reserve `Foo` and `Baz` at minimum).

Testability:
- Add/adjust unit/transform behavior so in the new `ExtendsClauseCollision` case, the generated builder no longer uses `B4` as a type parameter name.


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Implement reserved-name detection for extends/implements referenced types <-
    - upcoming (not yet): Deterministically rename colliding builder type parameter identifiers
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement reserved-name detection for `@SuperBuilder` builder generic type parameters so generated type parameter identifiers never collide with *simple names* of types referenced in the annotated class’s `extends` and `implements` clauses.

##### Technical Specs
- **Scope**: `@SuperBuilder` code generation for both compiler backends present in the repo (javac handler and eclipse handler). If only one exists, implement there; otherwise implement in both to keep behavior consistent.
- **Goal**: Expand the existing “reserved names” set used when choosing builder type parameter names to include names referenced in:
  - `extends` type (if present)
  - `implements` types (0..n)
- **Reserved-name sources** (must all be included):
  - Declared type parameter names on the annotated type
  - Generated builder / builderImpl simple names
  - **Simple names referenced by `extends`/`implements` types**, including nested references:
    - Example: `B2.B4<Object>` must reserve at least `B4` (and reserve `B2` as well if it can be used unqualified in the generated scope).
  - Handle common type forms:
    - Parameterized types: `Foo<Bar.Baz>` → reserve `Foo` and `Baz` (and `Bar` if applicable per implementation approach)
    - Arrays: `Foo[]`, `Bar.Baz[][]` → reserve element type names
    - Wildcards / bounds: `Foo<? extends Bar.Baz>` → reserve `Foo` and `Baz`
- **AST traversal helper**:
  - Add a small, testable helper that walks the backend’s type-reference AST nodes and collects identifier tokens / simple names into a `Set<String>`.
  - Ensure traversal is defensive for nulls and unexpected node shapes.

##### Implementation Checklist
- [ ] Locate the code path where `@SuperBuilder` computes builder generic type parameter identifiers (builder self-type, parent builder type, and any internal generics).
- [ ] Introduce/extend a `reservedNames` set and populate it with existing reserved sources plus `extends`/`implements` referenced type names.
- [ ] Implement a backend-specific helper for extracting referenced simple names from type references:
  - [ ] Covers qualified/nested types (`A.B.C`)
  - [ ] Covers type arguments recursively (`A<B.C<D>>`)
  - [ ] Covers arrays and wildcard bounds
- [ ] Wire the helper into the reserved-name computation so the collision case is prevented *before* name-picking finalizes.
- [ ] Keep changes localized to naming/collision logic; do not alter unrelated codegen formatting.

##### Success Criteria
- [ ] In the `SuperBuilderNameClashes.ExtendsClauseCollision` scenario (`implements B2.B4<Object>, B3<Object>`), `B4` is present in the reserved set used for choosing builder generic names.
- [ ] After delombok, the generated builder generic parameter name is *not* `B4` for this case (actual renaming strategy handled in the next task).
- [ ] No unrelated transform fixtures change as a side-effect of collecting more reserved names.

##### Files to Read (guidance)
- `src/core/lombok/javac/handlers/HandleSuperBuilder.java` (or equivalent)
- `src/core/lombok/eclipse/handlers/HandleSuperBuilder.java` (or equivalent)
- Any existing helper used for collecting/avoiding reserved identifiers in builder generation

##### Files to Modify
- The `@SuperBuilder` handler(s) where builder type parameter names are selected
- Add a small helper class/method near the handler(s) if needed (keep visibility minimal)


### 2. Fix @SuperBuilder builder generic name collision with referenced types in extends/implements clauses (Epic: user query)

#### Description

Implement a Lombok @SuperBuilder codegen fix so that delombok output compiles when generated builder generic type parameter names would collide with simple names of referenced types appearing in the annotated type’s extends/implements clauses.

Bug scenario (from task CSV / new fixture): In `SuperBuilderNameClashes.java`, a class like `ExtendsClauseCollision extends B implements B2.B4<Object>, B3<Object>` causes the generated builder to introduce a type parameter named `B4`, which clashes with the interface simple name `B4` referenced in the implements clause.

Deliverables / acceptance:
- Delombok output for the new `SuperBuilderNameClashes.ExtendsClauseCollision` compiles.
- Transform tests for `SuperBuilderNameClashes` (including `ExtendsClauseCollision`) pass.
- Generated source avoids simple-name collisions between builder generic type parameters and referenced type names from extends/implements clauses.
- No regressions in other SuperBuilder transform tests.



### 3. user query

#### Description

Locate task_5_projectlombok_lombok.csv and create a plan to fix the bug described inside.


### 4. Update/verify transform test fixtures for new ExtendsClauseCollision case (Epic: user query)

#### Description

Ensure the new `SuperBuilderNameClashes.ExtendsClauseCollision` case is represented in test resources and expected delombok output.

This task aligns fixtures and expected output with the corrected generator behavior (after implementing the fix). It must not paper over the bug by only changing fixtures without a generator fix.

Acceptance:
- `test/transform/resource/before/SuperBuilderNameClashes.java` (or equivalent) contains the new case.
- `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` reflects the new, non-colliding generic parameter name(s) produced by the fixed generator.
- Transform test runner passes for this file.



### 5. Deterministically rename colliding builder type parameter identifiers (Epic: Fix @SuperBuilder builder generic name collision with referenced types in extends/implements clauses)

#### Description

Add logic so when a preferred/candidate builder type parameter name is in the reserved set, Lombok chooses a stable alternative.

Implementation outline:
- Introduce a `pickNonClashingName(base, reserved)` helper:
  - If `base` not reserved → use it.
  - Else try `base_`, then `base__`, or numeric suffix (`base2`, `base3`, …) until free.
- Apply this helper to all generated builder type parameters (including builder self-type, parent builder type, and any additional internal type parameters generated by @SuperBuilder).
- Ensure the renaming is applied consistently across all references within generated code (builder class declaration, return types, method generic bounds, etc.).
- Keep output minimal: only rename when collision exists.

Testability:
- For the collision case, verify a single deterministic rename occurs and the rest of the generated code compiles.
- Existing SuperBuilder tests should remain unchanged unless they relied on previously-colliding names.


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement reserved-name detection for extends/implements referenced types
    - current (in progress task): Deterministically rename colliding builder type parameter identifiers <-
    - upcoming (not yet): Run and validate SuperBuilder transform tests; update expected outputs only as required
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add deterministic renaming for colliding `@SuperBuilder` builder type parameter identifiers. When a preferred name is reserved (including new reservations from `extends`/`implements` referenced types), pick a stable alternative and apply it consistently across all generated references.

##### Technical Specs
- **Helper**: Introduce `pickNonClashingName(base, reserved)` with deterministic behavior:
  - If `base` not in `reserved` → return `base`
  - Else try `base_`, then `base__`, then `base___`… (or `base2`, `base3`…); choose one strategy and apply consistently
  - Must guarantee termination (e.g., loop until a free name is found)
- **Apply to all builder generics** generated by `@SuperBuilder`, including:
  - Builder “self type” generic
  - Parent builder generic(s)
  - Any additional synthetic/internal generic parameters introduced by the feature
- **Consistency requirement**:
  - Once a name is chosen, *all* occurrences of that type parameter in generated code must use the renamed identifier:
    - Builder class declaration
    - BuilderImpl class declaration
    - Method return types and parameter types
    - Generic bounds and extends clauses inside generated types
- **Minimal diffs**:
  - Only rename when there is a collision (`base ∈ reserved`)
  - Do not rename non-colliding cases

##### Implementation Checklist
- [ ] Add `pickNonClashingName` (backend-specific or shared, depending on existing structure).
- [ ] Ensure the function updates both:
  - The returned chosen name
  - The `reserved` set (add chosen name immediately to prevent later collisions)
- [ ] Identify every builder-related type parameter generated by `@SuperBuilder` and run it through `pickNonClashingName`.
- [ ] Ensure ordering is deterministic (same input → same output); avoid iteration over hash sets when generating sequences of names.
- [ ] Update all internal references to use the final chosen identifiers (do not leave any stale references to the original name).

##### Success Criteria
- [ ] For `ExtendsClauseCollision`, exactly one stable rename occurs (e.g., `B4` → `B4_`), and the entire generated delombok output compiles.
- [ ] Existing `@SuperBuilder` transform tests remain unchanged unless they truly had a hidden collision (avoid broad churn).
- [ ] The rename choice is deterministic across runs and across javac/eclipse backends (if both are implemented).

##### Files to Modify
- The `@SuperBuilder` codegen handler(s) that declare and reference builder generic parameters
- Any supporting name-allocation utilities used by `@SuperBuilder`


### 6. Run and validate SuperBuilder transform tests; update expected outputs only as required (Epic: Fix @SuperBuilder builder generic name collision with referenced types in extends/implements clauses)

#### Description

Validate the fix against Lombok transform tests and ensure fixtures match the corrected codegen.

Steps:
- Apply the provided `test_patch` from the CSV row (or confirm it’s already applied) adding the `ExtendsClauseCollision` case.
- Run the transform test suite (or at minimum the SuperBuilderNameClashes transform test).
- Update `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` to reflect the renamed builder generic parameter (i.e., expected delombok output after fix).
- Confirm no other after-delombok files change (unless the fix legitimately affects other cases).

Acceptance:
- `SuperBuilderNameClashes` transform test passes.
- No regressions in other SuperBuilder transform tests.


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Deterministically rename colliding builder type parameter identifiers
    - current (in progress task): Run and validate SuperBuilder transform tests; update expected outputs only as required <-
    - upcoming (not yet): Apply/confirm test patch for ExtendsClauseCollision fixture
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run and validate Lombok transform tests for the `@SuperBuilder` fix, and update only the necessary expected `after-delombok` fixture output to match the corrected, non-colliding builder generic name.

##### Technical Specs
- **Patch/fixture state**:
  - Ensure the CSV-provided `test_patch` adding `ExtendsClauseCollision` is applied (or confirm it is already present).
- **Test execution**:
  - Run the transform test(s) that cover `SuperBuilderNameClashes` first.
  - Then run the broader SuperBuilder transform test set to detect regressions.
- **Expected output updates**:
  - Update `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` to reflect the new chosen builder type parameter name(s) after the generator fix.
  - Keep changes minimal and localized to renamed identifiers required by the collision-avoidance logic.

##### Implementation Checklist
- [ ] Confirm the new `ExtendsClauseCollision` case exists in the relevant transform resources (before and/or after-delombok as per project convention).
- [ ] Run the focused transform test for `SuperBuilderNameClashes`.
- [ ] If the test fails only due to expected-output mismatch, regenerate/derive the correct expected `after-delombok` content and apply minimal diffs.
- [ ] Re-run the focused test to green.
- [ ] Run the wider SuperBuilder transform tests; ensure no unexpected fixture diffs appear elsewhere.
- [ ] If other fixtures change, justify them as direct consequence of the collision fix; otherwise revert and refine the implementation.

##### Success Criteria
- [ ] `SuperBuilderNameClashes` transform test passes including the `ExtendsClauseCollision` case.
- [ ] No regressions in other SuperBuilder transform tests.
- [ ] Only necessary `after-delombok` fixture changes are committed; no broad formatting churn.

##### Files to Modify
- `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` (as required)
- Potentially `test/transform/resource/before/SuperBuilderNameClashes.java` only if the `test_patch` was not yet applied


### 7. Apply/confirm test patch for ExtendsClauseCollision fixture (Epic: Update/verify transform test fixtures for new ExtendsClauseCollision case)

#### Description

Ensure the transform test input/expected-output files include the new `ExtendsClauseCollision` case described in the CSV `test_patch`.

Work:
- Apply the patch content from the CSV row to the appropriate test resource(s):
  - `test/transform/resource/before/SuperBuilderNameClashes.java` (input) and/or
  - `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` (expected delombok output)
  depending on how Lombok’s transform tests are structured for this case.
- Verify the added constructs match the scenario:
  - nested interface `B2.B4<X>` and `B3<Y>`
  - class `ExtendsClauseCollision extends B implements B2.B4<Object>, B3<Object>`
  - expected builder code that will change after the generator fix.

Acceptance:
- Test resources contain the new case and compile as plain Java sources (ignoring Lombok transforms) where applicable.


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Run and validate SuperBuilder transform tests; update expected outputs only as required
    - current (in progress task): Apply/confirm test patch for ExtendsClauseCollision fixture <-
    - upcoming (not yet): Update expected after-delombok output to match the new non-colliding builder type parameter name
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Apply (or confirm applied) the CSV `test_patch` that introduces the new `SuperBuilderNameClashes.ExtendsClauseCollision` transform fixture, ensuring the test resources correctly represent the collision scenario and remain valid Java sources for the transform harness.

##### Technical Specs
- **Where to apply** (depending on Lombok transform test structure):
  - `test/transform/resource/before/SuperBuilderNameClashes.java` (input using Lombok annotations)
  - `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` (expected delombok output)
- **Fixture content requirements**:
  - Nested interface structure:
    - `interface B2 { interface B4<X> {} }`
    - `interface B3<Y> {}`
  - New annotated class:
    - `class ExtendsClauseCollision extends B implements B2.B4<Object>, B3<Object> { ... }`
  - Expected output must reflect current generator behavior at the time of application:
    - If generator fix is not yet present, expected output may still show the problematic `B4` type param (this will be updated in a later task).
    - Do not “fix” the bug by changing only the fixture; the fixture must expose the collision.

##### Implementation Checklist
- [ ] Apply the patch content from the CSV row exactly, preserving surrounding formatting conventions of the fixture file.
- [ ] Ensure the new case is placed in the correct section/order within `SuperBuilderNameClashes.java` consistent with other cases.
- [ ] Validate that:
  - [ ] The “before” fixture compiles as a normal Java source file (ignoring Lombok processing) as required by the harness conventions.
  - [ ] The “after-delombok” fixture remains syntactically valid Java text (even if it wouldn’t compile until the fix is implemented).
- [ ] Ensure no unrelated fixture content changes occur.

##### Success Criteria
- [ ] The transform test resources contain the `ExtendsClauseCollision` case with the required nested interfaces and implements clause (`B2.B4<Object>, B3<Object>`).
- [ ] Diffs are limited to adding the new case (no incidental edits).
- [ ] Fixture files remain well-formed and consistent with Lombok transform test conventions.

##### Files to Modify
- `test/transform/resource/before/SuperBuilderNameClashes.java` and/or
- `test/transform/resource/after-delombok/SuperBuilderNameClashes.java`


### 8. Update expected after-delombok output to match the new non-colliding builder type parameter name (Epic: Update/verify transform test fixtures for new ExtendsClauseCollision case)

#### Description

Once generator fix is in place, update `after-delombok/SuperBuilderNameClashes.java` so the expected output reflects the renamed builder type parameter (i.e., not `B4` when `B4` is used as a referenced type in extends/implements).

Guidance:
- Keep diffs minimal: only change the type parameter identifiers that are renamed by the collision-avoidance algorithm.
- Ensure the rename is consistent within the generated builder class and any related types.

Acceptance:
- The expected file matches actual delombok output produced by the fixed generator.


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply/confirm test patch for ExtendsClauseCollision fixture
    - current (in progress task): Update expected after-delombok output to match the new non-colliding builder type parameter name <-
    - upcoming (not yet): Run SuperBuilderNameClashes transform tests and verify no unrelated fixture diffs
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Update the SuperBuilder transform expected-output fixture so it matches the **new delombok output produced by the generator fix** that avoids type-parameter name collisions with referenced types in `extends`/`implements` clauses.

##### Scope
- File: `test/transform/resource/after-delombok/SuperBuilderNameClashes.java`
- Case: `SuperBuilderNameClashes.ExtendsClauseCollision`

##### Technical Specs
- Update only the generated builder-related generic type parameter identifier(s) that were renamed by the collision-avoidance logic (e.g., a parameter previously named `B4` must no longer be `B4` if `B4` is referenced as a type in `implements B2.B4<Object>`).
- Ensure the rename is **consistent everywhere** that identifier appears within the generated code for the case, including (as applicable):
  - builder class type parameter list
  - builder implementation type parameter list
  - `extends`/`implements` clauses on generated builders
  - method return types / parameter types referencing the builder generics
  - any casts or helper methods that mention the type parameter
- Keep the diff minimal and localized to the `ExtendsClauseCollision` expected output block.

##### Implementation Checklist
- [ ] Run delombok/transform generation for `SuperBuilderNameClashes` using the fixed generator behavior and capture the actual output for `ExtendsClauseCollision`.
- [ ] Edit `after-delombok/SuperBuilderNameClashes.java` so the `ExtendsClauseCollision` section matches the newly generated output exactly.
- [ ] Verify there are no incidental formatting or whitespace-only changes outside the necessary block.
- [ ] Verify the expected output compiles as Java (as per transform test conventions) and that the builder generic name is not a colliding identifier.

##### Success Criteria
- [ ] `test/transform/resource/after-delombok/SuperBuilderNameClashes.java` matches the actual delombok output for the fixed generator.
- [ ] Only the required identifier renames (and their direct references) change; no unrelated fixture edits.
- [ ] The `ExtendsClauseCollision` expected output no longer uses `B4` as the generated builder generic parameter name when `B4` is a referenced type in the annotated class’ `implements` clause.

##### Notes
- Do not “fix” the test by handwaving: the expected output must reflect the generator’s deterministic rename strategy, not an arbitrary rename.


### 9. Run SuperBuilderNameClashes transform tests and verify no unrelated fixture diffs (Epic: Update/verify transform test fixtures for new ExtendsClauseCollision case)

#### Description

Run Lombok transform tests focusing on `SuperBuilderNameClashes` and then the broader SuperBuilder transform test set.

Checks:
- `SuperBuilderNameClashes` passes, including `ExtendsClauseCollision`.
- No unexpected changes in other `after-delombok` fixtures.

Acceptance:
- All SuperBuilder transform tests pass.
- If broader suite is run, no regressions.


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Update expected after-delombok output to match the new non-colliding builder type parameter name
    - current (in progress task): Run SuperBuilderNameClashes transform tests and verify no unrelated fixture diffs <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Execute the Lombok transform tests for the `SuperBuilderNameClashes` fixture (including the new `ExtendsClauseCollision` case) and confirm that the generator fix does not introduce unrelated golden-file diffs or regressions in other SuperBuilder transform fixtures.

##### Scope
- Primary: transform test(s) covering `test/transform/resource/before/SuperBuilderNameClashes.java` and `test/transform/resource/after-delombok/SuperBuilderNameClashes.java`
- Secondary: broader SuperBuilder transform test set (as available in the repo)

##### Implementation Checklist
- [ ] Run the transform test runner targeting `SuperBuilderNameClashes` (or the smallest suite that includes it).
- [ ] Confirm `ExtendsClauseCollision` is present in the before/after resources and is exercised by the test run.
- [ ] Confirm the test run produces no diffs for `SuperBuilderNameClashes` beyond what is already checked into `after-delombok`.
- [ ] Run the broader SuperBuilder transform tests (or the full transform suite if that is the standard workflow).
- [ ] Review git status / diff to ensure no other `after-delombok` fixtures changed unexpectedly.
- [ ] If any additional fixtures change, treat as a regression unless there is a clearly justified, reviewable reason tied to the collision-avoidance fix (and then keep changes minimal).

##### Success Criteria
- [ ] The `SuperBuilderNameClashes` transform test passes, including the `ExtendsClauseCollision` scenario.
- [ ] No unexpected diffs appear in other `test/transform/resource/after-delombok/*` fixtures.
- [ ] The broader SuperBuilder transform test set passes without regressions (or, if the full suite is run, it passes as well).
