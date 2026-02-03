# Plan Name: Locate and Analyze Preact Bug Report CSV

## Tasks

### 1. Add test case for progress value=0 to render.test.js (Epic: Fix progress element value=0 attribute removal bug)

#### Description

Add the failing test case to test/browser/render.test.js around line 758. The test should verify that when rendering <progress value={0} max="100" />, both the DOM element's value property equals 0 and the value attribute equals '0'. Test code:

```javascript
// #2756
it('should set progress value to 0', () => {
    render(<progress value={0} max="100" />, scratch);
    expect(scratch.firstChild.value).to.equal(0);
    expect(scratch.firstChild.getAttribute('value')).to.equal('0');
});
```

This test should initially fail, demonstrating the bug. Success criteria: Test is added and fails before the fix is implemented.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Add test case for progress value=0 to render.test.js <-
    - upcoming (not yet): Locate attribute handling code in Preact's diff logic
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add a test case to verify that progress elements correctly handle `value={0}`. This test will initially fail, confirming the bug exists.

##### Technical Specs:
- **Test Location**: `test/browser/render.test.js` around line 758
- **Test Structure**: Standard Mocha/Chai test using the existing `render()` helper and `scratch` element
- **Verification Points**: 
  - DOM property `value` should equal the number `0`
  - DOM attribute `value` should equal the string `'0'`

##### Implementation Checklist:
- [ ] Add the test case to `test/browser/render.test.js` at approximately line 758
- [ ] Use the exact test code provided (references issue #2756)
- [ ] Verify the test is within the `render()` describe block
- [ ] Run the test to confirm it fails before any fixes are applied

##### Success Criteria:
- [ ] Test is added to the correct file and location
- [ ] Test follows existing test patterns in the file
- [ ] **Test fails initially**, demonstrating the bug (DOM attribute check fails because Preact removes the attribute)
- [ ] Test code matches the specification exactly

##### Files to Modify:
- `test/browser/render.test.js` - Add test case around line 758

---


### 2. Fix progress element value=0 attribute removal bug

#### Description

Fix the bug where Preact removes the value attribute from progress elements when set to 0, causing cross-browser styling inconsistencies. The issue is that when rendering <progress value={0} max="100" />, Preact removes the value attribute from the DOM instead of setting it to '0'. This causes Firefox to treat ::-moz-progress-bar as 100% and WebKit to treat ::-webkit-progress-value as 0%. The root cause is likely in the attribute/property handling logic where 0 is treated as a falsy value and removed, rather than being recognized as a valid numeric value.


### 3. Locate attribute handling code in Preact's diff logic (Epic: Fix progress element value=0 attribute removal bug)

#### Description

Locate the code responsible for setting DOM attributes and properties in Preact. This is likely in src/diff/props.js or a similar file in the src/diff/ directory. Look for logic that:
1. Handles attribute vs property setting for DOM elements
2. Contains conditional logic for when to set vs remove attributes
3. May use falsy checks (if (value) or value || default) that treat 0 as false
4. Handles special cases for form elements and their attributes

Document the specific file(s) and function(s) that need modification. Pay attention to how numeric attributes (value, min, max, step) are currently handled. Success criteria: Identified the exact location where the bug occurs and understand the current logic flow.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add test case for progress value=0 to render.test.js
    - current (in progress task): Locate attribute handling code in Preact's diff logic <-
    - upcoming (not yet): Fix falsy value handling for numeric attributes
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate the code in Preact's diff logic where DOM attributes and properties are set. This investigation will identify where the bug occurs so the next ticket can fix it.

##### Technical Specs:
- **Primary Search Location**: `src/diff/props.js` or similar files in `src/diff/`
- **Code Patterns to Find**:
  - Attribute vs property setting logic for DOM elements
  - Conditional checks for when to set/remove attributes
  - Falsy value checks like `if (value)`, `value || default`, or `!value`
  - Special handling for form elements (progress, input, textarea, meter)
  - Numeric attribute handling (value, min, max, step)

##### Implementation Checklist:
- [ ] Explore `src/diff/` directory to locate property/attribute handling
- [ ] Identify the specific function(s) responsible for setting DOM properties/attributes
- [ ] Find conditional logic that determines whether to set or remove attributes
- [ ] Look for falsy checks that would incorrectly treat `0` as "no value"
- [ ] Document how numeric attributes are currently processed
- [ ] Note any special cases for form elements

##### Success Criteria:
- [ ] Identified the exact file(s) containing the bug
- [ ] Identified the specific function(s) that need modification
- [ ] Documented the current logic flow for attribute/property setting
- [ ] Identified where falsy checks are treating `0` incorrectly
- [ ] Understanding of why both property AND attribute need to be set for progress elements

##### Files to Read:
- `src/diff/props.js` (or equivalent property handling file)
- Other files in `src/diff/` directory as needed
- Any utility files that handle attribute/property setting

---


### 4. Fix falsy value handling for numeric attributes (Epic: Fix progress element value=0 attribute removal bug)

#### Description

Modify the attribute handling logic to properly treat 0 as a valid value for numeric attributes. The fix should:

1. Change falsy checks from `if (value)` or `value || default` to `if (value != null)` or similar that distinguishes between 0 and null/undefined
2. Apply this fix specifically to numeric attributes: value, min, max, step
3. Ensure both the DOM property AND the attribute are set correctly (progress elements require both)
4. Consider if this affects other elements like <input>, <meter>, <textarea> with numeric values

The key is to check for null/undefined explicitly rather than using falsy checks, so that 0 is preserved as a valid numeric value. Success criteria: The code no longer removes attributes when their value is 0, and treats 0 as a valid numeric value.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate attribute handling code in Preact's diff logic
    - current (in progress task): Fix falsy value handling for numeric attributes <-
    - upcoming (not yet): Run tests and verify no regressions
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Fix the attribute handling logic to treat `0` as a valid numeric value rather than removing it. This requires changing falsy checks to explicit null/undefined checks.

##### Technical Specs:
- **Target Logic**: Attribute/property setting code identified in ticket #3
- **Core Change**: Replace falsy checks with null/undefined checks
  - **Before**: `if (value)` or `value || default` (treats 0 as falsy)
  - **After**: `if (value != null)` or `value !== undefined` (preserves 0)
- **Scope**: Numeric attributes on form elements (value, min, max, step)
- **Dual Setting**: Ensure both DOM property AND attribute are set (required for progress elements)

##### Implementation Checklist:
- [ ] Modify falsy checks to use `!= null` or `!== undefined` comparisons
- [ ] Apply fix to numeric attributes: value, min, max, step
- [ ] Ensure the fix sets both the DOM property and the HTML attribute
- [ ] Verify the fix handles edge cases:
  - `value={0}` → sets property to 0 and attribute to "0"
  - `value={null}` → removes/doesn't set the attribute
  - `value={undefined}` → removes/doesn't set the attribute
  - `value=""` → handles empty string appropriately
- [ ] Consider impact on other form elements: input, meter, textarea, select
- [ ] Preserve existing behavior for non-numeric attributes

##### Success Criteria:
- [ ] Code no longer removes attributes when value is `0`
- [ ] Both DOM property and HTML attribute are set correctly for numeric values
- [ ] `0` is treated as a valid numeric value, not as falsy/empty
- [ ] `null` and `undefined` still remove/skip setting the attribute
- [ ] No changes to behavior for non-numeric attributes
- [ ] Fix applies consistently across progress, input, meter, and textarea elements

##### Dependencies:
- Ticket #3 must be completed (location of bug identified)

##### Files to Modify:
- Files identified in ticket #3 (likely `src/diff/props.js` or equivalent)

---


### 5. Run tests and verify no regressions (Epic: Fix progress element value=0 attribute removal bug)

#### Description

Execute the test suite to verify the fix:

1. **FAIL_TO_PASS verification**: Run the test 'render() > should set progress value to 0' and confirm it now passes
2. **Regression testing**: Run all existing render() tests to ensure no regressions were introduced. Pay special attention to:
   - Tests involving falsy values (null, undefined, false)
   - Tests for form elements (input, textarea, select)
   - Tests for attribute vs property handling
   - Tests for other numeric attributes

3. If any tests fail, analyze whether they indicate a problem with the fix or if they were incorrectly passing before
4. Document any edge cases discovered during testing

Success criteria: The target test passes and all existing render() tests continue to pass without regressions.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Fix falsy value handling for numeric attributes
    - current (in progress task): Run tests and verify no regressions <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify that the fix resolves the bug without introducing regressions by running the test suite and confirming both the new test and all existing tests pass.

##### Technical Specs:
- **Test Command**: Use Preact's existing test runner (likely `npm test` or similar)
- **Primary Verification**: Confirm test `'render() > should set progress value to 0'` now passes (FAIL_TO_PASS)
- **Regression Testing**: Run all render() tests to ensure no existing functionality broke
- **Focus Areas**:
  - Falsy value tests (null, undefined, false, 0, "")
  - Form element tests (input, textarea, select, meter, progress)
  - Attribute vs property handling tests
  - Numeric attribute tests (value, min, max, step)

##### Implementation Checklist:
- [ ] Run the specific test: `'render() > should set progress value to 0'`
- [ ] Verify the test passes (both assertions succeed)
- [ ] Run all render() tests in the test suite
- [ ] Review any test failures to determine if they indicate:
  - A problem with the fix (needs adjustment)
  - Tests were incorrectly passing before (document as edge case)
- [ ] Pay special attention to tests involving:
  - Falsy values being set as attributes/properties
  - Form elements with numeric attributes
  - Attribute removal behavior
- [ ] Document any discovered edge cases or unexpected behaviors

##### Success Criteria:
- [ ] **FAIL_TO_PASS**: Test `'render() > should set progress value to 0'` now passes
- [ ] **PASS_TO_PASS**: All existing render() tests continue to pass
- [ ] No regressions in attribute/property handling
- [ ] No regressions in form element behavior
- [ ] No regressions in falsy value handling (except for numeric 0, which should now work)
- [ ] Any edge cases or unexpected behaviors are documented

##### Dependencies:
- Ticket #4 must be completed (fix implemented)

##### Files to Read:
- Test output/results
- `test/browser/render.test.js` (to understand context of any failures)
