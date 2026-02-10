# Plan Name: Create Bug Fix Plan for CSV Task

## Tasks

### 1. Locate and analyze sprintf char formatting implementation (Epic: Fix sprintf minus flag bug for char formatting)

#### Description

Explore the fmtlib/fmt codebase to locate the sprintf implementation files (likely include/fmt/printf.h or src/printf.cc). Identify the specific function or code section that handles char type formatting. Map out the code flow from format string parsing through to char output. Document the file paths and function names involved in char formatting.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Locate and analyze sprintf char formatting implementation <-
    - upcoming (not yet): Identify root cause of minus flag being ignored for char
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate and document the sprintf char formatting implementation in the fmtlib/fmt codebase. This is an investigation task to map out the code architecture.

##### Technical Specs:
  - **Code Exploration**: Search the codebase for sprintf implementation, likely in `include/fmt/printf.h` or `src/printf.cc`
  - **Function Identification**: Find the specific function(s) that handle char type (`%c`) formatting
  - **Flow Mapping**: Trace the code path from format string parsing → type detection → char formatting → output
  - **Documentation**: Create clear notes on file paths, function names, and key code sections

##### Implementation Checklist:
  - [ ] Locate the main sprintf implementation file(s)
  - [ ] Identify the entry point function for sprintf formatting
  - [ ] Find where format specifiers are parsed (where `%c`, `%d`, etc. are detected)
  - [ ] Locate the char-specific formatting function/code block
  - [ ] Map out the call chain from sprintf entry to char output
  - [ ] Document any relevant structs, classes, or helper functions involved

##### Success Criteria:
  - [ ] Clear identification of all files involved in char formatting
  - [ ] Documented function names and their responsibilities
  - [ ] Understanding of how format string parsing routes to char formatter
  - [ ] Notes are sufficient for the next developer to navigate directly to the char formatting logic

##### Files to Explore:
  - `include/fmt/printf.h`
  - `src/printf.cc` (if exists)
  - Any related header files referenced by the above

---


### 2. Fix sprintf minus flag bug for char formatting

#### Description

Fix the bug where fmt::sprintf ignores the minus flag (-) when formatting char type, causing incorrect right-alignment instead of left-alignment. The expected behavior is that '%-5c' with 'a' should produce 'a    ' (left-aligned with right padding) to match std::printf behavior.


### 3. Identify root cause of minus flag being ignored for char (Epic: Fix sprintf minus flag bug for char formatting)

#### Description

Analyze why the minus flag works correctly for other types (%-5d produces '7    ', %-5hhi produces '97   ') but fails for char type (%-5c produces '    a' instead of 'a    '). Compare the code paths for integer formatting vs char formatting. Identify where the alignment/padding logic differs. Determine if the minus flag is not being passed to the char formatter, or if the char formatter is not respecting it. Document the specific code location and logic causing the bug.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate and analyze sprintf char formatting implementation
    - current (in progress task): Identify root cause of minus flag being ignored for char <-
    - upcoming (not yet): Implement fix to respect minus flag for char formatting
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Identify the root cause of why the minus flag (`-`) is ignored for char formatting while working correctly for other types. This requires comparative analysis of different formatting code paths.

##### Technical Specs:
  - **Comparative Analysis**: Compare integer formatting (`%-5d`) vs char formatting (`%-5c`) code paths
  - **Flag Processing**: Trace how the minus flag is parsed and passed to formatters
  - **Alignment Logic**: Identify where padding/alignment decisions are made for each type
  - **Bug Isolation**: Determine whether the flag isn't being passed to char formatter, or if char formatter ignores it

##### Implementation Checklist:
  - [ ] Document how integer formatting handles the minus flag (reference: `%-5d` → `"7    "` works correctly)
  - [ ] Document how char-as-integer formatting handles the minus flag (reference: `%-5hhi` → `"97   "` works correctly)
  - [ ] Document how char formatting currently handles (or ignores) the minus flag (reference: `%-5c` → `"    a"` bug)
  - [ ] Identify the specific code location where char formatting diverges from integer formatting
  - [ ] Determine if the alignment flag struct/parameter is missing or being ignored in char path
  - [ ] Document the exact line(s) of code causing the bug

##### Success Criteria:
  - [ ] Clear explanation of why integer/char-as-int formatting works but char formatting fails
  - [ ] Specific code location(s) identified where the bug occurs
  - [ ] Understanding of whether the issue is in flag parsing, flag passing, or flag application
  - [ ] Root cause documented with enough detail to guide the fix implementation

##### Dependencies:
  - Task #2 (code location mapping) should be completed first

##### Files to Analyze:
  - Files identified in task #2 containing sprintf and char formatting logic

---


### 4. Implement fix to respect minus flag for char formatting (Epic: Fix sprintf minus flag bug for char formatting)

#### Description

Modify the char formatting code to properly handle the minus flag for left-alignment. Ensure that when the minus flag is present, the char is left-aligned with padding spaces added to the right (e.g., 'a    ' for %-5c with 'a'). Follow the same pattern used by integer and string formatters. Make minimal changes to avoid breaking existing functionality. The fix should make fmt::sprintf behavior match std::printf for char formatting with minus flag.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Identify root cause of minus flag being ignored for char
    - current (in progress task): Implement fix to respect minus flag for char formatting <-
    - upcoming (not yet): Validate fix with comprehensive testing
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement the fix to make char formatting respect the minus flag for left-alignment, matching std::printf behavior.

##### Technical Specs:
  - **Code Modification**: Update char formatting logic to handle minus flag properly
  - **Alignment Logic**: Ensure char is left-aligned with right padding when minus flag present
  - **Pattern Consistency**: Follow the same alignment pattern used by integer and string formatters
  - **Minimal Changes**: Make surgical changes to avoid unintended side effects

##### Implementation Checklist:
  - [ ] Modify char formatting code to check for minus flag (left-align flag)
  - [ ] Implement left-alignment with right padding for char type (e.g., `'a'` → `"a    "` for width 5)
  - [ ] Ensure default behavior (no minus flag) remains unchanged (right-align with left padding)
  - [ ] Follow the alignment pattern from integer formatter as reference
  - [ ] Verify the fix is minimal and doesn't alter unrelated formatting behavior
  - [ ] Ensure the fix handles edge cases (width=1, width=0, etc.)

##### Success Criteria:
  - [ ] `fmt::sprintf("%-5c", 'a')` produces `"a    "` (left-aligned, right-padded)
  - [ ] `fmt::sprintf("%5c", 'a')` still produces `"    a"` (right-aligned, left-padded)
  - [ ] Implementation mirrors the alignment logic used for other types
  - [ ] Code changes are minimal and focused on the specific bug
  - [ ] No modifications to unrelated formatting logic

##### Dependencies:
  - Task #3 (root cause identification) must be completed first

##### Files to Modify:
  - The char formatting function/section identified in tasks #2 and #3 (likely in `include/fmt/printf.h` or `src/printf.cc`)

---


### 5. Validate fix with comprehensive testing (Epic: Fix sprintf minus flag bug for char formatting)

#### Description

Run the PrintfTest.MinusFlag test to verify all three test cases pass: 1) EXPECT_PRINTF('7    ', '%-5d', 7), 2) EXPECT_PRINTF('97   ', '%-5hhi', 'a'), 3) EXPECT_PRINTF('a    ', '%-5c', 'a'). Run the complete PrintfTest suite (40+ tests) to ensure no regressions in tests like NoArgs, Escape, PositionalArgs, Width, DynamicWidth, Char, etc. Test edge cases like different width values, different chars, and combination with other flags if applicable.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement fix to respect minus flag for char formatting
    - current (in progress task): Validate fix with comprehensive testing <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Validate the fix through comprehensive testing to ensure the bug is resolved and no regressions are introduced.

##### Technical Specs:
  - **Target Test**: Run `PrintfTest.MinusFlag` to verify the three specific test cases pass
  - **Regression Testing**: Run the complete PrintfTest suite (40+ tests) to ensure no existing functionality breaks
  - **Edge Case Testing**: Test additional scenarios beyond the basic test cases

##### Implementation Checklist:
  - [ ] Run `PrintfTest.MinusFlag` and verify all three cases pass:
    - `EXPECT_PRINTF("7    ", "%-5d", 7)` - Integer with minus flag
    - `EXPECT_PRINTF("97   ", "%-5hhi", 'a')` - Char as integer with minus flag
    - `EXPECT_PRINTF("a    ", "%-5c", 'a')` - Char with minus flag (the bug fix)
  - [ ] Run complete PrintfTest suite including: NoArgs, Escape, PositionalArgs, Width, DynamicWidth, Char, etc.
  - [ ] Test edge cases:
    - Different width values (%-1c, %-10c, %-100c)
    - Different characters (special chars, unicode if applicable)
    - Width smaller than character (%-0c)
    - Combinations with other flags if supported
  - [ ] Verify behavior matches std::printf for all test cases

##### Success Criteria:
  - [ ] All three PrintfTest.MinusFlag test cases pass
  - [ ] All 40+ existing PrintfTest suite tests continue to pass (zero regressions)
  - [ ] Edge cases behave correctly and match std::printf behavior
  - [ ] fmt::sprintf char formatting with minus flag now matches std::printf behavior

##### Dependencies:
  - Task #4 (fix implementation) must be completed first

##### Files to Reference:
  - `test/printf-test.cc` - Contains the test suite to run