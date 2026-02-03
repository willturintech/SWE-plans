# Plan Name: Identify and Plan Bug Fix for Redis CSV Task

## Tasks

### 1. Identify why FCALL and redis.call bypass MONITOR in current implementation (Epic: Fix MONITOR to log FCALL/FUNCTION execution and nested redis.call commands)

#### Description

Reproduce the issue with the new introspection.tcl test failing, then trace the execution path to determine where MONITOR feed is skipped.

Implementation notes (Redis 7.x):
- Trace outer FCALL handling and confirm whether it reaches the normal monitor-feed point used for client commands.
- Trace redis.call/pcall execution path (functions engine) and confirm whether it uses a client/context that disables monitor feed.

Acceptance:
- A short note in code comments or commit message identifying the exact function(s)/branch(es) responsible for missing MONITOR entries.
- Local run of the single failing test shows current broken behavior prior to fix.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Identify why FCALL and redis.call bypass MONITOR in current implementation <-
    - upcoming (not yet): Ensure FCALL command itself is emitted to MONITOR exactly once
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Reproduce and pinpoint the exact Redis 7.x code path(s) where MONITOR logging is skipped for (a) the outer `FCALL` command and (b) subcommands executed inside functions via `redis.call`/`redis.pcall`.

##### Scope / Deliverable
Produce an implementation-oriented investigation write-up (commit message note or code comments) that identifies the precise function(s), branch(es), or flags responsible for the missing MONITOR entries. This ticket does **not** implement the fix; it establishes the root cause with evidence.

##### Technical Specs
- **Test reproduction**
  - Run the newly-added failing test in `tests/unit/introspection.tcl` that asserts MONITOR visibility for `FCALL` and nested `redis.call`.
  - Capture/inspect the MONITOR output to confirm the absence of expected lines (baseline broken behavior).
- **Tracing requirements (Redis server C)**
  - Trace the `FCALL` execution path from command dispatch through any function-engine entrypoint.
  - Verify whether the normal monitor feed point used for client commands is invoked (or bypassed) for `FCALL`.
  - Trace the execution path for `redis.call` / `redis.pcall` from the function engine into the generic command execution layer.
  - Confirm whether the function engine uses a synthetic client/context or execution flags that suppress monitor emission (e.g., “internal client”, “no logging”, “no propagation”, etc.).

##### Implementation Checklist
- [ ] Re-run only the relevant test(s) to reproduce failure deterministically (avoid running the full suite).
- [ ] Add lightweight tracing (debug logging guarded by compile-time/debug macros if needed) or use a debugger to identify:
  - Where monitor output is normally generated for standard commands.
  - Whether `FCALL` ever reaches that code.
  - Whether nested `redis.call` reaches that code, and if not, where it diverges.
- [ ] Identify the responsible function(s) and condition(s) with file+function names (and approximate line numbers if practical).
- [ ] Document findings as either:
  - A short, targeted code comment near the relevant branch, or
  - A concise commit message note describing: “why MONITOR is skipped” + “where to hook”.

##### Success Criteria
- [ ] The single failing introspection test is run locally and demonstrates the current broken behavior (missing `FCALL` and/or nested command MONITOR lines).
- [ ] A written note (comment or commit message) explicitly identifies the exact function(s)/branch(es)/flags causing bypass for:
  - `FCALL` monitor emission, and
  - nested `redis.call`/`redis.pcall` monitor emission.
- [ ] The write-up is specific enough that another engineer can implement tickets (6) and (7) without repeating the investigation.

##### Dependencies
- New failing test exists in `tests/unit/introspection.tcl` (from earlier test ticket).

##### Files to Read (guidance)
- `tests/unit/introspection.tcl` (the failing test case)
- Redis server sources related to:
  - command dispatch / execution (`processCommand*`, `call()`, etc.)
  - monitor feed (`replicationFeedMonitors()` / `feedMonitor()` or equivalents)
  - functions engine (`fcallCommand` / function execution helpers / scripting bridge for `redis.call`)

---


### 2. Fix MONITOR to log FCALL/FUNCTION execution and nested redis.call commands (Epic: user query)

#### Description

Implement Redis-side changes so MONITOR shows (1) the FCALL command itself and (2) the commands executed from within server-side functions (redis.call/pcall), preserving expected formatting and existing argument redaction behavior.

[REQ] Must log:
- The outer FCALL command line itself (as seen by the client).
- Each subcommand executed inside the function via redis.call/redis.pcall (e.g. SET foo bar).

[IMPL] Likely implementation shape (Redis 7.x):
- Ensure the FCALL command goes through the same monitoring path as normal commands (if it currently bypasses monitor feed due to special-casing in the functions subsystem).
- For subcommands invoked from inside functions, hook into the generic command execution path used by redis.call/pcall so it emits monitor lines using the same formatting/redaction code path as external commands.
- Avoid duplicate monitor lines: exactly one entry for FCALL + one per nested subcommand.
- Preserve argument redaction: any command flagged to redact args must remain redacted when emitted from within a function.
- Keep overhead minimal when no MONITOR clients are attached (fast no-op checks; no extra allocations).

[UNK] Expected touchpoints in Redis source tree (for implementer to confirm):
- MONITOR feed: replicationFeedMonitors()/feedMonitor() and related formatting helpers.
- Command execution: call()/processCommand*/command propagation path where monitor feed is normally emitted.
- Functions engine: FCALL/FUNCTION command handlers and the execution helper used by redis.call/pcall.

Deliverables:
- Source changes in Redis server (C) that make the tests pass.
- No regressions in existing MONITOR/redaction tests.


### 3. Regression coverage: MONITOR redaction + edge cases for function execution (Epic: user query)

#### Description

Ensure the fix does not leak sensitive args and behaves correctly across edge cases.

[REQ] Must preserve security expectations:
- Commands that are redacted in MONITOR when run normally must remain redacted when executed via redis.call/pcall inside functions.

Exit criteria:
- All relevant tests green; no unexpected extra monitor lines; no sensitive args leaked.


### 4. Add/adjust unit test for MONITOR visibility of FCALL + redis.call commands (Epic: user query)

#### Description

Land the proposed failing test (or equivalent) into tests/unit/introspection.tcl to reproduce the bug and validate the fix.

[REQ] Test assertions:
- With an active MONITOR client, executing FCALL should produce a MONITOR line for the FCALL command.
- The function body using redis.call('set','foo','bar') should produce a MONITOR line for the executed SET (or equivalent) with expected formatting.

[IMPL] Guidance to keep the test robust:
- Use a dedicated monitor client connection and drain its output deterministically.
- Avoid hard-coding timestamp/client id fields; match on command substrings/patterns that are stable.
- Use proper escaping/quoting patterns consistent with other MONITOR tests in introspection.tcl.


### 5. user query

#### Description

locate task_5_redis_redis.csv and create a plan to fix the bug contained inside.


### 6. Ensure FCALL command itself is emitted to MONITOR exactly once (Epic: Fix MONITOR to log FCALL/FUNCTION execution and nested redis.call commands)

#### Description

Modify the FCALL/FUNCTION execution path so the FCALL invocation produces a MONITOR line with standard formatting.

Constraints:
- Must not double-log FCALL (e.g., both at command dispatch and inside functions engine).
- Must preserve existing argument redaction rules.
- Must be gated by a cheap “any monitor clients?” check to keep overhead low.

Acceptance:
- The new unit test sees one MONITOR line containing the FCALL command.
- No extra FCALL-related monitor lines are emitted in the same execution.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Identify why FCALL and redis.call bypass MONITOR in current implementation
    - current (in progress task): Ensure FCALL command itself is emitted to MONITOR exactly once <-
    - upcoming (not yet): Emit MONITOR entries for redis.call/redis.pcall subcommands using standard formatting + redaction
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement Redis server changes so the **outer `FCALL` invocation** is emitted to MONITOR **exactly once**, using standard MONITOR formatting and preserving argument redaction behavior.

##### Technical Specs
- **Behavior**
  - When a MONITOR client is active, executing `FCALL ...` must produce one MONITOR line representing the `FCALL` command as seen by the calling client.
  - Emission must be consistent with how normal client commands are formatted in MONITOR (quoting/escaping, argument rendering).
- **Constraints**
  - Do not double-log `FCALL` (avoid “once at dispatch” + “once inside functions engine”).
  - Preserve existing MONITOR redaction rules (if `FCALL` args should be redacted per existing rules, do so).
  - Add negligible overhead when MONITOR is off: guard formatting/work behind a fast “any monitors?” check.

##### Implementation Checklist
- [ ] Locate the correct point to emit MONITOR for `FCALL` so it mirrors standard command handling.
- [ ] Ensure exactly one emission by auditing whether:
  - The generic command execution path already emits MONITOR for `FCALL`, or
  - `FCALL` is special-cased and requires explicit emission.
- [ ] If explicit emission is required:
  - Use the same monitor feed/formatting helper used for external commands (do not duplicate formatting logic).
  - Gate the work behind a fast monitor-clients-present check before doing any allocations.
- [ ] Validate no duplicate `FCALL` lines appear when nested calls occur.
- [ ] Keep changes minimal and localized; avoid altering unrelated MONITOR output formatting.

##### Success Criteria
- [ ] The new introspection unit test observes **one** MONITOR line containing the `FCALL` command.
- [ ] There are **no additional** `FCALL`-related MONITOR lines emitted during the same function execution.
- [ ] Existing MONITOR tests (including redaction-focused tests) remain green.
- [ ] Code review is able to verify a clear fast-path when MONITOR is disabled (no unconditional formatting/allocation).

##### Dependencies
- Requires ticket (5) investigation results (where FCALL bypass occurs) to choose the correct hook point.
- Requires the failing unit test that asserts FCALL visibility.

##### Files to Modify (expected)
- Redis server C sources in the FCALL/FUNCTION command handler and/or generic command execution/monitor feed path.

---


### 7. Emit MONITOR entries for redis.call/redis.pcall subcommands using standard formatting + redaction (Epic: Fix MONITOR to log FCALL/FUNCTION execution and nested redis.call commands)

#### Description

Hook the internal command execution used by server-side functions so each nested redis.call/pcall produces a MONITOR line, matching the behavior of normal client commands.

Constraints:
- Use the same formatting/redaction helpers as external commands.
- Ensure the ordering is deterministic: FCALL line first, then subcommands in the order executed.
- Avoid duplicates (ensure only one place feeds monitors for these internal calls).

Acceptance:
- The new unit test sees MONITOR lines containing the nested command(s), e.g. "SET foo bar".
- Existing MONITOR redaction tests still pass and no sensitive args are leaked.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Ensure FCALL command itself is emitted to MONITOR exactly once
    - current (in progress task): Emit MONITOR entries for redis.call/redis.pcall subcommands using standard formatting + redaction <-
    - upcoming (not yet): Performance + correctness verification for MONITOR-on/off scenarios
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement Redis server changes so **each** subcommand executed inside server-side functions via `redis.call` / `redis.pcall` emits a MONITOR entry, using the **same formatting and redaction** behavior as external client commands, with deterministic ordering and no duplicates.

##### Technical Specs
- **Behavior**
  - With MONITOR enabled, a function invoked via `FCALL` that runs `redis.call('SET','foo','bar')` (or equivalent) must generate a MONITOR line for the nested `SET foo bar`.
  - The MONITOR output ordering must be deterministic:
    1) `FCALL ...`
    2) nested subcommands in execution order
- **Constraints**
  - Use existing monitor formatting helpers (quoting/escaping) and the same redaction logic used for external commands.
  - Avoid duplicate monitor lines for the same nested command (ensure only one monitoring site is active for internal calls).
  - Preserve security expectations: redacted commands remain redacted when invoked internally.
  - Keep overhead minimal when no monitors are present (fast conditional checks).

##### Implementation Checklist
- [ ] Identify the internal execution mechanism used by `redis.call`/`redis.pcall` (function engine → generic execution).
- [ ] Ensure internal calls traverse (or explicitly invoke) the same monitor feed mechanism as normal commands.
- [ ] Confirm argument vectors/objects passed to monitor formatting are identical (or equivalent) to external command invocation, so formatting/redaction stays consistent.
- [ ] Ensure monitor emission happens:
  - For successful `redis.call` subcommands
  - For attempted `redis.pcall` subcommands (even when the call results in an error object returned to the function), consistent with existing expectations/tests
- [ ] Verify the exact emission point does not cause duplication (e.g., not both at an “internal call wrapper” and deep inside `call()`).
- [ ] Add/adjust minimal internal guards so no formatting work is done when MONITOR is off.

##### Success Criteria
- [ ] The introspection unit test sees MONITOR lines for nested subcommands (e.g., contains `SET foo bar` with stable formatting).
- [ ] Existing MONITOR redaction tests continue to pass; no secrets/arguments leak via nested function execution.
- [ ] Output order is deterministic and matches test expectations: one `FCALL` line, followed by one line per nested subcommand in execution order.
- [ ] No duplicates are observed for nested subcommand monitor entries across repeated runs.

##### Dependencies
- Depends on ticket (5) identification of the bypass point for `redis.call`/`redis.pcall`.
- Interacts with ticket (6) insofar as ordering/duplication between `FCALL` and nested subcommand logging must be correct.

##### Files to Modify (expected)
- Redis server C sources in the functions engine internal-call execution path and/or shared command execution/monitor feed helpers.

---


### 8. Performance + correctness verification for MONITOR-on/off scenarios (Epic: Fix MONITOR to log FCALL/FUNCTION execution and nested redis.call commands)

#### Description

Validate that the added logging adds negligible overhead when no MONITOR clients are attached and is correct when MONITOR is enabled.

Checklist:
- Confirm code paths are behind a fast condition (e.g., check monitor_clients count / server.monitors length before doing formatting allocations).
- Run unit tests that cover MONITOR and introspection; ensure no regressions.

Acceptance:
- All unit tests pass.
- Code review notes indicate no unconditional allocations/work were added on the common path when MONITOR is off.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Emit MONITOR entries for redis.call/redis.pcall subcommands using standard formatting + redaction
    - current (in progress task): Performance + correctness verification for MONITOR-on/off scenarios <-
    - upcoming (not yet): Apply proposed failing test to tests/unit/introspection.tcl
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Validate performance and correctness of the MONITOR logging changes for `FCALL` and nested `redis.call`/`redis.pcall`, with focus on ensuring negligible overhead when MONITOR is disabled and correct behavior when enabled.

##### Technical Specs
- **Correctness checks**
  - Run unit tests covering introspection/MONITOR behavior, including the new tests and existing MONITOR redaction tests.
  - Confirm no unrelated MONITOR output formatting regressions.
- **Performance / overhead checks**
  - Review implementation to ensure all additional work is behind a fast “any monitor clients?” gate (e.g., monitor client count / monitor list length).
  - Confirm no unconditional allocations, argument rewrites, or formatting occur on the common path when MONITOR is off.

##### Implementation Checklist
- [ ] Run the relevant unit test segments:
  - `tests/unit/introspection.tcl` (new FCALL + nested monitoring assertions)
  - MONITOR-focused tests, especially those asserting redaction behavior
- [ ] Perform a targeted code review pass on changes from tickets (6) and (7):
  - Verify the presence and placement of fast-path conditions
  - Identify any allocations/string formatting done before checking monitor presence
  - Ensure monitor formatting is invoked only when necessary
- [ ] Confirm correctness for both scenarios:
  - MONITOR disabled: no observable behavioral changes and minimal runtime overhead
  - MONITOR enabled: FCALL + nested command lines appear with correct ordering and redaction

##### Success Criteria
- [ ] All unit tests pass, including new introspection/MONITOR tests and existing redaction tests.
- [ ] Review notes explicitly confirm: no unconditional allocations/work were added to the common execution path when MONITOR is off.
- [ ] No MONITOR format regressions are introduced for unrelated commands (validated by existing assertions).


### 9. Apply proposed failing test to tests/unit/introspection.tcl (Epic: Add/adjust unit test for MONITOR visibility of FCALL + redis.call commands)

#### Description

Introduce the failing test case from the bug report (task_5_redis_redis.csv) into tests/unit/introspection.tcl.

Acceptance:
- Test is present, follows existing style, and fails on current Redis behavior (no FCALL / nested redis.call lines in MONITOR).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Performance + correctness verification for MONITOR-on/off scenarios
    - current (in progress task): Apply proposed failing test to tests/unit/introspection.tcl <-
    - upcoming (not yet): Make MONITOR assertions stable and deterministic
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add a new failing unit test to reproduce the bug where `MONITOR` does not show `FCALL` and does not show commands executed via `redis.call` inside a function.

##### Scope / Intent
Introduce (as-is or equivalent) the failing test case from `@tasks/task_5_redis_redis.csv` into Redis’ `tests/unit/introspection.tcl`, in the same style as existing `MONITOR` tests. The test must fail on current/broken behavior (i.e., before the server-side fix), demonstrating missing monitor entries.

##### Technical Specs
- **Test file**: `tests/unit/introspection.tcl`
- **Test behavior**:
  - Define and load a Redis Function (library) that executes at least one nested command via `redis.call(...)` (e.g., `SET foo bar`).
  - Start a `MONITOR` client.
  - Execute the function via `FCALL`.
  - Assert that monitor output includes:
    - a line for the `FCALL` invocation
    - a line for the nested command (e.g., `SET foo bar`)
- **Assertions**: match only stable command tokens/quoting (do not assert on timestamps/client ids).

##### Implementation Checklist
- [ ] Locate the proposed patch/test in `@tasks/task_5_redis_redis.csv` and transcribe it into `tests/unit/introspection.tcl` (or implement an equivalent minimal reproduction).
- [ ] Place the test in the appropriate section near existing `MONITOR` tests; follow naming conventions and formatting.
- [ ] Ensure the test uses a function body that performs a clear nested call (`redis.call`) with easily matchable arguments (e.g., `foo` / `bar`).
- [ ] Add the initial assertions for both the outer `FCALL` and inner nested command.

##### Success Criteria
- [ ] Test is present in `tests/unit/introspection.tcl` and follows existing test style.
- [ ] On the currently broken Redis behavior, the test fails specifically because the expected `MONITOR` lines for `FCALL` and/or nested `redis.call` are absent (not due to unrelated errors like function load failures).

##### Files to Read
- `@tasks/task_5_redis_redis.csv` (bug report + proposed failing test)
- `tests/unit/introspection.tcl` (existing `MONITOR` tests for style/patterns)

##### Files to Modify
- `tests/unit/introspection.tcl`


### 10. Make MONITOR assertions stable and deterministic (Epic: Add/adjust unit test for MONITOR visibility of FCALL + redis.call commands)

#### Description

Adjust the test to avoid flakes:
- Use a dedicated monitor connection.
- Read/drain monitor output deterministically (wait for N lines, or loop until patterns match).
- Match only stable parts of the line (command tokens / quoting), avoid timestamps/client IDs.

Acceptance:
- Test passes reliably across repeated runs once the fix is in.
- Test does not depend on wall clock timing beyond standard test harness patterns.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Apply proposed failing test to tests/unit/introspection.tcl
    - current (in progress task): Make MONITOR assertions stable and deterministic <-
    - upcoming (not yet): Ensure test cleanup (MONITOR client teardown)
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Harden the new `MONITOR` + `FCALL` introspection unit test so it is deterministic and non-flaky across repeated runs and varying environments.

##### Scope / Intent
Refactor/adjust the test added in task (9) to reliably capture and assert `MONITOR` output without depending on wall clock timing, and without matching unstable parts of monitor lines (timestamps, DB/client identifiers, etc.).

##### Technical Specs
- **Dedicated monitor connection**:
  - Use a dedicated client connection solely for `MONITOR` to avoid interleaving with other commands.
- **Deterministic read/drain**:
  - Implement a robust “read until patterns observed” loop or “read N lines then assert” approach consistent with Redis test harness practices.
  - Ensure the test drains any pre-existing monitor output before the action under test (`FCALL`) to avoid false positives.
- **Stable matching**:
  - Match only stable substrings/patterns: command name + args with correct quoting/escaping as used by existing tests.
  - Avoid asserting on timestamp prefix, client id, or address fields.
- **Order**:
  - Prefer asserting ordering if it is guaranteed (e.g., `FCALL` line first, then nested `SET`), but do so using deterministic parsing/collection rather than timing.

##### Implementation Checklist
- [ ] Update monitor-capture logic to explicitly drain initial `MONITOR` output before running `FCALL`.
- [ ] Implement a deterministic collection routine:
  - loop reading monitor lines until both expected patterns are found, with a bounded max-iterations to prevent hangs.
  - alternatively, read a bounded number of lines and assert membership.
- [ ] Update assertions to use stable patterns aligned with other `introspection.tcl` `MONITOR` tests (quoting/escaping included).
- [ ] Ensure the test does not introduce fixed `after`/sleep timing beyond established harness patterns.

##### Success Criteria
- [ ] Test passes reliably once the server fix is present, across repeated runs (no flakes).
- [ ] Test does not depend on timestamps, client ids, or wall clock sleeps to observe output.
- [ ] Assertions are resilient to minor formatting variance outside the command token payload (e.g., changing client address formatting should not break the test).

##### Files to Read
- `tests/unit/introspection.tcl` (existing deterministic MONITOR tests/helpers)

##### Files to Modify
- `tests/unit/introspection.tcl` (the newly added test from task 9)


### 11. Ensure test cleanup (MONITOR client teardown) (Epic: Add/adjust unit test for MONITOR visibility of FCALL + redis.call commands)

#### Description

Ensure the monitor client is properly closed/disabled so later tests are not affected.

Acceptance:
- No cross-test interference (no unexpected extra MONITOR output in later tests).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Make MONITOR assertions stable and deterministic
    - current (in progress task): Ensure test cleanup (MONITOR client teardown) <-
    - upcoming (not yet): Add redaction regression test for redacted commands executed inside a function
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Ensure the `MONITOR` client used by the new `FCALL`/function introspection tests is properly torn down so it cannot affect later tests.

##### Scope / Intent
Prevent cross-test interference caused by leaving a client in `MONITOR` mode or leaving unread monitor output buffered. After the test completes, the monitoring connection must be cleanly stopped and closed.

##### Technical Specs
- **Teardown requirements**:
  - Disable monitor mode and/or close the dedicated monitor connection deterministically.
  - Drain any remaining monitor output if required by the harness to avoid impacting subsequent reads.
- **Isolation**:
  - The test should not leave extra background clients, blocked sockets, or lingering monitor state.

##### Implementation Checklist
- [ ] Add explicit teardown steps at the end of the test:
  - issue an appropriate command / disconnect sequence to stop monitoring
  - close the connection using existing harness patterns
- [ ] Ensure teardown runs even if assertions fail (use the test framework’s cleanup/finally patterns where available in Tcl tests).
- [ ] Verify no additional monitor lines appear in subsequent tests due to leaked monitor clients.

##### Success Criteria
- [ ] No cross-test interference: later tests do not observe unexpected `MONITOR` output and do not hang waiting for monitor reads.
- [ ] The monitor client is reliably terminated/closed in all test outcomes (pass/fail).

##### Files to Read
- `tests/unit/introspection.tcl` (patterns for client teardown and monitor tests)

##### Files to Modify
- `tests/unit/introspection.tcl`


### 12. Add redaction regression test for redacted commands executed inside a function (Epic: Regression coverage: MONITOR redaction + edge cases for function execution)

#### Description

Create/extend a test that executes a command known to be MONITOR-redacted when called normally, but invoked via redis.call inside a function.

Steps:
- Identify an existing redaction command in the test suite (e.g., one of the AUTH/ACL/CONFIG style commands covered by current MONITOR redaction tests).
- Define a function that runs it with a clearly recognizable secret argument.
- Start MONITOR and run FCALL to trigger the function.
- Assert the monitor output contains the command but does not contain the secret argument; instead it uses the same redaction placeholder format as external invocations.

Acceptance:
- Test fails if secret is leaked.
- Test passes with fix and alongside existing redaction tests.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Ensure test cleanup (MONITOR client teardown)
    - current (in progress task): Add redaction regression test for redacted commands executed inside a function <-
    - upcoming (not yet): Add edge-case regression: multiple nested redis.call invocations
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add a regression test ensuring `MONITOR` argument redaction is preserved when a redacted command is executed inside a function via `redis.call`.

##### Scope / Intent
Create or extend unit coverage proving that commands which are normally redacted in `MONITOR` output (e.g., `AUTH`, `ACL SETUSER`, `CONFIG SET` depending on existing coverage) remain redacted when invoked from within server-side functions (`FCALL` → `redis.call(...)`). The test must fail if a secret leaks.

##### Technical Specs
- **Test file**: `tests/unit/introspection.tcl`
- **Approach**:
  1. Identify an existing `MONITOR` redaction test in `introspection.tcl` and reuse the same command type and expected placeholder formatting.
  2. Define/load a Redis Function that calls the chosen redacted command via `redis.call`, including a clearly recognizable secret argument (e.g., `S3CR3T-DO-NOT-LEAK`).
  3. Start a dedicated `MONITOR` client and drain output deterministically.
  4. Execute the function via `FCALL`.
  5. Assert monitor output:
     - includes the command name/token sequence indicating the command ran
     - does **not** include the secret literal anywhere
     - includes the same redaction placeholder format used for the equivalent external invocation in existing tests (do not invent a new placeholder)

##### Implementation Checklist
- [ ] Locate existing redaction coverage in `tests/unit/introspection.tcl` and pick one command already asserted to be redacted.
- [ ] Implement a function library whose body invokes that redacted command via `redis.call` with a unique secret string.
- [ ] Add monitor capture logic using the deterministic pattern established in task (10): dedicated monitor connection + drain + bounded read loop.
- [ ] Add assertions:
  - positive match for presence of the redacted command line (stable tokens)
  - negative match ensuring the secret is absent
  - positive match for the correct redaction placeholder formatting used elsewhere in the file
- [ ] Add teardown to ensure monitor client is closed (align with task (11) patterns).

##### Success Criteria
- [ ] Test fails if the secret argument appears in any `MONITOR` line produced by executing the function.
- [ ] Test passes when redaction behavior is correct for function-internal calls and does not break existing redaction tests.
- [ ] The expected redaction placeholder matches the existing suite’s behavior for the same command executed externally.

##### Dependencies
- Depends on having stable `MONITOR` read/drain and teardown patterns available (reuse work from tasks 10/11).

##### Files to Read
- `tests/unit/introspection.tcl` (existing MONITOR redaction tests and placeholder expectations)

##### Files to Modify
- `tests/unit/introspection.tcl`


### 13. Add edge-case regression: multiple nested redis.call invocations (Epic: Regression coverage: MONITOR redaction + edge cases for function execution)

#### Description

Add a test function that performs multiple redis.call/redis.pcall invocations (including a write and a read).

Assertions:
- MONITOR shows one line per nested command in execution order.
- There is exactly one FCALL entry.
- No duplicate lines for the same nested command.

Acceptance:
- Deterministic pass across repeated runs.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add redaction regression test for redacted commands executed inside a function
    - current (in progress task): Add edge-case regression: multiple nested redis.call invocations <-
    - upcoming (not yet): Add edge-case regression: redis.pcall error path still logs attempted subcommand
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add a deterministic regression test in `tests/unit/introspection.tcl` that validates MONITOR output when a server-side function (invoked via `FCALL`) performs **multiple nested `redis.call`/`redis.pcall` invocations**, including at least one write and one read.

##### Technical Specs
- **Test location:** `tests/unit/introspection.tcl` in the existing MONITOR-related section (follow established style/patterns).
- **Function under test:** Define a Lua function via `FUNCTION LOAD` that:
  - Executes multiple subcommands in sequence, e.g.:
    - `redis.call('set','k','v')`
    - `redis.call('get','k')`
    - Optionally an extra command to ensure >2 nested calls (e.g., `del`, `exists`, `incr`) while keeping assertions stable.
  - Returns a simple deterministic value (e.g., the GET result) so the test can assert the function itself succeeded.
- **MONITOR harness:** Use a dedicated MONITOR client connection and read/drain output deterministically. Avoid reliance on timestamps, client ids, or wall-clock ordering beyond “eventually receive N expected lines”.

##### Required Assertions
- Exactly **one** MONITOR line corresponding to the outer `FCALL` invocation.
- MONITOR includes **one line per nested subcommand** executed inside the function, in **execution order**.
- No duplicate MONITOR lines for the same nested command (e.g., only one `SET ...`, only one `GET ...`).
- Match only stable substrings/patterns in the MONITOR output:
  - Must match presence of command tokens and args (with correct quoting as used elsewhere in `introspection.tcl`).
  - Must not hard-code timestamps, db numbers, client ids, or addresses.

##### Implementation Checklist
- [ ] Add a new test case block with a unique, descriptive test name under the introspection/MONITOR tests.
- [ ] Create/Load a function with multiple `redis.call` / `redis.pcall` invocations.
- [ ] Start MONITOR on a dedicated client, then execute `FCALL`.
- [ ] Collect monitor lines deterministically until all expected patterns are observed or a bounded timeout/iteration limit is reached (use existing helper patterns in this file).
- [ ] Assert:
  - One `FCALL` line total.
  - One line each for the nested commands in order.
  - No duplicates (e.g., count matches per command pattern).
- [ ] Ensure cleanup: stop/close the MONITOR client and delete any keys used (`DEL k`) to prevent cross-test interference.

##### Success Criteria
- [ ] Test fails on buggy behavior where nested calls (or FCALL) are missing from MONITOR.
- [ ] Test passes reliably across repeated runs once the fix is present (no flakes).
- [ ] Test does not introduce dependence on unstable MONITOR fields.

##### Files to Modify
- `tests/unit/introspection.tcl`


### 14. Add edge-case regression: redis.pcall error path still logs attempted subcommand (Epic: Regression coverage: MONITOR redaction + edge cases for function execution)

#### Description

Add a test function that uses redis.pcall on an invalid command (or wrong arity) to force an error without aborting the function.

Assertions:
- MONITOR includes an entry for the attempted subcommand.
- Function returns expected error object/structure without breaking the test.

Acceptance:
- Prevents regressions where internal errors suppress monitor logging.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add edge-case regression: multiple nested redis.call invocations
    - current (in progress task): Add edge-case regression: redis.pcall error path still logs attempted subcommand <-
    - upcoming (not yet): Run relevant test suite segments and confirm no MONITOR format regressions
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add a regression test in `tests/unit/introspection.tcl` ensuring that when a server-side function uses `redis.pcall` and triggers an error (invalid command or wrong arity), **MONITOR still logs the attempted subcommand**, and the function returns a structured error response without aborting the whole function execution.

##### Technical Specs
- **Test location:** `tests/unit/introspection.tcl`, near other MONITOR/function tests.
- **Function behavior:** Load a function via `FUNCTION LOAD` that:
  - Executes a known-failing call via `redis.pcall`, such as:
    - Unknown command (preferred for stability), e.g. `redis.pcall('NO_SUCH_CMD','x')`, or
    - Wrong arity for a real command (only if stable across versions), e.g. `redis.pcall('SET','onlykey')`.
  - Optionally performs a follow-up valid command after the failing `pcall` (e.g., `redis.call('set','ok','1')`) to ensure function continues executing.
  - Returns the `pcall` result (error object/table) in a deterministic form that can be asserted.
- **MONITOR harness:** Dedicated MONITOR connection, deterministic drain, stable substring matching only.

##### Required Assertions
- MONITOR output contains:
  - Exactly one `FCALL` entry for the function invocation.
  - An entry for the attempted failing subcommand (the command name should appear in the MONITOR line).
- The `FCALL` invocation returns an error object/structure consistent with `redis.pcall` semantics (i.e., error is captured rather than aborting execution).
  - Assertions must be robust to minor formatting differences; validate key properties (e.g., reply type indicates error, or returned string contains “ERR”/command name), consistent with other tests in the suite.
- If a follow-up valid command is included, MONITOR must also show it and the test must assert it happened after the failing one.

##### Implementation Checklist
- [ ] Add a new test case with a focused name (pcall error path logging).
- [ ] Load a function containing a failing `redis.pcall` invocation.
- [ ] Start MONITOR on a dedicated client, execute `FCALL`, capture function reply.
- [ ] Deterministically collect MONITOR lines until expected patterns are observed.
- [ ] Assert:
  - Presence of the failing subcommand line (match stable tokens).
  - (Optional) Presence of the follow-up command line, in correct order.
  - Exactly one `FCALL` line.
- [ ] Cleanup: stop/close MONITOR client; delete keys used.

##### Success Criteria
- [ ] Test prevents regressions where errors inside `redis.pcall` suppress MONITOR logging.
- [ ] Deterministic pass across repeated runs once the fix is in.
- [ ] No cross-test interference via leaked MONITOR state or leftover keys.

##### Files to Modify
- `tests/unit/introspection.tcl`


### 15. Run relevant test suite segments and confirm no MONITOR format regressions (Epic: Regression coverage: MONITOR redaction + edge cases for function execution)

#### Description

Execute the unit test(s) that cover:
- tests/unit/introspection.tcl (new FCALL + nested call visibility test)
- Existing MONITOR tests (including redaction).

Acceptance:
- All tests pass.
- No change in output formatting for unrelated MONITOR cases (validated by existing assertions).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add edge-case regression: redis.pcall error path still logs attempted subcommand
    - current (in progress task): Run relevant test suite segments and confirm no MONITOR format regressions <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run the relevant Redis unit test segments to validate that the new MONITOR + functions coverage does not regress existing MONITOR formatting/redaction behavior, and record/confirm outcomes as part of the ticket completion.

##### Technical Specs
- **Primary test file:** `tests/unit/introspection.tcl`
- **Scope to include:**
  - Newly added FCALL/nested-call visibility tests
  - Existing MONITOR tests in `introspection.tcl`, including redaction-related assertions
- **Execution method:** Use the project’s standard Redis test runner invocation patterns (as used elsewhere in the repo/docs). Ensure repeated runs are feasible to detect flakes.

##### Implementation Checklist
- [ ] Execute `tests/unit/introspection.tcl` (entire file, not just a single test) to ensure:
  - New tests pass
  - Existing MONITOR assertions (including redaction) remain unchanged and green
- [ ] Execute any additional existing MONITOR-focused test subsets if they exist in the suite (e.g., other `tests/unit/*` files that explicitly test MONITOR/redaction), but do not broaden scope beyond what is relevant to MONITOR formatting/security.
- [ ] Re-run the relevant subset at least once (or in a small loop) to confirm determinism/no flakes introduced by MONITOR read/drain logic.
- [ ] Confirm no unexpected output-format changes were required to satisfy new tests (the point is to validate compatibility with existing assertions, not to update golden patterns broadly).

##### Success Criteria
- [ ] All executed tests pass (including redaction/security-related MONITOR tests).
- [ ] No unrelated MONITOR output formatting changes are introduced (validated by existing assertions staying green).
- [ ] Repeated runs show deterministic results for the new MONITOR tests (no intermittent failures).

##### Deliverable Notes
- Provide a brief run summary in the ticket/PR description (commands run + confirmation that introspection/MONITOR/redaction tests passed), suitable for reviewer verification.
