# Plan Name: Analyze CSV File and Create Bug Patch Plan

## Tasks

### 1. Apply reproduction patch (Epic: Fix fmt::sprintf ignoring minus flag for char)

#### Description

Apply the test patch provided in `tasks/task_1_fmtlib_fmt.csv` to `test/printf-test.cc`. This will introduce the failing test cases:
- `EXPECT_PRINTF("7    ", "%-5d", 7);`
- `EXPECT_PRINTF("97   ", "%-5hhi", 'a');`
- `EXPECT_PRINTF("a    ", "%-5c", 'a');`


#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Apply reproduction patch <-
    - upcoming (not yet): Confirm bug reproduction
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

This task involves setting up the reproduction case for the reported issue. You need to apply a patch provided in a CSV file to the test suite.

##### Steps:
1.  Read the file `tasks/task_1_fmtlib_fmt.csv`.
2.  Extract the patch or code changes specified for `test/printf-test.cc`.
3.  Apply these changes to `test/printf-test.cc`. This should introduce a new test case (likely named `PrintfTest.MinusFlag` or similar) that asserts the behavior of the minus flag with `char` types.

##### Deliverables:
- Modified `test/printf-test.cc` containing the new test cases:
    - `EXPECT_PRINTF("7    ", "%-5d", 7);`
    - `EXPECT_PRINTF("97   ", "%-5hhi", 'a');`
    - `EXPECT_PRINTF("a    ", "%-5c", 'a');`

##### Files to read:
- `tasks/task_1_fmtlib_fmt.csv`
- `test/printf-test.cc`

##### Files to modify:
- `test/printf-test.cc`


### 2. Fix fmt::sprintf ignoring minus flag for char

#### Description

The goal is to fix a bug in `fmt::sprintf` where the minus flag (left-alignment) is ignored for `char` types.
The plan involves reproducing the issue with the provided patch, locating the defect in `include/fmt/printf.h` (inferred location), and implementing a fix.



### 3. Confirm bug reproduction (Epic: Fix fmt::sprintf ignoring minus flag for char)

#### Description

Build and run the tests to confirm that `PrintfTest.MinusFlag` fails.
Expected failure: The output for char formatting will be right-aligned instead of left-aligned.
Command (typical): `cmake . && make && test/printf-test` or `ctest -R PrintfTest.MinusFlag`

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply reproduction patch
    - current (in progress task): Confirm bug reproduction <-
    - upcoming (not yet): Analyze printf implementation
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Now that the reproduction test case has been applied, you need to confirm that it fails as expected.

##### Implementation Checklist:
- [ ] Build the project using CMake and Make (or standard build tools available in the environment).
- [ ] Run the specific test case added in the previous step (e.g., `ctest -R PrintfTest.MinusFlag` or by running the test binary directly).
- [ ] Verify that the test fails.
- [ ] Analyze the failure output. The failure should demonstrate that the output is right-aligned (default) instead of left-aligned (minus flag), e.g., expecting `"a    "` but getting `"    a"`.

##### Success Criteria:
- [ ] The build completes successfully.
- [ ] The test `PrintfTest.MinusFlag` is executed.
- [ ] The test fails specifically on the assertion for the `char` type with the minus flag.


### 4. Analyze printf implementation (Epic: Fix fmt::sprintf ignoring minus flag for char)

#### Description

Locate the implementation of `sprintf` and `printf` formatting in the codebase.
Based on standard fmtlib structure, this is likely in `include/fmt/printf.h`.
Identify the code path that handles the `%c` specifier and why it ignores the alignment flag.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Confirm bug reproduction
    - current (in progress task): Analyze printf implementation <-
    - upcoming (not yet): Implement fix in source code
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Analyze the codebase to locate the defect causing the test failure.

##### Implementation Checklist:
- [ ] Locate the implementation of `sprintf` and its underlying formatting logic in `include/fmt/printf.h`.
- [ ] Trace how the `%c` specifier is parsed and formatted.
- [ ] Identify where the alignment flags (specifically the minus flag) are handled for other types versus `char`.
- [ ] Determine why the alignment logic is skipped or ignored for `char`.

##### Success Criteria:
- [ ] The specific function or code block responsible for formatting `char` in `printf` context is identified.
- [ ] The reason for the missing left-alignment is understood (e.g., missing branch, incorrect flag check, or direct character write bypassing padding logic).

##### Files to read:
- `include/fmt/printf.h`


### 5. Implement fix in source code (Epic: Fix fmt::sprintf ignoring minus flag for char)

#### Description

Modify the code in `include/fmt/printf.h` (or relevant file) to ensure that when `char` is formatted with the minus flag (e.g., `%-5c`), it is correctly left-aligned.
Ensure that existing flags (width, etc.) are still respected.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Analyze printf implementation
    - current (in progress task): Implement fix in source code <-
    - upcoming (not yet): Verify fix with reproduction test
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement the fix for the `sprintf` minus flag bug.

##### Implementation Checklist:
- [ ] Modify `include/fmt/printf.h` (or the file identified in the previous analysis).
- [ ] Ensure that when a `char` is formatted with the minus flag (e.g., `%-5c`), the output is padded to the right (left-aligned).
- [ ] Ensure that standard width formatting still applies (e.g., `%5c` should still be right-aligned).
- [ ] Ensure no changes break existing functionality for other types or standard `printf` behavior.

##### Success Criteria:
- [ ] The code explicitly handles left-alignment for character formatting in `sprintf`.

##### Files to modify:
- `include/fmt/printf.h`


### 6. Verify fix with reproduction test (Epic: Fix fmt::sprintf ignoring minus flag for char)

#### Description

Run the specific test case `PrintfTest.MinusFlag` again to verify that the fix works.
The test should now pass, producing left-aligned output for the char cases.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement fix in source code
    - current (in progress task): Verify fix with reproduction test <-
    - upcoming (not yet): Run full regression tests
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify that the fix for `fmt::sprintf` (ignoring minus flag for char) works as expected.

##### Implementation Checklist:
  - [ ] Rebuild the project if necessary (ensure changes from the fix are compiled).
  - [ ] Run the specific test case `PrintfTest.MinusFlag`.
    - Command (typical): `ctest -R PrintfTest.MinusFlag` or `./test/printf-test` with appropriate filtering.
  - [ ] Verify that the test output indicates **PASS**.

##### Success Criteria:
  - [ ] `PrintfTest.MinusFlag` passes successfully.
  - [ ] The output for the char cases is left-aligned (implied by the test passing).

##### Dependencies:
  - The fix must be implemented in the source code (Task 15).
  - The reproduction test must exist in `test/printf-test.cc` (Task 12).


### 7. Run full regression tests (Epic: Fix fmt::sprintf ignoring minus flag for char)

#### Description

Run the full test suite to ensure that the changes didn't break any other functionality in the library.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Verify fix with reproduction test
    - current (in progress task): Run full regression tests <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run the full regression test suite to ensure the changes to `fmt::sprintf` did not break existing functionality.

##### Implementation Checklist:
  - [ ] Build the full project to ensure all tests are up to date.
  - [ ] Run the complete test suite.
    - Command (typical): `ctest` or `make test`.
  - [ ] Review the output for any failures.

##### Success Criteria:
  - [ ] All tests in the suite pass (100% tests passed).
  - [ ] No new errors or regressions are reported.

##### Dependencies:
  - The fix must be verified on the specific test case first (Task 16).
