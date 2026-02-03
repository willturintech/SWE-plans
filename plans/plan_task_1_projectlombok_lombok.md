# Plan Name: Locate CSV File and Create Bug Fix Plan for Project Lombok

## Tasks

### 1. Analyze current HandleVal.java implementation in javac handlers (Epic: Fix val keyword type inference for lambda parameters in javac/delombok)

#### Description

Investigate the current implementation of src/core/lombok/javac/handlers/HandleVal.java to understand:
- How type inference currently works for val keyword
- Where the type resolution logic is implemented
- How it handles different expression types (assignments, method calls, etc.)
- Identify where it fails for lambda expressions
- Document the current flow: when HandleVal is triggered, how it extracts types from initializer expressions

Key focus: Understand the type attribution process and identify why 'does not have a representable type' error occurs for lambda expressions with casts.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Analyze current HandleVal.java implementation in javac handlers <-
    - upcoming (not yet): Compare Eclipse and javac HandleVal implementations
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Investigate how `HandleVal.java` currently performs type inference to identify why it fails for lambda expressions with casts.

##### Technical Specs:
- **Analysis Target**: `src/core/lombok/javac/handlers/HandleVal.java`
- **Focus Areas**:
  - Type inference mechanism for `val` keyword
  - Type resolution logic and its entry points
  - Expression type handling (assignments, method calls, literals, etc.)
  - Type attribution process timing and dependencies
  - Error path that produces "does not have a representable type"

##### Implementation Checklist:
- [ ] Document how HandleVal is triggered in the javac compilation phase
- [ ] Trace the flow from `val` keyword detection to type extraction from initializer
- [ ] Identify which javac AST node types are currently handled
- [ ] Locate where type resolution fails for lambda expressions
- [ ] Document the type attribution process and its relationship to HandleVal
- [ ] Identify specific code paths that handle (or fail to handle) JCTypeCast nodes
- [ ] Note any assumptions made about expression types being fully resolved

##### Success Criteria:
- [ ] Clear understanding of when and how HandleVal extracts types from initializers
- [ ] Identification of the specific failure point for lambda + cast expressions
- [ ] Documentation of current AST node handling capabilities
- [ ] Understanding of type attribution requirements before type inference

##### Dependencies:
- Access to `src/core/lombok/javac/handlers/HandleVal.java`
- Familiarity with javac AST structure (JCTree nodes)

##### Files to read:
- `src/core/lombok/javac/handlers/HandleVal.java`
- Related javac type resolution utilities in the same package

---


### 2. Fix val keyword type inference for lambda parameters in javac/delombok

#### Description

Fix the bug where Lombok's val keyword fails when used with lambda parameters in javac/delombok, causing error: 'Cannot use val here because initializer expression does not have a representable type'. The Eclipse plugin already handles this correctly, so javac/delombok needs to be updated to match that behavior.

Key test case:
```java
val foo = (Function<Supplier<String>, String>) s -> s.get();
```

This should be transformed to:
```java
final java.util.function.Function<java.util.function.Supplier<java.lang.String>, java.lang.String> foo = (Function<Supplier<String>, String>) s -> s.get();
```


### 3. Compare Eclipse and javac HandleVal implementations (Epic: Fix val keyword type inference for lambda parameters in javac/delombok)

#### Description

Compare src/core/lombok/eclipse/handlers/HandleVal.java (working) with src/core/lombok/javac/handlers/HandleVal.java (broken) to identify:
- How Eclipse successfully handles lambda type inference
- Differences in AST representation between Eclipse JDT and javac
- How Eclipse extracts type information from cast expressions
- Any Eclipse-specific APIs or techniques that solve this problem

Document the key differences that allow Eclipse to succeed where javac fails. This will inform the implementation strategy for the javac fix.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Analyze current HandleVal.java implementation in javac handlers
    - current (in progress task): Compare Eclipse and javac HandleVal implementations <-
    - upcoming (not yet): Implement type resolution for cast expressions containing lambdas
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Compare the working Eclipse implementation with the broken javac implementation to understand how Eclipse successfully resolves types for lambda expressions with casts.

##### Technical Specs:
- **Comparison Files**:
  - `src/core/lombok/eclipse/handlers/HandleVal.java` (working reference)
  - `src/core/lombok/javac/handlers/HandleVal.java` (broken implementation)
- **Analysis Focus**:
  - Lambda type inference approaches in each compiler
  - AST representation differences for cast expressions and lambdas
  - Cast expression type extraction mechanisms
  - Eclipse JDT vs javac API differences

##### Implementation Checklist:
- [ ] Compare overall structure and approach between implementations
- [ ] Identify how Eclipse handles JCTypeCast equivalent nodes
- [ ] Document Eclipse's lambda type resolution strategy
- [ ] Note AST representation differences for the test case: `(Function<Supplier<String>, String>) s -> s.get()`
- [ ] Identify Eclipse-specific APIs used for type extraction
- [ ] Document key algorithmic differences that enable Eclipse success
- [ ] Extract portable patterns that can be adapted to javac

##### Success Criteria:
- [ ] Clear documentation of why Eclipse succeeds where javac fails
- [ ] Identification of specific techniques Eclipse uses for cast + lambda handling
- [ ] Understanding of whether differences are compiler-specific or implementation choices
- [ ] Actionable insights that inform the javac fix strategy

##### Dependencies:
- Completion of task #2 (understanding current javac implementation)
- Access to both Eclipse and javac handler implementations

##### Files to read:
- `src/core/lombok/eclipse/handlers/HandleVal.java`
- `src/core/lombok/javac/handlers/HandleVal.java`

---


### 4. Implement type resolution for cast expressions containing lambdas (Epic: Fix val keyword type inference for lambda parameters in javac/delombok)

#### Description

Modify src/core/lombok/javac/handlers/HandleVal.java to properly handle type inference when the initializer is a cast expression containing a lambda:

1. Detect when the initializer expression is a JCTypeCast
2. When a cast is present, extract the target type from the cast expression
3. Use the cast type as the inferred type for the val variable
4. Ensure type attribution is complete before attempting type inference
5. Handle nested lambda contexts (val used inside lambda body)

Implementation should handle:
- `(FunctionalInterface<T>) lambda` patterns
- Generic type parameters in functional interfaces
- Nested lambda expressions
- Edge cases where cast might not provide complete type information

The fix should make javac behavior consistent with Eclipse plugin.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Compare Eclipse and javac HandleVal implementations
    - current (in progress task): Implement type resolution for cast expressions containing lambdas <-
    - upcoming (not yet): Add inParameter() test method to ValInLambda test files
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Modify the javac HandleVal implementation to properly resolve types when `val` is used with cast expressions containing lambdas, making javac behavior consistent with the Eclipse plugin.

##### Technical Specs:
- **Target File**: `src/core/lombok/javac/handlers/HandleVal.java`
- **Core Changes**:
  - Add JCTypeCast detection logic
  - Extract target type from cast expressions
  - Use cast type as inferred type when lambda is the expression
  - Ensure type attribution completion before inference
  - Support nested lambda contexts

##### Implementation Checklist:
- [ ] Add logic to detect when initializer is a JCTypeCast node
- [ ] Extract the target type from cast expressions (e.g., `Function<Supplier<String>, String>`)
- [ ] Implement fallback: use cast type when direct lambda inference fails
- [ ] Verify type attribution is complete before attempting inference
- [ ] Handle generic type parameters in functional interfaces correctly
- [ ] Support nested lambda scenarios (val inside lambda body)
- [ ] Add appropriate error handling for edge cases
- [ ] Preserve existing behavior for non-lambda val declarations

##### Success Criteria:
- [ ] Test case `val foo = (Function<Supplier<String>, String>) s -> s.get();` compiles successfully
- [ ] Delombok produces correct output with explicit types and final modifier
- [ ] Nested lambda contexts work: `val` inside lambda bodies resolves correctly
- [ ] Generic type parameters are preserved correctly
- [ ] No regressions in existing val functionality
- [ ] Error messages remain clear when type resolution genuinely fails

##### Dependencies:
- Completion of task #2 (understanding current implementation)
- Completion of task #3 (understanding Eclipse's approach)

##### Files to modify:
- `src/core/lombok/javac/handlers/HandleVal.java`

---


### 5. Add inParameter() test method to ValInLambda test files (Epic: Fix val keyword type inference for lambda parameters in javac/delombok)

#### Description

Update the test resource files to include the new test method that validates val works with lambda parameters:

1. Add to test/transform/resource/before/ValInLambda.java:
```java
import java.util.function.Function;
import java.util.function.Supplier;

public void inParameter() {
    val foo = (Function<Supplier<String>, String>) s -> s.get();
    val foo2 = foo.apply(() -> {
        val bar = "";
        return bar;
    });
}
```

2. Add expected delombok output to test/transform/resource/after-delombok/ValInLambda.java with explicit types
3. Add expected ECJ output to test/transform/resource/after-ecj/ValInLambda.java

Ensure the test demonstrates both:
- val with cast lambda expression
- val used inside nested lambda body

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement type resolution for cast expressions containing lambdas
    - current (in progress task): Add inParameter() test method to ValInLambda test files <-
    - upcoming (not yet): Verify javac-ValInLambda.java test passes
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add the `inParameter()` test method to ValInLambda test resource files to validate that `val` works correctly with lambda parameters and nested lambda contexts.

##### Technical Specs:
- **Test Files to Update**:
  - `test/transform/resource/before/ValInLambda.java` (source with val)
  - `test/transform/resource/after-delombok/ValInLambda.java` (expected delombok output)
  - `test/transform/resource/after-ecj/ValInLambda.java` (expected ECJ output)
- **Test Coverage**:
  - val with cast to functional interface: `(Function<Supplier<String>, String>)`
  - Lambda expression as initializer
  - val used inside nested lambda body

##### Implementation Checklist:
- [ ] Add `inParameter()` method to before/ValInLambda.java with required imports
- [ ] Include test case: `val foo = (Function<Supplier<String>, String>) s -> s.get();`
- [ ] Include nested lambda test: `val foo2 = foo.apply(() -> { val bar = ""; return bar; });`
- [ ] Add expected delombok output with fully qualified types and final modifiers
- [ ] Add expected ECJ output matching delombok format
- [ ] Ensure proper imports for java.util.function.Function and Supplier
- [ ] Verify test method signature matches existing test structure

##### Success Criteria:
- [ ] All three test files contain the `inParameter()` method
- [ ] Expected outputs show correct type inference:
  - `final java.util.function.Function<java.util.function.Supplier<java.lang.String>, java.lang.String> foo`
  - `final java.lang.String foo2`
  - `final java.lang.String bar`
- [ ] Test demonstrates both primary and nested lambda val usage
- [ ] Files are properly formatted and consistent with existing test structure

##### Dependencies:
- None (can be done independently, though logically follows analysis tasks)

##### Files to modify:
- `test/transform/resource/before/ValInLambda.java`
- `test/transform/resource/after-delombok/ValInLambda.java`
- `test/transform/resource/after-ecj/ValInLambda.java`


### 6. Verify javac-ValInLambda.java test passes (Epic: Fix val keyword type inference for lambda parameters in javac/delombok)

#### Description

Run the FAIL_TO_PASS test to verify the fix works:

Execute: javac-ValInLambda.java(lombok.transform.TestWithDelombok)

This test should now pass after the implementation changes. Verify:
- The test compiles successfully without 'does not have a representable type' errors
- The delombok output matches expected types
- All val declarations in the test are correctly transformed to explicit types with final modifier
- Nested lambda contexts are handled correctly

If the test fails, debug the type resolution logic and adjust the implementation.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add inParameter() test method to ValInLambda test files
    - current (in progress task): Verify javac-ValInLambda.java test passes <-
    - upcoming (not yet): Run regression tests to ensure existing functionality unchanged
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify that the javac ValInLambda test now passes after implementing the type resolution fix for lambda expressions with cast operations.

##### Technical Specs:
- **Testing Framework**: Execute `javac-ValInLambda.java(lombok.transform.TestWithDelombok)` from the FAIL_TO_PASS test suite
- **Test Location**: `test/transform/resource/before/ValInLambda.java` and corresponding after files
- **Validation**: Confirm compilation succeeds without type resolution errors, delombok output matches expected transformations

##### Implementation Checklist:
- [ ] Run the specific test: `javac-ValInLambda.java(lombok.transform.TestWithDelombok)`
- [ ] Verify no "Cannot use 'val' here because initializer expression does not have a representable type" errors occur
- [ ] Confirm the `inParameter()` test method compiles successfully
- [ ] Validate delombok output in `test/transform/resource/after-delombok/ValInLambda.java` matches expected fully-qualified types
- [ ] Verify ECJ output in `test/transform/resource/after-ecj/ValInLambda.java` is correct
- [ ] Check that all `val` declarations are transformed to `final` with explicit types
- [ ] Confirm nested lambda contexts (val inside lambda body) work correctly
- [ ] If test fails, capture error messages and stack traces for debugging

##### Success Criteria:
- [ ] `javac-ValInLambda.java(lombok.transform.TestWithDelombok)` test passes completely
- [ ] `val foo = (Function<Supplier<String>, String>) s -> s.get();` transforms to `final java.util.function.Function<...> foo = ...`
- [ ] `val bar = "";` inside nested lambda transforms correctly to `final java.lang.String bar = "";`
- [ ] No compilation errors related to type resolution
- [ ] Delombok output matches expected transformations exactly

##### Dependencies:
- Task #4 (Implement type resolution for cast expressions containing lambdas) must be completed

##### Files to Read:
- `test/transform/resource/before/ValInLambda.java` - Test input
- `test/transform/resource/after-delombok/ValInLambda.java` - Expected delombok output
- `test/transform/resource/after-ecj/ValInLambda.java` - Expected ECJ output

---


### 7. Run regression tests to ensure existing functionality unchanged (Epic: Fix val keyword type inference for lambda parameters in javac/delombok)

#### Description

Execute the PASS_TO_PASS test suite to ensure the fix doesn't break existing Lombok functionality:

Run all lombok.transform.TestWithDelombok tests including:
- Builder tests (BuilderSimple, BuilderComplex, BuilderDefaults, etc.)
- Accessor tests (Accessors, AccessorsConfiguration)
- Other Val tests
- All other javac transform tests

Verify that all previously passing tests still pass. If any regressions are found:
- Identify which test failed
- Determine if the fix introduced the regression
- Adjust the implementation to handle both the new lambda case and existing cases
- Ensure the fix is scoped narrowly to lambda/cast expressions without affecting other val use cases

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Verify javac-ValInLambda.java test passes
    - current (in progress task): Run regression tests to ensure existing functionality unchanged <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Execute the full PASS_TO_PASS regression test suite to ensure the val lambda fix doesn't break any existing Lombok functionality across all javac transform tests.

##### Technical Specs:
- **Test Suite**: `lombok.transform.TestWithDelombok` - all tests except the FAIL_TO_PASS case
- **Scope**: All existing passing tests including Builder, Accessor, Val, and other Lombok features
- **Focus Areas**: Ensure HandleVal.java changes only affect lambda/cast scenarios without impacting standard val usage

##### Implementation Checklist:
- [ ] Run complete `lombok.transform.TestWithDelombok` test suite
- [ ] Verify all Builder tests pass (BuilderSimple, BuilderComplex, BuilderDefaults, etc.)
- [ ] Verify all Accessor tests pass (Accessors, AccessorsConfiguration)
- [ ] Verify existing Val tests continue to pass (non-lambda scenarios)
- [ ] Verify all other javac transform tests pass
- [ ] Document any test failures with specific test names and error messages
- [ ] For each regression found, determine root cause
- [ ] Verify fix is scoped to cast expressions with lambdas only
- [ ] Ensure HandleVal.java changes don't alter behavior for standard variable initialization

##### Success Criteria:
- [ ] All previously passing tests in PASS_TO_PASS remain passing
- [ ] Zero regressions introduced by the lambda/cast type resolution fix
- [ ] Standard val usage (non-lambda) continues to work identically
- [ ] No performance degradation in test execution time
- [ ] If regressions found, implementation adjusted to handle both old and new cases

##### Dependencies:
- Task #4 (Implement type resolution for cast expressions containing lambdas) must be completed
- Task #6 (Verify javac-ValInLambda.java test passes) should be validated first

##### Files to Modify (if regressions found):
- `src/core/lombok/javac/handlers/HandleVal.java` - Narrow the scope or add guards to prevent affecting non-lambda cases
