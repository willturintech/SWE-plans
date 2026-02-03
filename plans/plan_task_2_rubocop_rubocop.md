# Plan Name: Identify and Plan Bug Fix from RuboCop CSV Report

## Tasks

### 1. Extract bug details (Epic: Analyze and Reproduce Bug)

#### Description

Read `tasks/task_2_rubocop_rubocop.csv` to extract the detailed bug description and the provided reproduction patch/snippet.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Extract bug details <-
    - upcoming (not yet): Verify environment
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Analyze the provided task file to understand the bug and extract reproduction steps.

##### Action Items:
- Read the content of `tasks/task_2_rubocop_rubocop.csv`.
- Extract the detailed problem description regarding the RuboCop exit status bug.
- Locate and extract the reproduction patch or code snippet provided in the CSV.

##### Success Criteria:
- A summary of the bug is generated.
- The reproduction test case/snippet is extracted and ready for use in subsequent steps.


### 2. Implement Fix (Epic: Fix RuboCop Exit Status for --display-only-correctable)

#### Description

Modify the RuboCop codebase to ensure the exit status is 0 when `--display-only-correctable` is used and only uncorrectable offenses are found.


### 3. Analyze and Reproduce Bug (Epic: Fix RuboCop Exit Status for --display-only-correctable)

#### Description

Analyze the bug report and reproduction steps provided in `tasks/task_2_rubocop_rubocop.csv`. Create a reproduction test case in the RuboCop codebase to confirm the issue.


### 4. Fix RuboCop Exit Status for --display-only-correctable

#### Description

Fix the bug where RuboCop returns exit status 1 when `--display-only-correctable` is used and only uncorrectable offenses exist, despite reporting 'no offenses detected'.


### 5. Verify environment (Epic: Analyze and Reproduce Bug)

#### Description

Locate `spec/rubocop/cli_spec.rb` in the repository to ensure the environment is correct and the file exists.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Extract bug details
    - current (in progress task): Verify environment <-
    - upcoming (not yet): Create reproduction test
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify the existence of the relevant test file in the codebase.

##### Action Items:
- Check for the existence of `spec/rubocop/cli_spec.rb`.
- Confirm it is the correct location for adding command-line interface tests.

##### Success Criteria:
- `spec/rubocop/cli_spec.rb` exists and is accessible.


### 6. Create reproduction test (Epic: Analyze and Reproduce Bug)

#### Description

Apply the reproduction test case (extracted from the CSV) into `spec/rubocop/cli_spec.rb` or a new spec file. The test should run `rubocop --display-only-correctable` on a file with uncorrectable offenses and expect exit code 0.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Verify environment
    - current (in progress task): Create reproduction test <-
    - upcoming (not yet): Confirm bug reproduction
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement the reproduction test case to expose the bug.

##### Action Items:
- Open `spec/rubocop/cli_spec.rb`.
- Append a new test case derived from the patch extracted in the previous analysis (from `tasks/task_2_rubocop_rubocop.csv`).
- The test case must:
  - Run RuboCop with the `--display-only-correctable` flag.
  - Analyze a file (can be a temporary file created within the test) that contains **uncorrectable** offenses.
  - Assert that the exit status is `0` (Success).
  - Note: This test is expected to fail on the current codebase.

##### Success Criteria:
- A new `describe`/`it` block is added to `spec/rubocop/cli_spec.rb` covering the reported scenario.
- The test asserts the correct behavior (exit code 0).


### 7. Confirm bug reproduction (Epic: Analyze and Reproduce Bug)

#### Description

Run the newly created test to confirm it fails with the current codebase (expecting exit code 1 instead of 0).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Create reproduction test
    - current (in progress task): Confirm bug reproduction <-
    - upcoming (not yet): Locate exit code logic
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Execute the newly created test to confirm the bug exists in the current codebase.

##### Action Items:
- Run the tests in `spec/rubocop/cli_spec.rb` (or the specific test case added).
- Observe the output and exit code.

##### Success Criteria:
- The reproduction test **fails**.
- The failure indicates that the actual exit status was `1` (or non-zero) instead of the expected `0`.
- This confirms the bug described in the issue.


### 8. Locate exit code logic (Epic: Implement Fix)

#### Description

Investigate `lib/rubocop/cli.rb`, `lib/rubocop/runner.rb`, or related files to identify where the exit code is calculated and where the `--display-only-correctable` flag is handled.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Confirm bug reproduction
    - current (in progress task): Locate exit code logic <-
    - upcoming (not yet): Implement exit code fix
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Investigate the codebase to identify the logic responsible for calculating the CLI exit code and handling the `--display-only-correctable` flag.

##### Goal
Locate the specific methods and lines of code that need modification to ensure the exit status is 0 when `--display-only-correctable` is used and only uncorrectable offenses are present.

##### Files to Investigate
- `lib/rubocop/cli.rb`
- `lib/rubocop/runner.rb`
- `lib/rubocop/options.rb` (if applicable)

##### Investigation Checklist
- [ ] Identify where command-line arguments (specifically `--display-only-correctable`) are parsed and stored.
- [ ] Trace the execution flow in `CLI#run` or `Runner#run`.
- [ ] Locate where the final exit code (e.g., `0` for success, `1` for offenses) is determined.
- [ ] Determine how the runner currently counts offenses versus how it filters them for display.


### 9. Implement exit code fix (Epic: Implement Fix)

#### Description

Modify the exit code logic to check if `--display-only-correctable` is active. If so, and if there are offenses but they are all uncorrectable (or explicitly ignored by the display flag), force exit code 0.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate exit code logic
    - current (in progress task): Implement exit code fix <-
    - upcoming (not yet): Verify fix
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Modify the RuboCop exit code logic to fix the reported bug.

##### Context
Currently, when running with `--display-only-correctable`, if there are offenses but none are autocorrectable, RuboCop outputs "no offenses detected" but exits with status 1. It should exit with status 0.

##### Technical Specs
- **Logic Change**: In the exit code calculation (likely in `lib/rubocop/cli.rb` or `lib/rubocop/runner.rb`), check if the `--display-only-correctable` option is enabled.
- **Condition**: If the option is enabled, and the remaining offenses (those that would be displayed) count is zero, force the exit code to be 0 (success), even if the raw offense count is non-zero.

##### Implementation Checklist
- [ ] Modify the logic to verify if `--display-only-correctable` is active.
- [ ] Adjust the return value/exit status calculation to return 0 if all detected offenses are uncorrectable and the display flag is set.

##### Files to Modify
- `lib/rubocop/cli.rb` (or `lib/rubocop/runner.rb` depending on investigation findings)


### 10. Verify fix (Epic: Implement Fix)

#### Description

Run the reproduction test case again to verify it now passes (exit code 0).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement exit code fix
    - current (in progress task): Verify fix <-
    - upcoming (not yet): Regression testing
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify the fix by running the reproduction test case created in previous steps.

##### Success Criteria
- [ ] The test case for `--display-only-correctable` with uncorrectable offenses must pass.
- [ ] The exit code returned by the test command must be `0`.

##### Instructions
- Run the spec file modified in the reproduction step (likely `spec/rubocop/cli_spec.rb`).
- Ensure the specific test case describing this bug passes.


### 11. Regression testing (Epic: Implement Fix)

#### Description

Run other relevant tests (e.g., `spec/rubocop/cli_spec.rb`) to ensure no regressions in other exit code scenarios.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Verify fix
    - current (in progress task): Regression testing <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Perform regression testing to ensure the changes do not break existing functionality.

##### Instructions
- Run the full suite of CLI specs to ensure standard exit code behavior (0 for success, 1 for offenses) remains correct for normal runs (without the flag).
- Ensure that runs *with* correctable offenses still exit with 1 (or 0 if corrected) as appropriate.

##### Implementation Checklist
- [ ] Run `bundle exec rspec spec/rubocop/cli_spec.rb` (or equivalent).
- [ ] Verify all tests pass.
