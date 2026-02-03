# Plan Name: Debug Plan for Tokio CSV Task

## Tasks

### 1. Extract test case (Epic: Reproduce the bug)

#### Description

Read `tasks/task_4_tokio-rs_tokio.csv` to identify the test case logic. The CSV contains a diff that adds assertions to `fn num_blocking_threads()`.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Extract test case <-
    - upcoming (not yet): Apply test case
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Read the task file `tasks/task_4_tokio-rs_tokio.csv` to extract the reproduction test case.

This file contains the details of the bug, including a diff or code snippet that demonstrates the issue. You need to identify the changes intended for `tokio/tests/rt_metrics.rs`, specifically looking for new assertions added to the `num_blocking_threads` test function.

##### Deliverables:
- Identify the logic required to reproduce the bug.
- Output the Rust code snippet or diff that needs to be applied to the test suite.

##### Files to read:
- `tasks/task_4_tokio-rs_tokio.csv`


### 2. Fix runtime metrics blocking threads miscount (Epic: user query)

#### Description

Extract the reproduction test case and applying it to the codebase to confirm the bug. Then fix the bug by modifying the metrics calculation.


### 3. Fix the bug (Epic: Fix runtime metrics blocking threads miscount)

#### Description

Fix the bug by modifying the metrics calculation in the runtime.


### 4. user query

#### Description

locate task_4_tokio-rs_tokio.csv and create a plan to fix the bug described inside.


### 5. Reproduce the bug (Epic: Fix runtime metrics blocking threads miscount)

#### Description

Extract the reproduction test case from the task CSV and apply it to the codebase to confirm the bug.


### 6. Apply test case (Epic: Reproduce the bug)

#### Description

Apply the test case changes to `tokio/tests/rt_metrics.rs`. Specifically, add the missing assertions to `fn num_blocking_threads`.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Extract test case
    - current (in progress task): Apply test case <-
    - upcoming (not yet): Confirm failure
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Apply the reproduction test case to the `tokio` test suite.

Based on the logic extracted in the previous step, modify `tokio/tests/rt_metrics.rs`. You need to add the missing assertions to the `fn num_blocking_threads` test case (or creating it if it doesn't exist, though it likely does).

##### Implementation Checklist:
- [ ] Read `tokio/tests/rt_metrics.rs` to understand the existing test structure.
- [ ] Inject the assertions that check for the correct number of blocking threads.
- [ ] Ensure the syntax is correct and fits the existing code style.

##### Files to modify:
- `tokio/tests/rt_metrics.rs`


### 7. Confirm failure (Epic: Reproduce the bug)

#### Description

Run the tests in `tokio/tests/rt_metrics.rs` to confirm that `num_blocking_threads` fails as expected.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply test case
    - current (in progress task): Confirm failure <-
    - upcoming (not yet): Locate code
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Confirm that the test fails as expected.

Now that the reproduction assertions are in place, run the tests to confirm the bug exists. We expect the `num_blocking_threads` test to fail due to the miscount.

##### Implementation Checklist:
- [ ] Run the specific test file using cargo (e.g., `cargo test --test rt_metrics`).
- [ ] Verify that the test fails.
- [ ] Record the failure output, specifically note the difference between the expected and actual thread count.

##### Success Criteria:
- [ ] Test fails.
- [ ] Failure message indicates a mismatch in blocking thread count (likely off by the number of worker threads).


### 8. Locate code (Epic: Fix the bug)

#### Description

Locate the implementation of `num_blocking_threads` in the `tokio` source code (likely in `tokio/src/runtime` metrics module). Analyze how it counts threads.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Confirm failure
    - current (in progress task): Locate code <-
    - upcoming (not yet): Apply fix
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate the implementation of `num_blocking_threads` to analyze the bug.

We need to understand how the runtime counts blocking threads. Search the codebase for the definition of `num_blocking_threads` within the `tokio` runtime source code.

##### Implementation Checklist:
- [ ] Search for `fn num_blocking_threads` in `tokio/src`.
- [ ] Read the implementation and any helper functions it calls.
- [ ] specific focus: Check if the calculation sums up different metrics and if `worker_threads` are explicitly or implicitly included in the result.

##### Files to read:
- `tokio/src/runtime/**` (Start search here)


### 9. Apply fix (Epic: Fix the bug)

#### Description

Modify the `num_blocking_threads` implementation to avoid double counting worker threads. The likely fix is to subtract the number of worker threads from the total if they are being included in the blocking count inappropriately.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate code
    - current (in progress task): Apply fix <-
    - upcoming (not yet): Verify fix
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Apply the fix for the `num_blocking_threads` miscount in the Tokio runtime metrics.

##### Context
We have identified that `num_blocking_threads()` returns an incorrect value, likely because it double-counts worker threads or includes them in the blocking thread count inappropriately. The goal is to adjust the calculation so that it accurately reflects only the number of blocking threads.

##### Technical Specs
- **Location**: Implementation of `num_blocking_threads` (likely in `tokio/src/runtime/metrics/runtime.rs` or `tokio/src/runtime/metrics/mod.rs` inside the `RuntimeMetrics` struct/impl).
- **Logic Change**: 
  - Analyze the current implementation of `num_blocking_threads`.
  - If it returns a total count of threads (blocking + workers), subtract the number of worker threads to isolate the blocking threads.
  - Ensure the resulting value represents the correct number of blocking threads as expected by the test case in `tokio/tests/rt_metrics.rs`.

##### Implementation Checklist
- [ ] Locate the `num_blocking_threads` method in the `tokio` runtime metrics source code.
- [ ] Modify the return value calculation to subtract `worker_threads` if the underlying metric includes them.
- [ ] Ensure the calculation handles cases where the subtraction might underflow (though unlikely if logic is correct) or adheres to the correct type (likely `usize`).

##### Success Criteria
- [ ] The code compiles successfully.
- [ ] The logic change aligns with the hypothesis that blocking threads were over-reported by the count of worker threads.


### 10. Verify fix (Epic: Fix the bug)

#### Description

Run the reproduction test case again to verify that the bug is fixed and `num_blocking_threads` reports the correct value.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply fix
    - current (in progress task): Verify fix <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify the fix for `num_blocking_threads` by running the reproduction test case.

##### Context
A reproduction test case was previously added to `tokio/tests/rt_metrics.rs` (specifically in `fn num_blocking_threads()`) which failed before the fix. We must now confirm that the fix applied in the previous step resolves the issue.

##### Technical Specs
- **Test File**: `tokio/tests/rt_metrics.rs`
- **Action**: Run the tests to confirm the assertion passes.

##### Implementation Checklist
- [ ] Run the specific test case: `cargo test --test rt_metrics num_blocking_threads` (or the relevant test function name).
- [ ] Verify that the test passes.
- [ ] If the test fails, analyze the failure output to determine if the logic in the fix needs adjustment.

##### Success Criteria
- [ ] `tokio/tests/rt_metrics.rs` compiles and runs.
- [ ] The `num_blocking_threads` test case passes with the new implementation.
