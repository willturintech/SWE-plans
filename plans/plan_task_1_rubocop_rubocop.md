# Plan Name: Locate and Plan Bug Fix for RuboCop CSV Task

## Tasks

### 1. Locate and analyze current string interpolation detection logic (Epic: Fix Style/RedundantFreeze to recognize Ruby variable interpolation syntax)

#### Description

Find the code in lib/rubocop/cop/style/redundant_freeze.rb that determines whether a string contains interpolation.

Tasks:
1. Open lib/rubocop/cop/style/redundant_freeze.rb
2. Locate the method(s) that check for string interpolation (likely checking for dstr node types or regex patterns)
3. Identify how the cop currently distinguishes between:
   - Immutable strings (frozen literals like 'foo', empty strings)
   - Mutable strings (those with interpolation like "#{expr}")
   - Strings with only interpolation vs strings with text+interpolation
4. Document the current logic - look for patterns like:
   - AST node type checks (str_type?, dstr_type?)
   - Pattern matching for #{...} syntax
   - Any helper methods from RuboCop::AST that handle interpolation
5. Check if there are any existing helper methods in RuboCop for detecting interpolation that might already support variable syntax

Key files to examine:
- lib/rubocop/cop/style/redundant_freeze.rb (main cop implementation)
- Possibly lib/rubocop/cop/mixin/ modules for string utilities
- RuboCop::AST::StringNode or similar for AST helpers

Deliverables:
- Understanding of current interpolation detection mechanism
- Identification of where to add variable interpolation detection
- Knowledge of what node types represent #@, #@@, #$ in Ruby AST

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Locate and analyze current string interpolation detection logic <-
    - upcoming (not yet): Implement detection for variable interpolation syntax (#@, #@@, #$)
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate and analyze the current string interpolation detection logic in RuboCop's Style/RedundantFreeze cop to understand how it determines string mutability.

##### Technical Specs:

**Analysis Focus:**
- Examine `lib/rubocop/cop/style/redundant_freeze.rb` to find interpolation detection methods
- Identify AST node type checks (likely `str_type?`, `dstr_type?`)
- Document how the cop distinguishes between immutable literals and mutable interpolated strings
- Check for existing RuboCop::AST helper methods that may already support variable interpolation syntax

**Key Investigation Points:**
- Current logic for detecting `#{...}` interpolation syntax
- How the cop handles strings with only interpolation vs. text+interpolation
- Whether `#@variable`, `#@@variable`, `#$variable` syntax is already partially handled
- Mixin modules in `lib/rubocop/cop/mixin/` that provide string utilities

##### Implementation Checklist:

- [ ] Open and review `lib/rubocop/cop/style/redundant_freeze.rb`
- [ ] Locate method(s) that check for string interpolation
- [ ] Document current immutability detection logic (frozen literals, empty strings)
- [ ] Document current interpolation detection logic (dstr nodes, regex patterns)
- [ ] Identify how pure interpolation (`"#{a}"`) vs mixed (`"text#{a}"`) is handled
- [ ] Research RuboCop::AST::StringNode or similar AST helpers
- [ ] Determine AST node types for `#@`, `#@@`, `#$` syntax
- [ ] Check if any existing helper methods detect variable interpolation

##### Success Criteria:

- [ ] Complete understanding of current interpolation detection mechanism documented
- [ ] Identified the exact location(s) where variable interpolation detection should be added
- [ ] Confirmed AST node types that represent `#@`, `#@@`, `#$` interpolation
- [ ] Documented whether fix requires new logic or extension of existing dstr handling

##### Dependencies:

- Access to `lib/rubocop/cop/style/redundant_freeze.rb`
- Understanding of Ruby AST node types (parser gem documentation may help)

##### Files to Read:

- `lib/rubocop/cop/style/redundant_freeze.rb` (primary analysis target)
- `lib/rubocop/cop/mixin/*` (potential string utility modules)
- RuboCop::AST documentation or source for StringNode helpers

---


### 2. Fix Style/RedundantFreeze to recognize Ruby variable interpolation syntax

#### Description

Fix RuboCop's Style/RedundantFreeze cop to correctly identify strings with variable interpolation (#@instance, #@@class, #$global) as containing interpolation. The cop currently only recognizes #{...} syntax and incorrectly treats variable interpolation strings as non-interpolated.

Bug details:
- Strings like "#@qwe/#@rty" contain interpolation and are mutable, but the cop treats them as immutable
- Strings like "#@a" (only interpolation, no text) are immutable like "#{a}", but the cop doesn't recognize this
- Need to add detection for #@variable, #@@variable, and #$variable syntax

Expected outcomes:
- 3 FAIL_TO_PASS tests should pass: 'allows "#$a" with freeze', 'allows "#@@a" with freeze', 'allows "#@a" with freeze'
- All 35+ existing PASS_TO_PASS tests must continue passing
- The cop correctly identifies both mutable strings with text+interpolation and immutable strings with only interpolation


### 3. Implement detection for variable interpolation syntax (#@, #@@, #$) (Epic: Fix Style/RedundantFreeze to recognize Ruby variable interpolation syntax)

#### Description

Modify the interpolation detection logic to recognize Ruby's variable interpolation shorthand syntax.

Implementation details:
1. Understand Ruby's variable interpolation in AST:
   - "#@foo" - instance variable interpolation
   - "#@@foo" - class variable interpolation
   - "#$foo" - global variable interpolation
   - These create dstr (dynamic string) nodes in the AST, similar to #{expr}

2. Modify the interpolation detection logic:
   - The cop likely checks for dstr node types to detect interpolation
   - Ensure that dstr nodes containing variable interpolation are recognized
   - The AST structure for "#@foo" should be similar to "#{@foo}" - both create dstr nodes
   - May need to add specific checks if the current code uses regex/string matching instead of AST node analysis

3. Distinguish between:
   - Pure interpolation strings: "#@a" (immutable, just like "#{a}")
   - Mixed strings: "top#@a" (mutable, contains text + interpolation)
   - This logic should already exist for #{} syntax, extend it to cover variable syntax

4. Implementation approach (typical RuboCop pattern):
   ```ruby
   # Check if node is a dstr (dynamic string) which includes all interpolation
   def interpolated_string?(node)
     node.dstr_type?
   end
   
   # Check if string only contains interpolation, no literal text
   def only_interpolation?(node)
     return false unless node.dstr_type?
     # Check if all children are interpolation nodes, no str nodes with content
   end
   ```

5. The fix might be as simple as ensuring dstr detection is comprehensive, or may require checking for specific variable interpolation patterns

Deliverables:
- Modified interpolation detection that recognizes #@, #@@, #$ syntax
- Logic that correctly identifies pure vs mixed interpolation strings
- Code follows RuboCop's style guidelines and patterns

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate and analyze current string interpolation detection logic
    - current (in progress task): Implement detection for variable interpolation syntax (#@, #@@, #$) <-
    - upcoming (not yet): Apply test patch and add test cases
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement detection for Ruby's variable interpolation shorthand syntax (`#@`, `#@@`, `#$`) in the Style/RedundantFreeze cop's interpolation logic.

##### Technical Specs:

**Ruby Variable Interpolation Syntax:**
- `#@foo` - instance variable interpolation (creates dstr node)
- `#@@foo` - class variable interpolation (creates dstr node)
- `#$foo` - global variable interpolation (creates dstr node)

**Implementation Strategy:**
- Modify interpolation detection to recognize dstr nodes containing variable interpolation
- Extend existing logic that handles `#{...}` syntax to cover variable shorthand
- Ensure distinction between immutable pure interpolation (`"#@a"`) and mutable mixed strings (`"top#@a"`)

**Expected AST Behavior:**
- Both `"#@foo"` and `"#{@foo}"` create dstr (dynamic string) nodes
- Pure interpolation strings (only variable, no text) are immutable like `"#{a}"`
- Mixed strings (text + variable) are mutable like `"text#{a}"`

##### Implementation Checklist:

- [ ] Modify interpolation detection method to handle dstr nodes comprehensively
- [ ] Ensure variable interpolation syntax creates same detection result as `#{...}`
- [ ] Verify logic correctly identifies pure interpolation strings as immutable
- [ ] Verify logic correctly identifies mixed interpolation strings as mutable
- [ ] Test with all three variable types: `#@`, `#@@`, `#$`
- [ ] Follow RuboCop's code style guidelines
- [ ] Add inline comments explaining variable interpolation handling

##### Success Criteria:

- [ ] Code recognizes `#@variable`, `#@@variable`, `#$variable` as interpolation
- [ ] Pure interpolation strings (`"#@a"`) treated as immutable (like `"#{a}"`)
- [ ] Mixed strings (`"top#@a"`) treated as mutable (like `"text#{a}"`)
- [ ] Implementation uses AST node analysis (dstr_type?) rather than regex if possible
- [ ] Code is clean, maintainable, and follows existing patterns in the cop

##### Dependencies:

- Completion of task #2 (understanding current detection logic)
- Knowledge of where to modify interpolation detection code

##### Files to Modify:

- `lib/rubocop/cop/style/redundant_freeze.rb` (interpolation detection method)

---


### 4. Apply test patch and add test cases (Epic: Fix Style/RedundantFreeze to recognize Ruby variable interpolation syntax)

#### Description

Apply the provided test patch to spec/rubocop/cop/style/redundant_freeze_spec.rb and ensure all test cases are properly integrated.

Tasks:
1. Apply the git diff patch from the CSV file to the test file:
   - The patch adds tests for mutable objects: 'top#@foo', 'top#@@foo', 'top#$foo'
   - The patch adds tests for immutable objects: '#@a', '#@@a', '#$a'
   - The patch adds offense tests for frozen variable interpolation strings

2. Verify the test patch applies cleanly:
   - Run: git apply <patch_file>
   - Or manually add the test cases if there are conflicts

3. Review the added test cases:
   - Mutable object tests (lines 10-12): should NOT trigger offense when frozen
   - Immutable object tests (lines 20-22, 29-31, 38-40, 84-86): should NOT trigger offense when frozen
   - Offense tests (lines 108-137): SHOULD trigger offense for freezing immutable interpolated strings

4. Understand test helpers:
   - 'it_behaves_like' shared examples for common test patterns
   - 'expect_offense' for checking cop detects issues
   - 'expect_correction' for checking autocorrect behavior

5. Run the test file:
   - bundle exec rspec spec/rubocop/cop/style/redundant_freeze_spec.rb
   - Initially, the 3 FAIL_TO_PASS tests should fail
   - After implementing the fix, all tests should pass

Deliverables:
- Test patch applied to spec file
- Understanding of test structure and expectations
- Baseline test run showing which tests currently fail

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement detection for variable interpolation syntax (#@, #@@, #$)
    - current (in progress task): Apply test patch and add test cases <-
    - upcoming (not yet): Run tests and verify fix
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Apply the provided test patch to the redundant_freeze spec file and verify test structure before implementation.

##### Technical Specs:

**Test Patch Contents:**
- Mutable object tests: `'top#@foo'`, `'top#@@foo'`, `'top#$foo'` (should NOT trigger offense when frozen)
- Immutable object tests: `'#@a'`, `'#@@a'`, `'#$a'` (should NOT trigger offense when frozen)
- Offense tests: frozen variable interpolation strings (SHOULD trigger offense)

**Test Integration:**
- Apply git diff patch from CSV file to `spec/rubocop/cop/style/redundant_freeze_spec.rb`
- Understand RSpec shared examples and test helpers used
- Establish baseline: which tests currently fail before implementation

##### Implementation Checklist:

- [ ] Extract test patch from CSV file (column: test_patch)
- [ ] Apply patch using `git apply` or manually integrate if conflicts exist
- [ ] Review mutable object tests (lines 10-12 per patch)
- [ ] Review immutable object tests (lines 20-22, 29-31, 38-40, 84-86 per patch)
- [ ] Review offense tests (lines 108-137 per patch)
- [ ] Understand `it_behaves_like` shared example usage
- [ ] Understand `expect_offense` and `expect_correction` helpers
- [ ] Run initial test suite to confirm 3 FAIL_TO_PASS tests fail
- [ ] Document baseline test results

##### Success Criteria:

- [ ] Test patch successfully applied to spec file
- [ ] All new test cases properly integrated and syntactically valid
- [ ] Initial test run confirms exactly 3 failing tests (the FAIL_TO_PASS cases)
- [ ] All existing PASS_TO_PASS tests still pass before implementation
- [ ] Test structure and expectations clearly understood for validation

##### Dependencies:

- Access to CSV file at `tasks/task_1_rubocop_rubocop.csv`
- Access to `spec/rubocop/cop/style/redundant_freeze_spec.rb`

##### Files to Read:

- `tasks/task_1_rubocop_rubocop.csv` (test_patch column)

##### Files to Modify:

- `spec/rubocop/cop/style/redundant_freeze_spec.rb` (apply test patch)

---


### 5. Run tests and verify fix (Epic: Fix Style/RedundantFreeze to recognize Ruby variable interpolation syntax)

#### Description

Execute the test suite to verify that the implementation fixes the bug without breaking existing functionality.

Test execution plan:
1. Run the specific redundant_freeze tests:
   ```bash
   bundle exec rspec spec/rubocop/cop/style/redundant_freeze_spec.rb
   ```
   - Verify all 3 FAIL_TO_PASS tests now pass:
     * 'allows "#$a" with freeze'
     * 'allows "#@@a" with freeze'
     * 'allows "#@a" with freeze'
   - Verify all 35+ PASS_TO_PASS tests continue passing

2. Run the full RuboCop test suite:
   ```bash
   bundle exec rake spec
   ```
   - Ensure no regressions in other cops
   - Check for any related failures

3. Manual verification with example code:
   - Create test.rb with the examples from the bug report:
   ```ruby
   # frozen_string_literal: true
   
   s1 = "#@qwe/#@rty".freeze  # Should NOT trigger offense (mutable string)
   s2 = "#@a".freeze           # Should trigger offense (immutable string)
   s3 = "top#@@foo".freeze     # Should NOT trigger offense (mutable string)
   ```
   - Run: bundle exec rubocop test.rb
   - Verify output matches expected behavior from bug report

4. Edge case testing:
   - Empty strings: "".freeze
   - Multiple interpolations: "#@a#@b".freeze
   - Mixed interpolation types: "#{x}#@y".freeze
   - Escaped interpolation: "\#@foo".freeze (should not be treated as interpolation)

5. Review autocorrect behavior:
   - The cop should only autocorrect truly redundant freeze calls
   - Should not autocorrect mutable strings

Deliverables:
- All tests passing
- Manual verification results documented
- Confirmation that edge cases are handled correctly
- No regressions in existing functionality

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply test patch and add test cases
    - current (in progress task): Run tests and verify fix <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Execute comprehensive test verification to confirm the implementation fixes the bug without introducing regressions.

##### Technical Specs:

**Test Execution Levels:**
1. Specific cop tests (redundant_freeze_spec.rb)
2. Full RuboCop test suite (all cops)
3. Manual verification with bug report examples
4. Edge case validation

**Expected Behavior:**
- 3 FAIL_TO_PASS tests must now pass
- All 35+ PASS_TO_PASS tests must continue passing
- Manual examples match expected behavior from bug report
- Autocorrect only applies to truly redundant freeze calls

##### Implementation Checklist:

- [ ] Run `bundle exec rspec spec/rubocop/cop/style/redundant_freeze_spec.rb`
- [ ] Verify 3 FAIL_TO_PASS tests pass: `allows "#$a" with freeze`, `allows "#@@a" with freeze`, `allows "#@a" with freeze`
- [ ] Verify all 35+ PASS_TO_PASS tests continue passing
- [ ] Run full test suite: `bundle exec rake spec`
- [ ] Check for regressions in other cops
- [ ] Create `test.rb` with bug report examples
- [ ] Run `bundle exec rubocop test.rb` and verify output
- [ ] Test edge cases: empty strings, multiple interpolations, mixed types, escaped syntax
- [ ] Verify autocorrect behavior is correct (only for truly immutable strings)

##### Success Criteria:

- [ ] All redundant_freeze_spec.rb tests pass (100% pass rate)
- [ ] Full RuboCop test suite passes with no new failures
- [ ] Manual test.rb verification matches expected behavior:
  - `"#@qwe/#@rty".freeze` - NO offense (mutable)
  - `"#@a".freeze` - registers offense (immutable)
  - `"top#@@foo".freeze` - NO offense (mutable)
- [ ] Edge cases handled correctly (escaped interpolation not treated as interpolation)
- [ ] Autocorrect only removes freeze from immutable pure interpolation strings
- [ ] No regressions in unrelated functionality

##### Dependencies:

- Completion of task #3 (implementation)
- Completion of task #4 (test patch applied)
- RuboCop development environment set up

##### Files to Read:

- Bug report examples in CSV for manual verification
