# Plan Name: Debug Laravel Framework CSV Task

## Tasks

### 1. Tests: implement task_3 scenarios for replicate() with UUID/ULID unique-id columns (Epic: Fix Eloquent Model::replicate() to avoid copying UUID/ULID unique identifiers on non-primary keys)

#### Description

Add/align PHPUnit tests described by `tasks/task_3_laravel_framework.csv` (and mirrored by the matching section in `Planning Agent Eval - eval_1.csv`, around `testCloneModelMakesAFreshCopyOfTheModelWhenModelHasUuidPrimaryKey`).

Implementation details:
- Update `tests/Database/DatabaseEloquentModelTest.php` (or the file referenced by existing replicate tests).
- Create minimal model stubs for:
  1) UUID primary key model using `Illuminate\Database\Eloquent\Concerns\HasUuids`
  2) ULID primary key model using `HasUlids`
  3) Model where primary key is normal (int) but a non-PK attribute (e.g. `uuid`) is treated as a generated unique id via the unique-id concern API.
  4) Same for ULID non-PK attribute.
- Add assertions that:
  - PK is excluded on replicate (existing behavior)
  - Non-PK unique-id attributes are also excluded (expected new behavior)
  - Optionally: after save, missing unique-id attributes are generated (if that’s the framework’s behavior for those stubs).

Acceptance criteria:
- At least one test fails on baseline because replicate currently copies non-PK UUID/ULID unique-id attribute(s).
- Tests pass once replicate fix is implemented.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Tests: implement task_3 scenarios for replicate() with UUID/ULID unique-id columns <-
    - upcoming (not yet): Implementation: update Model::replicate() exclusion list to also exclude unique-id attributes
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add/align PHPUnit coverage for Eloquent `Model::replicate()` to ensure UUID/ULID “unique-id” attributes (including non-primary-key columns) are *not* copied during replication, matching the scenarios described in `tasks/task_3_laravel_framework.csv` (and mirrored in `Planning Agent Eval - eval_1.csv` near `testCloneModelMakesAFreshCopyOfTheModelWhenModelHasUuidPrimaryKey`).

##### Technical Specs
- **Test location**
  - Update the existing replicate/clone tests in `tests/Database/DatabaseEloquentModelTest.php` (or the file already containing `replicate()` tests if they’ve been moved in this repo version).
- **Model stubs (define inside the test file if that’s the prevailing convention)**
  1) Model with **UUID primary key** using `Illuminate\Database\Eloquent\Concerns\HasUuids`
  2) Model with **ULID primary key** using `Illuminate\Database\Eloquent\Concerns\HasUlids`
  3) Model with **integer primary key** but a **non-PK UUID unique-id column** (e.g. `uuid`) generated via the framework’s unique-id concern API (i.e., use whatever mechanism this Laravel version uses: `HasUniqueIds`/`uniqueIds()`/`usesUniqueIds()` etc., as appropriate)
  4) Same as (3) but for **ULID** (e.g. `ulid`)
- **Assertions**
  - Existing behavior: primary key value is excluded/reset on `replicate()`
  - New expected behavior: non-PK unique-id attributes are excluded/reset on `replicate()`
  - If applicable for these stubs in this Laravel version: after `save()`, missing unique-id attributes are generated (assert generation only if deterministic/standard for the concern in this version)

##### Implementation Checklist
- [ ] Inspect `tasks/task_3_laravel_framework.csv` and mirror the relevant test patch content precisely (names, expectations, and structure) so the evaluation harness matches.
- [ ] Add new test methods adjacent to existing clone/replicate tests to minimize drift and keep intent clear.
- [ ] Implement the 4 minimal model stubs required by the scenarios.
- [ ] Ensure the “non-PK unique-id” models exercise the canonical unique-id API for this Laravel version (no custom generation logic).
- [ ] Ensure at least one new/updated test demonstrates the **current baseline failure**: replication incorrectly copies non-PK UUID/ULID unique-id attributes.

##### Success Criteria
- [ ] On baseline (before task 8), at least one test fails because `replicate()` carries over a non-PK UUID/ULID unique-id attribute.
- [ ] After task 8, all new tests pass.
- [ ] No unrelated test expectations are changed; existing replicate/clone tests remain intact unless the CSV patch explicitly updates them.

##### Files to Read
- `tasks/task_3_laravel_framework.csv`
- `Planning Agent Eval - eval_1.csv` (only for confirmation if the CSV is hard to interpret)
- `tests/Database/DatabaseEloquentModelTest.php`

##### Files to Modify
- `tests/Database/DatabaseEloquentModelTest.php`


### 2. Fix Eloquent Model::replicate() to avoid copying UUID/ULID unique identifiers on non-primary keys

#### Description

Implement and validate a change in Laravel Eloquent `Model::replicate()` such that when a model uses `HasUuids`/`HasUlids` on *non-primary key* columns, replication will not carry over those unique identifiers by default (similar to how primary key is excluded). Must satisfy/align with tests introduced in `tasks/task_3_laravel_framework.csv` (mirrored in `Planning Agent Eval - eval_1.csv` around the lines matching `testCloneModelMakesAFreshCopyOfTheModelWhenModelHasUuidPrimaryKey` and the associated ULID/unique-column scenarios).

Key known behavior from CSV snippet:
- Replication currently excludes the model primary key but not additional unique keys.
- This becomes a practical bug when `HasUuids` or `HasUlids` are used for unique columns that are not the primary key: replicate() retains them, leading to unique constraint violations or unintended identifier reuse.

Constraints:
- Backward compatible for models not using HasUuids/HasUlids.
- No regressions for UUID/ULID primary key models (still excluded as today).
- Tests: add/update unit tests in `DatabaseEloquentModelTest` per CSV patch and ensure they pass.

Note: This plan assumes we can inspect and modify Laravel framework source in this workspace (typical paths: `src/Illuminate/Database/Eloquent/Model.php`, concerns under `src/Illuminate/Database/Eloquent/Concerns/`).


### 3. Implementation: update Model::replicate() exclusion list to also exclude unique-id attributes (Epic: Fix Eloquent Model::replicate() to avoid copying UUID/ULID unique identifiers on non-primary keys)

#### Description

Modify `Illuminate\Database\Eloquent\Model::replicate()` so it excludes unique-id columns (UUID/ULID) in addition to the primary key.

Implementation details:
- Locate `replicate()` in `src/Illuminate/Database/Eloquent/Model.php`.
- Identify the canonical API for unique-id columns used by `HasUuids`/`HasUlids` in this Laravel version (commonly via a shared concern like `HasUniqueIds` exposing `uniqueIds()` and/or a boolean like `usesUniqueIds()` / `uniqueIdsShouldBeGenerated()`).
- When building the `$except` list inside `replicate()`:
  - Keep existing behavior: exclude primary key, timestamps, and any caller-provided `$except`.
  - If the model indicates it uses generated unique IDs, merge `uniqueIds()` into the exclusion list.
  - Ensure the primary key is not re-added redundantly.
  - Ensure this code path is a no-op for models without the unique-id concern methods.

Acceptance criteria:
- New tests pass.
- Existing replicate tests pass.
- No behavior change for models that do not opt into UUID/ULID generation concerns.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Tests: implement task_3 scenarios for replicate() with UUID/ULID unique-id columns
    - current (in progress task): Implementation: update Model::replicate() exclusion list to also exclude unique-id attributes <-
    - upcoming (not yet): Validation: run Eloquent replicate/clone test suite and confirm no regressions
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Update Laravel Eloquent `Illuminate\Database\Eloquent\Model::replicate()` to also exclude UUID/ULID-generated unique-id attributes on replication (including non-primary-key columns), while preserving backward compatibility and existing replicate semantics.

##### Technical Specs
- **Target**
  - `src/Illuminate/Database/Eloquent/Model.php`, method `replicate(array $except = null)` (exact signature may vary slightly by version).
- **Behavioral change**
  - Current replicate exclusion set includes: primary key, timestamps, and any caller-provided `$except`.
  - Extend the exclusion set to also include **unique-id attributes** generated by UUID/ULID concerns when the model indicates it uses them.
- **Version-aware API usage**
  - Determine the canonical mechanism in this codebase for “unique id columns” (commonly via a concern like `HasUniqueIds` with methods such as `uniqueIds()`, `usesUniqueIds()`, `uniqueIdsShouldBeGenerated()`, etc.).
  - Implement the replicate logic using those existing methods (no new public API unless absolutely required by the framework style).
- **Compatibility constraints**
  - For models that do **not** use UUID/ULID generation concerns, behavior must remain unchanged.
  - For UUID/ULID **primary key** models, keep existing behavior (PK excluded as today).
  - Avoid hard dependencies on methods that may not exist on all models; guard calls appropriately.

##### Implementation Checklist
- [ ] Locate `Model::replicate()` and identify how `$except` is constructed today (PK, timestamps, and provided `$except`).
- [ ] Identify the unique-id concern API available in this Laravel version and the method(s) to obtain the unique-id column list.
- [ ] Merge unique-id column names into the replicate exclusion list **only when** the model indicates it uses generated unique IDs.
- [ ] Ensure the primary key is not redundantly added and the final exclusion list is unique/deduplicated.
- [ ] Ensure the implementation is a no-op for models not using unique IDs (including models that don’t have the unique-id methods).
- [ ] Keep the change localized to `replicate()` unless a tiny internal helper is needed for clarity (avoid broad refactors).

##### Success Criteria
- [ ] All tests added/updated in task 7 pass.
- [ ] Existing replicate/clone tests pass unchanged (except where the CSV patch explicitly modifies them).
- [ ] Replicate behavior for non-UUID/ULID models is unchanged by code review: no new exclusions unless the model uses unique-id generation concerns.

##### Dependencies
- Depends on task (7) tests to define the expected behavior clearly.

##### Files to Read
- `src/Illuminate/Database/Eloquent/Model.php`
- Any related concerns:
  - `src/Illuminate/Database/Eloquent/Concerns/HasUuids.php`
  - `src/Illuminate/Database/Eloquent/Concerns/HasUlids.php`
  - Any shared unique-id concern used by the above (e.g., `HasUniqueIds`)

##### Files to Modify
- `src/Illuminate/Database/Eloquent/Model.php`


### 4. Validation: run Eloquent replicate/clone test suite and confirm no regressions (Epic: Fix Eloquent Model::replicate() to avoid copying UUID/ULID unique identifiers on non-primary keys)

#### Description

Run the PHPUnit subset that includes `DatabaseEloquentModelTest` and any other replicate-related tests.

Implementation details:
- Execute PHPUnit for the database tests suite (command depends on repo conventions).
- Confirm that new tests pass and no existing tests are broken.

Acceptance criteria:
- Green test run for relevant suites.
- If failures occur, adjust the replicate implementation (not tests) to preserve backward compatibility for non-unique-id models.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implementation: update Model::replicate() exclusion list to also exclude unique-id attributes
    - current (in progress task): Validation: run Eloquent replicate/clone test suite and confirm no regressions <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Validate the replicate/clone behavior change by running the relevant PHPUnit suites and confirming no regressions beyond the intended `replicate()` semantics update.

##### Technical Specs
- **Test execution**
  - Run PHPUnit for the database-related tests, ensuring `DatabaseEloquentModelTest` is included.
  - Also run any focused subset that covers `replicate()`/cloning if such a group exists in this repo’s test configuration.
- **Failure handling**
  - If failures occur, treat them as regressions unless they are directly explained by the intended change.
  - Fix regressions by adjusting the `replicate()` implementation (task 8 scope), not by weakening or removing the new tests from task 7.

##### Implementation Checklist
- [ ] Execute the PHPUnit command(s) used by this repository for database tests (use the repo’s documented conventions).
- [ ] Confirm task 7 scenarios pass, including:
  - PK excluded on replicate
  - Non-PK UUID/ULID unique-id attributes excluded on replicate
- [ ] Scan for any newly failing tests outside the new/updated cases and attribute them to:
  - unintended broadening of exclusions, or
  - incorrect detection of unique-id usage on models not opting in
- [ ] Adjust the `Model::replicate()` change to restore backward compatibility where needed.

##### Success Criteria
- [ ] Green test run for `DatabaseEloquentModelTest` and other replicate/clone-related coverage.
- [ ] No regressions for models not using UUID/ULID unique-id generation concerns.
- [ ] No regressions for UUID/ULID primary-key models (primary key remains excluded as before).

##### Files to Read (as needed)
- PHPUnit configuration and test runner docs in the repo (e.g., `phpunit.xml*`, `composer.json` scripts)
- CI configuration (if present) for canonical test commands

##### Files to Modify
- None by default; only adjust framework code from task 8 if regressions are detected.
