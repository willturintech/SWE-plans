# Plan Name: Locate and Fix RuboCop CSV Bug

## Tasks

### 1. Setup Environment (Epic: Explore and Reproduce)

#### Description

Checkout the repository and setup the environment.
Note: This is a ruby project. Ensure ruby and dependencies are installed.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Setup Environment <-
    - upcoming (not yet): Create Reproduction Case
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Set up the development environment for the RuboCop project.

##### Implementation Checklist:
  - [ ] Check the current directory content to verify the structure.
  - [ ] Ensure Ruby is installed and available.
  - [ ] Install dependencies using `bundle install`.

##### Success Criteria:
  - [ ] `bundle check` or `bundle install` completes successfully.
  - [ ] The environment is ready for running specs and ruby scripts.


### 2. Verify Fix (Epic: Fix Style/RedundantParentheses Bug)

#### Description

Verify the fix ensures the reported issue is resolved and no regressions are introduced


### 3. Explore and Reproduce (Epic: Fix Style/RedundantParentheses Bug)

#### Description

Explore the codebase and reproduce the issue reported in task_4_rubocop_rubocop.csv


### 4. Implement Fix (Epic: Fix Style/RedundantParentheses Bug)

#### Description

Implement the fix for the reported issue


### 5. Fix Style/RedundantParentheses Bug

#### Description

Fix the RuboCop Style/RedundantParentheses bug where it fails to detect redundant parentheses around lambda/proc with brace blocks.


### 6. Create Reproduction Case (Epic: Explore and Reproduce)

#### Description

Create a reproduction script `reproduce_issue.rb` or a spec file that demonstrates the failure.
The issue is that `Style/RedundantParentheses` does not detect redundant parentheses around `lambda { ... }` or `proc { ... }`.
Example: `->() { ... }` or `lambda() { ... }` might be okay, but `(lambda { ... })` might be the issue?
Wait, the description says "redundant parens around lambda/proc with brace blocks".
Example: `(lambda { ... })` or `(proc { ... })`.
I need to check the problem statement in the CSV to be precise.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Setup Environment
    - current (in progress task): Create Reproduction Case <-
    - upcoming (not yet): Analyze Code
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Create a reproduction case to demonstrate the `Style/RedundantParentheses` bug.

##### Context
The issue is described in `tasks/task_4_rubocop_rubocop.csv`. It states that `Style/RedundantParentheses` fails to detect redundant parentheses around `lambda` or `proc` with brace blocks (e.g., `(lambda { ... })`).

##### Implementation Checklist:
  - [ ] Read `tasks/task_4_rubocop_rubocop.csv` to confirm the exact problem description and any examples.
  - [ ] Create a file named `reproduce_issue.rb` containing code that uses redundant parentheses around `lambda { ... }` and `proc { ... }`.
  - [ ] Run `rubocop` (using `bundle exec rubocop`) specifically on `reproduce_issue.rb`.
  - [ ] Confirm that RuboCop currently **fails** to report an offense for these lines (demonstrating the bug).

##### Success Criteria:
  - [ ] `reproduce_issue.rb` exists with valid Ruby code illustrating the issue.
  - [ ] Running RuboCop on this file yields no offenses (proving the false negative).


### 7. Analyze Code (Epic: Implement Fix)

#### Description

Analyze `lib/rubocop/cop/style/redundant_parentheses.rb` (or similar path) to understand why it ignores brace blocks for lambdas/procs.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Create Reproduction Case
    - current (in progress task): Analyze Code <-
    - upcoming (not yet): Apply Fix
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Analyze the existing implementation of `Style/RedundantParentheses` to identify why it ignores brace blocks for lambdas and procs.

##### Implementation Checklist:
  - [ ] Locate the file `lib/rubocop/cop/style/redundant_parentheses.rb`.
  - [ ] Read the code to understand the criteria used to determine if parentheses are redundant.
  - [ ] Specifically look for logic that might exclude block nodes, `lambda`, or `proc` nodes, or logic that handles precedence and might be overly conservative regarding braces.
  - [ ] Document your findings briefly in `analysis_notes.md`, explaining which method or condition prevents the detection.

##### Success Criteria:
  - [ ] Root cause identified in the source code.
  - [ ] `analysis_notes.md` created with a brief explanation of the logic gap.


### 8. Apply Fix (Epic: Implement Fix)

#### Description

Modify `Style/RedundantParentheses` to detect and autocorrect redundant parentheses around lambda/proc with brace blocks.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Analyze Code
    - current (in progress task): Apply Fix <-
    - upcoming (not yet): Verify Reproduction
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement the fix for `Style/RedundantParentheses` to detect and autocorrect redundant parentheses around lambda/proc with brace blocks.

##### Technical Specs:
  - **Cop:** `Style/RedundantParentheses`
  - **Change:** Update the logic to allow flagging parentheses as redundant when wrapping a `lambda` or `proc` call with a brace block (e.g., `(lambda { })`).
  - **Safety:** Ensure this does not flag cases where parentheses are required (e.g., method calls on the result, or precedence issues, though brace blocks bind tightly).

##### Implementation Checklist:
  - [ ] Modify `lib/rubocop/cop/style/redundant_parentheses.rb` to address the issue identified in the analysis.
  - [ ] Run the reproduction script `reproduce_issue.rb` using `bundle exec rubocop`.
  - [ ] Verify that it now reports offenses for the redundant parentheses.
  - [ ] Run `bundle exec rubocop -a reproduce_issue.rb` to verify autocorrection works (should remove the parentheses).

##### Success Criteria:
  - [ ] The reproduction script now triggers `Style/RedundantParentheses` offenses.
  - [ ] Autocorrection successfully removes the redundant parentheses.


### 9. Verify Reproduction (Epic: Verify Fix)

#### Description

Run the reproduction case and ensure it passes (offense detected and autocorrected).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply Fix
    - current (in progress task): Verify Reproduction <-
    - upcoming (not yet): Run Regression Tests
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify that the implementation fix resolves the reported issue using the reproduction script created earlier.

##### Context
We have implemented a fix in `Style/RedundantParentheses` to detect redundant parentheses around lambda/proc with brace blocks (e.g., `(lambda { ... })`). We now need to confirm this fix works as expected.

##### Instructions
1.  **Run Reproduction Script**: Execute the reproduction script or spec created in the previous exploration phase (`reproduce_issue.rb` or similar).
2.  **Verify Offense Detection**: Ensure that RuboCop now reports an offense for the previously ignored case.
3.  **Verify Autocorrection**: Run RuboCop with the autocorrect flag (`-a` or `-A`) on the reproduction case and verify that the redundant parentheses are removed correctly.
    - Example input: `(lambda { result })`
    - Expected output: `lambda { result }`

##### Success Criteria:
- [ ] The reproduction script detects the offense `Style/RedundantParentheses`.
- [ ] Autocorrection successfully removes the redundant parentheses without syntax errors.

##### Dependencies:
- The fix must be applied to `lib/rubocop/cop/style/redundant_parentheses.rb`.


### 10. Run Regression Tests (Epic: Verify Fix)

#### Description

Run existing specs for `Style/RedundantParentheses` to ensure no regressions.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Verify Reproduction
    - current (in progress task): Run Regression Tests <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run the existing regression tests to ensure the changes to `Style/RedundantParentheses` have not introduced any side effects.

##### Context
Changes were made to `Style/RedundantParentheses` to handle brace blocks in lambdas/procs. We must ensure that existing behavior (handling of other redundant parentheses cases) remains intact.

##### Instructions
1.  **Locate Specs**: Find the existing spec file for this cop. It is likely located at `spec/rubocop/cop/style/redundant_parentheses_spec.rb`.
2.  **Run Specs**: Execute the specs using `bundle exec rspec <path_to_spec_file>`.
3.  **Analyze Results**:
    - If all tests pass, the task is complete.
    - If there are failures, report them. Do not attempt to fix unrelated bugs, but fix regressions caused by recent changes if simple.

##### Success Criteria:
- [ ] All examples in `spec/rubocop/cop/style/redundant_parentheses_spec.rb` pass.
- [ ] No new failures or errors are introduced.

##### Files to read:
- `spec/rubocop/cop/style/redundant_parentheses_spec.rb`
