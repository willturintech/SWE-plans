# Plan Name: Analyze and Plan Bug Fix from Project Lombok CSV

## Tasks

### 1. Locate FieldDefaults Handler (Epic: Explore Codebase)

#### Description

Search for `HandleFieldDefaults` classes (likely in `src/core/lombok/core/handlers` or similar) and `FieldDefaults` annotation definition.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Locate FieldDefaults Handler <-
    - upcoming (not yet): Investigate Record Detection
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate the code responsible for handling `FieldDefaults` in Lombok.

##### Objectives
- Identify the handler classes for `FieldDefaults`. Lombok typically has separate handlers for Eclipse and Javac (e.g., `HandleFieldDefaults.java`).
- Locate the definition of the `FieldDefaults` annotation to understand its properties.

##### Implementation Checklist
- [ ] Search for `HandleFieldDefaults` in `src/core/lombok/javac/handlers` and `src/core/lombok/eclipse/handlers`.
- [ ] Search for `FieldDefaults.java` definition.
- [ ] Note down the file paths for the handlers as they will be modified later.


### 2. Verify Fix (Epic: Fix Lombok FieldDefaults on Records)

#### Description

Run tests to ensure the fix works and doesn't break regressions.


### 3. Reproduce Bug (Epic: Fix Lombok FieldDefaults on Records)

#### Description

Create a reproduction test case to confirm the bug. The context mentions `test/transform/resource/before/FieldDefaultsViaConfigOnRecord.java`. Verify this test fails.


### 4. Implement Fix (Epic: Fix Lombok FieldDefaults on Records)

#### Description

Implement the fix in the `FieldDefaults` handler to exclude or handle `record` types correctly.


### 5. Explore Codebase (Epic: Fix Lombok FieldDefaults on Records)

#### Description

Explore the codebase to identify the relevant files for `FieldDefaults` handling and how Lombok detects `records`.


### 6. Fix Lombok FieldDefaults on Records

#### Description

Locate task_2_projectlombok_lombok.csv and create a plan to fix the bug described inside.


### 7. Investigate Record Detection (Epic: Explore Codebase)

#### Description

Investigate how Lombok detects `record` types. Look for utility methods like `isRecord` in `JavacNode`, `EclipseNode`, or `LombokProcessor`.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate FieldDefaults Handler
    - current (in progress task): Investigate Record Detection <-
    - upcoming (not yet): Create Test Case
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Investigate how Lombok detects Java `record` types in its AST wrappers.

##### Objectives
- Determine if `JavacNode` or `EclipseNode` (or their underlying AST types) expose a method like `isRecord()`.
- If not directly on the node, look for utility classes in `lombok.core`, `lombok.javac`, or `lombok.eclipse` that provide this check.

##### Implementation Checklist
- [ ] Search for usages of `record` string or `isRecord` methods in the codebase.
- [ ] specific focus on `JavacNode.java` and `EclipseNode.java` or related AST helpers.
- [ ] Document the method or field used to identify a record.


### 8. Create Test Case (Epic: Reproduce Bug)

#### Description

Extract the test case `test/transform/resource/before/FieldDefaultsViaConfigOnRecord.java` and expected output from `task_2_projectlombok_lombok.csv` or create it based on requirements.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Investigate Record Detection
    - current (in progress task): Create Test Case <-
    - upcoming (not yet): Verify Failure
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Create the reproduction test case to confirm the bug where `FieldDefaults` incorrectly processes records.

##### Objectives
- Extract the test case content from `tasks/task_2_projectlombok_lombok.csv`.
- Create the source file `test/transform/resource/before/FieldDefaultsViaConfigOnRecord.java`.
- Create the expected output files (likely `after-delombok` and `after-ecj`) if provided in the CSV, or infer that they should exist to run the comparison test.

##### Technical Specs
- The issue is that `lombok.config` settings for `FieldDefaults` (like `defaultPrivate = true`) might be applied to `record` components, which causes issues or invalid code generation.
- The test file should demonstrate a `record` being affected by these settings.

##### Implementation Checklist
- [ ] Read `tasks/task_2_projectlombok_lombok.csv` to find the test code.
- [ ] Create `test/transform/resource/before/FieldDefaultsViaConfigOnRecord.java`.
- [ ] Create corresponding expected files in `test/transform/resource/after-delombok/` and `test/transform/resource/after-ecj/` if data is available.


### 9. Verify Failure (Epic: Reproduce Bug)

#### Description

Run the test using Lombok's test infrastructure (e.g., `ant test` or specific test runner) and verify it fails due to incorrect transformation of the record.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Create Test Case
    - current (in progress task): Verify Failure <-
    - upcoming (not yet): Add Record Check
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify that the newly created test case fails, confirming the bug.

##### Objectives
- Run the Lombok test suite.
- Ensure that `FieldDefaultsViaConfigOnRecord.java` fails compilation or comparison against expected output (due to the bug not being fixed yet).

##### Implementation Checklist
- [ ] Run tests using `ant test` (standard for Lombok) or identify the specific JUnit test runner for transformation tests (e.g., a class typically named `TransformTests` or similar in `test/transform`).
- [ ] Confirm the test fails.
- [ ] Capture the failure message to understand exactly how the transformation is incorrect (e.g., fields made private when they shouldn't be, or syntax errors).


### 10. Add Record Check (Epic: Implement Fix)

#### Description

Modify `HandleFieldDefaults` (or relevant handler) to check if the node is a `record`.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Verify Failure
    - current (in progress task): Add Record Check <-
    - upcoming (not yet): Skip Logic for Records
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

This task focuses on preparing the `FieldDefaults` handler to be aware of Java `record` types. You need to modify the handler(s) to detect if the class being processed is a record.

##### Technical Specs
- **Target Files**: Locate `HandleFieldDefaults.java` (or similar) in both:
  - `src/core/lombok/javac/handlers/`
  - `src/core/lombok/eclipse/handlers/`
- **Detection Logic**:
  - **Eclipse**: Inspect the `EclipseNode` or underlying `TypeDeclaration` to check if it is a record.
  - **Javac**: Inspect the `JavacNode` or underlying `JCClassDecl` to check if it represents a record.

##### Implementation Checklist
- [ ] Locate the `FieldDefaults` handler for Eclipse.
- [ ] In the main handling method (e.g., `handle`), retrieve the type declaration and create a boolean flag (e.g., `isRecord`) indicating if the node is a record.
- [ ] Locate the `FieldDefaults` handler for Javac.
- [ ] Similarly, implement the `isRecord` detection logic.

##### Success Criteria
- [ ] The handlers can successfully identify if a type is a record.
- [ ] Verification: You may add temporary logging or rely on the subsequent task to verify this works when the logic is applied.


### 11. Skip Logic for Records (Epic: Implement Fix)

#### Description

If the node is a record, prevent `defaultPrivate` and `makeFinal` logic from modifying the fields, or ensure they are handled in a way that respects record semantics (already private final).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add Record Check
    - current (in progress task): Skip Logic for Records <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

This task focuses on applying the logic to skip `FieldDefaults` modifications for records, utilizing the detection logic established or planned in the previous step.

##### Technical Specs
- **Goal**: Prevent `lombok.fieldDefaults.defaultPrivate` and `makeFinal` from altering record components/fields, as records imply specific immutability and visibility semantics that shouldn't be overridden by this configuration.
- **Scope**: Modifying the same files identified in the previous task (`HandleFieldDefaults` for Eclipse and Javac).

##### Implementation Checklist
- [ ] In the Eclipse handler:
  - Use the `isRecord` check.
  - If the node is a record, ensure that the logic for `makeFinal` and `defaultPrivate` is skipped or effectively disabled.
- [ ] In the Javac handler:
  - Use the `isRecord` check.
  - If the node is a record, skip the relevant transformation logic.

##### Success Criteria
- [ ] The provided test case `test/transform/resource/before/FieldDefaultsViaConfigOnRecord.java` compiles and passes (or the generated code matches expectations where the record is left intact regarding modifiers).
- [ ] Regular classes still have `FieldDefaults` applied correctly (regression check).
