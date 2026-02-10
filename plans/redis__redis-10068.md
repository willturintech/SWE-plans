# Plan Name: Locate Redis Bug Report and Create Fix Plan

## Tasks

### 1. Investigate XTRIM MINID implementation and identify root cause (Epic: Fix Redis XTRIM MINID bug with large ID deltas)

#### Description

Locate and analyze the XTRIM command implementation in the Redis codebase to identify the root cause of the bug.

Tasks:
1. Find XTRIM command implementation (likely in t_stream.c or stream.c)
2. Locate the MINID trimming logic and stream ID comparison functions
3. Analyze how stream entries are iterated and compared against the MINID threshold
4. Identify why large deltas between the first entry ID and subsequent IDs cause incorrect deletion behavior
5. Document the root cause (likely: incorrect ID comparison logic, off-by-one error, or issue with first/master record handling)

Deliverables:
- Clear understanding of where the bug exists in the code
- Documentation of the specific function(s) and logic that need to be fixed
- Root cause analysis explaining why the bug occurs

Context:
- Redis stream IDs format: <millisecondsTime>-<sequenceNumber>
- IDs must be monotonically increasing
- Bug specifically manifests when there's a large timestamp delta between entries

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Investigate XTRIM MINID implementation and identify root cause <-
    - upcoming (not yet): Implement fix for stream ID comparison in XTRIM MINID
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Investigate and document the root cause of the XTRIM MINID bug in the Redis codebase.

##### Technical Specs:

**Investigation Scope:**
- Locate XTRIM command implementation (likely in `t_stream.c` or `stream.c`)
- Identify MINID trimming logic and stream ID comparison functions
- Analyze stream entry iteration and ID comparison against MINID threshold
- Determine why large timestamp deltas cause incorrect deletion behavior

**Stream ID Context:**
- Format: `<millisecondsTime>-<sequenceNumber>` (e.g., "1641544570597-0")
- Must be monotonically increasing
- Bug manifests when first entry has low manual ID (e.g., "1-0") followed by auto-generated IDs with current timestamps

##### Implementation Checklist:

- [ ] Find and document the XTRIM command handler function
- [ ] Locate the MINID-specific trimming code path
- [ ] Identify all stream ID comparison functions used in trimming logic
- [ ] Trace through the stream entry iteration mechanism (likely radix tree-based)
- [ ] Analyze the ID comparison logic when processing the test scenario (1-0 → 1641544570597-0 → 1641544570597-1)
- [ ] Document the specific bug: likely incorrect comparison operator, off-by-one error, or first entry handling issue

##### Success Criteria:

- [ ] Documented location of bug in codebase (specific file, function, and line range)
- [ ] Clear explanation of why entries with IDs >= MINID are being incorrectly deleted
- [ ] Identified the specific comparison logic or condition that needs modification
- [ ] Root cause analysis explains the mechanism of failure with large timestamp deltas

##### Dependencies:

- None (this is the initial investigation task)

##### Files to Read:

- `t_stream.c` or `stream.c` (XTRIM command implementation)
- Stream-related header files for ID comparison functions
- Radix tree implementation files (if needed for understanding entry traversal)

##### Files to Document:

- Create investigation findings document listing:
  - Bug location (file, function, line numbers)
  - Current buggy logic/code snippet
  - Root cause explanation
  - Recommended fix approach

---


### 2. Fix Redis XTRIM MINID bug with large ID deltas

#### Description

Fix the bug where XTRIM MINID incorrectly deletes messages with IDs higher than the specified threshold when there's a large delta between the first message ID and subsequent auto-generated IDs. The bug causes all messages to be deleted even when their IDs are >= the MINID threshold.

Bug scenario: When a stream has an entry with a low manual ID (e.g., '1-0') followed by entries with auto-generated IDs with current timestamps (e.g., '1641544570597-0'), calling XTRIM MINID with one of the higher IDs incorrectly deletes all entries.

Success criteria:
- Test 'XTRIM with MINID option, big delta from master record' must pass
- All 7 existing XTRIM tests must continue passing

Repository: redis/redis (C codebase)
Test location: tests/unit/type/stream.tcl


### 3. Implement fix for stream ID comparison in XTRIM MINID (Epic: Fix Redis XTRIM MINID bug with large ID deltas)

#### Description

Modify the XTRIM MINID logic to correctly handle stream ID comparisons when there are large deltas between entry IDs.

Requirements:
1. Fix the ID comparison logic identified in the investigation phase
2. Ensure entries with IDs >= MINID threshold are retained (not deleted)
3. Ensure entries with IDs < MINID threshold are correctly deleted
4. Handle edge cases: large timestamp deltas, manual vs auto-generated IDs, first entry effects
5. Maintain backwards compatibility with existing XTRIM behavior

Implementation guidelines:
- Modify only the necessary comparison/trimming logic
- Preserve existing functionality for all other XTRIM modes (MAXLEN, ~, LIMIT)
- Use appropriate stream ID comparison functions
- Consider the radix tree structure used for stream storage

Deliverables:
- Modified C code with the bug fix
- Code follows Redis coding standards
- Logic correctly handles the test case scenario (1-0, 1641544570597-0, 1641544570597-1)

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Investigate XTRIM MINID implementation and identify root cause
    - current (in progress task): Implement fix for stream ID comparison in XTRIM MINID <-
    - upcoming (not yet): Add test case and verify fix with full test suite
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement the fix for XTRIM MINID stream ID comparison to correctly handle large timestamp deltas between entries.

##### Technical Specs:

**Core Fix:**
- Modify ID comparison logic in XTRIM MINID code path identified in investigation
- Ensure proper comparison: retain entries with `ID >= MINID`, delete entries with `ID < MINID`
- Handle edge cases: large timestamp deltas, manual vs auto-generated IDs, first entry effects

**Code Constraints:**
- Modify only the necessary comparison/trimming logic
- Preserve all other XTRIM functionality (MAXLEN, approximate trimming with ~, LIMIT)
- Use existing Redis stream ID comparison functions correctly
- Respect radix tree structure for stream storage
- Follow Redis C coding standards and conventions

##### Implementation Checklist:

- [ ] Implement corrected ID comparison logic (fix the specific bug identified in investigation)
- [ ] Ensure entries with IDs >= MINID threshold are retained
- [ ] Ensure entries with IDs < MINID threshold are deleted
- [ ] Handle the test scenario correctly: retain 1641544570597-0 and 1641544570597-1 when MINID is 1641544570597-0
- [ ] Verify no changes to MAXLEN, ~, or LIMIT behavior
- [ ] Add inline comments explaining the fix (especially around edge cases)
- [ ] Ensure no memory leaks or resource issues introduced

##### Success Criteria:

- [ ] Code compiles without errors or warnings
- [ ] Logic correctly processes test case: stream with IDs (1-0, 1641544570597-0, 1641544570597-1) trimmed with MINID 1641544570597-0 retains the latter two entries
- [ ] ID comparison handles both small and large timestamp values correctly
- [ ] First/master entry with low ID doesn't affect subsequent high-ID entries
- [ ] Code follows Redis style guidelines (indentation, naming, comments)

##### Dependencies:

- Completed investigation task (#2) with documented root cause and fix location

##### Files to Read:

- Investigation findings document from task #2
- Existing stream ID comparison utility functions
- Redis coding style documentation

##### Files to Modify:

- Primary file containing XTRIM MINID logic (identified in investigation, likely `t_stream.c`)
- Any related stream utility files if comparison functions need adjustment

---


### 4. Add test case and verify fix with full test suite (Epic: Fix Redis XTRIM MINID bug with large ID deltas)

#### Description

Add the new test case to the Redis test suite and verify that the fix resolves the bug without introducing regressions.

Test addition:
1. Add the test 'XTRIM with MINID option, big delta from master record' to tests/unit/type/stream.tcl
2. Test logic:
   - DEL mystream
   - XADD mystream 1-0 f v
   - XADD mystream 1641544570597-0 f v
   - XADD mystream 1641544570597-1 f v
   - XTRIM mystream MINID 1641544570597-0
   - Assert result: {{1641544570597-0 {f v}} {1641544570597-1 {f v}}}

Verification:
1. Run the new test and verify it passes
2. Run all existing XTRIM tests and verify they still pass:
   - 'XTRIM with MINID option'
   - 'XTRIM with MAXLEN option basic test'
   - 'XTRIM with ~ is limited'
   - 'XTRIM without ~ is not limited'
   - 'XTRIM without ~ and with LIMIT'
   - 'XTRIM with LIMIT delete entries no more than limit'
   - 'XTRIM with ~ MAXLEN can propagate correctly'
3. Run broader Redis stream test suite to check for any unexpected side effects

Success criteria:
- New test passes (FAIL_TO_PASS)
- All 7 existing XTRIM tests pass (PASS_TO_PASS)
- No regressions in other stream functionality

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement fix for stream ID comparison in XTRIM MINID
    - current (in progress task): Add test case and verify fix with full test suite <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add the failing test case to the Redis test suite and verify the fix resolves the bug without introducing regressions.

##### Technical Specs:

**Test Addition:**
- File: `tests/unit/type/stream.tcl`
- Test name: "XTRIM with MINID option, big delta from master record"
- Test operations:
  1. `DEL mystream`
  2. `XADD mystream 1-0 f v`
  3. `XADD mystream 1641544570597-0 f v`
  4. `XADD mystream 1641544570597-1 f v`
  5. `XTRIM mystream MINID 1641544570597-0`
  6. Verify result: `{{1641544570597-0 {f v}} {1641544570597-1 {f v}}}`

**Verification Scope:**
- New test must pass (FAIL_TO_PASS transition)
- 7 existing XTRIM tests must continue passing (PASS_TO_PASS)
- Broader stream test suite should show no regressions

##### Implementation Checklist:

- [ ] Add new test case to `tests/unit/type/stream.tcl` in appropriate location
- [ ] Use proper Tcl test syntax matching existing test format
- [ ] Include descriptive test comments explaining the large delta scenario
- [ ] Run new test in isolation to verify it passes with the fix
- [ ] Run all 7 existing XTRIM tests to confirm no regressions
- [ ] Run complete stream test suite to check for unexpected side effects
- [ ] Document any test execution issues or unexpected behavior

##### Success Criteria:

- [ ] New test "XTRIM with MINID option, big delta from master record" passes
- [ ] All existing XTRIM tests pass:
  - "XTRIM with MINID option"
  - "XTRIM with MAXLEN option basic test"
  - "XTRIM with ~ is limited"
  - "XTRIM without ~ is not limited"
  - "XTRIM without ~ and with LIMIT"
  - "XTRIM with LIMIT delete entries no more than limit"
  - "XTRIM with ~ MAXLEN can propagate correctly"
- [ ] No regressions in other stream functionality (XADD, XREAD, XRANGE, etc.)
- [ ] Test output clearly shows expected vs actual results

##### Dependencies:

- Completed fix implementation (#3) with corrected XTRIM MINID logic

##### Files to Read:

- Existing tests in `tests/unit/type/stream.tcl` for format reference
- Redis test framework documentation for Tcl test syntax

##### Files to Modify:

- `tests/unit/type/stream.tcl` (add new test case)
