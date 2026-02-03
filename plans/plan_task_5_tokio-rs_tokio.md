# Plan Name: Analyze and Plan Bug Fix for Tokio CSV Task

## Tasks

### 1. Tokio mpsc is_empty()/len() bugfix (Windows every 32 msgs) — implement + verify (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Deliver regression coverage + fix for Tokio v1.37.0 Windows bug where `Receiver::is_empty()` can return `false` while `len()==0` (periodic every 32 messages). Covers bounded `mpsc::Receiver` and, where feasible, `UnboundedReceiver`.

Scope/constraints:
- No breaking public API changes.
- Thread-safe and performant (no heavy locks).
- Cross-platform correctness; regression must exercise Windows.

Success criteria:
- New regression test(s) fail on affected versions/platform (Windows) pre-fix and pass post-fix.
- Existing `tokio/tests/sync_mpsc.rs` remains passing.
- `is_empty()` consistent with `len()==0` in steady state (after drain).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Tokio mpsc is_empty()/len() bugfix (Windows every 32 msgs) — implement + verify <-
    - upcoming (not yet): Add bounded regression test to `tokio/tests/sync_mpsc.rs`
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Deliver the complete fix + verification for the Tokio v1.37.0 Windows bug where `mpsc::Receiver::is_empty()` (and potentially `UnboundedReceiver::is_empty()`) can report `false` while `len() == 0`, periodically (reported every 32 messages). Keep the change localized, thread-safe, cross-platform, and performant (no heavy locks, no breaking public API changes). Ensure all existing `tokio/tests/sync_mpsc.rs` tests keep passing and add/keep regression coverage.

##### Technical Specs
- **Code area**: `tokio/src/sync/mpsc/**` (bounded + unbounded implementations as applicable).
- **Behavioral invariant (steady-state, post-drain)**: after a `recv()` that drains the channel, `len() == 0` must imply `is_empty() == true` for that receiver instance.
- **Concurrency constraints**:
  - Preserve existing semantics: `len()` is a snapshot under concurrency; do not attempt to make it linearizable via locks.
  - Avoid adding blocking synchronization; prefer a small number of atomic ops.
  - Fix must be correct under weak memory models and on Windows.

##### Implementation Checklist
- [ ] Ensure the bounded regression test from task (17) is present and passes after the fix.
- [ ] Ensure unbounded coverage from task (18) is present, or a code-adjacent explanation exists if impossible with public API.
- [ ] Identify the source-of-truth for queue occupancy (counter/indices/bitfields) used by `len()` and unify `is_empty()` to derive emptiness from the same source-of-truth as `len()` (or vice-versa), unless this would break semantics.
- [ ] If `len()` and `is_empty()` already read the same underlying state, unify the **atomic ordering** (loads/stores) so `is_empty()` cannot observe stale/non-empty state after the receiver has drained a message.
- [ ] If internal state is bit-packed or uses wraparound logic, explicitly validate the correctness of mask/shift/wrap behavior around a 32-period boundary; fix any off-by-one or masking errors.
- [ ] Add a short comment near the chosen logic documenting the invariant and why the ordering/state selection is correct (including mention of the Windows/32-msg regression).

##### Success Criteria (Verification)
- [ ] On Windows, the new regression test(s) reproduce the failure on the affected version/commit (at least intermittently/periodically as reported) and pass reliably after the fix.
- [ ] `cargo test -p tokio --test sync_mpsc` passes on all supported platforms.
- [ ] No public API changes; no performance regressions from introducing locking/heavy synchronization.
- [ ] Code review demonstrates `is_empty()` and `len()` cannot diverge in the post-drain steady-state due to reading different state or using weaker/stale atomic visibility.

##### Files to Read
- `tokio/src/sync/mpsc/**` (bounded + unbounded internals)
- `tokio/tests/sync_mpsc.rs`

##### Files to Modify
- `tokio/src/sync/mpsc/**` (targeted, minimal changes)
- `tokio/tests/sync_mpsc.rs` (regression tests)

---


### 2. Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs)

#### Description

Implement a bugfix in Tokio `sync::mpsc` where `Receiver::is_empty()` (and likely `UnboundedReceiver::is_empty()`) can return `false` even when `len()==0`, reproducible on Windows every 32 messages (Tokio v1.37.0).

[REQ] Add regression test(s) that fail on affected versions/platforms and pass after fix; keep `tokio/tests/sync_mpsc.rs` passing.
[REQ] Fix must be thread-safe, cross-platform, and avoid heavy locking or breaking changes.

Notes/assumptions for this plan:
- We will cover both bounded and unbounded receivers because the bug report mentions both and they likely share the same internal counter/queue-state logic.
- The plan includes concrete investigation steps (instrumentation + hypothesis validation) but keeps scope to implementation work (no standalone research-only tickets).


### 3. Add bounded regression test to `tokio/tests/sync_mpsc.rs` (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Implement the regression test described in the task CSV’s `test_patch`.

Implementation details:
- Add `#[tokio::test] async fn test_is_empty_32_msgs()`.
- Use `let (tx, mut rx) = mpsc::channel(33);`.
- Loop `for value in 1..257`:
  - `tx.send(value).await.unwrap();`
  - `rx.recv().await.unwrap();`
  - Assert `rx.is_empty()` with diagnostic message including `value` and `rx.len()`.

Acceptance criteria:
- Test compiles and runs.
- On Windows with affected Tokio version (or when checking out the affected commit), it reproduces the failure (at least intermittently/periodically as reported).
- After fix, passes reliably.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Tokio mpsc is_empty()/len() bugfix (Windows every 32 msgs) — implement + verify
    - current (in progress task): Add bounded regression test to `tokio/tests/sync_mpsc.rs` <-
    - upcoming (not yet): Add unbounded regression test (or document why not possible via public API)
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add the bounded regression test to `tokio/tests/sync_mpsc.rs` exactly as described in the provided patch, ensuring it compiles, runs, and demonstrates the reported `is_empty()`/`len()` inconsistency on Windows pre-fix.

##### Technical Specs
- **Test file**: `tokio/tests/sync_mpsc.rs`
- **Test name**: `test_is_empty_32_msgs`
- **Channel**: bounded `mpsc::channel(33)`
- **Loop**: `for value in 1..257` (inclusive start, exclusive end)
  - `tx.send(value).await.unwrap();`
  - `rx.recv().await.unwrap();`
  - `assert!(rx.is_empty(), "... value={value} len={}", rx.len());` (diagnostic must include `value` and `rx.len()`)

##### Implementation Checklist
- [ ] Add `#[tokio::test] async fn test_is_empty_32_msgs()` to `tokio/tests/sync_mpsc.rs`.
- [ ] Import/use the existing `tokio::sync::mpsc` patterns consistent with the file.
- [ ] Ensure the assertion message includes both:
  - the current `value`
  - the observed `rx.len()`
- [ ] Keep the test deterministic in structure (no sleeps/timeouts); it should rely only on send/recv ordering.

##### Success Criteria
- [ ] Test compiles and runs in the existing Tokio test harness.
- [ ] On Windows with the affected Tokio version/commit, the test reproduces the failure (at least intermittently/periodically as reported).
- [ ] After the fix (task 16), the test passes reliably.

##### Files to Modify
- `tokio/tests/sync_mpsc.rs`

---


### 4. Add unbounded regression test (or document why not possible via public API) (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Attempt to add a parallel regression test for `mpsc::unbounded_channel()`/`UnboundedReceiver` if it exposes `len()` and `is_empty()` methods.

Implementation details:
- Add a `#[tokio::test]` that sends and receives in a loop (>= 256 iterations) and asserts `is_empty()` after each recv.
- If `len()` is not available for unbounded receiver, keep assertion focused on `is_empty()` and include diagnostics available.
- If `is_empty()`/`len()` are not both publicly available, add a short comment in the test file referencing the upstream issue and why unbounded coverage cannot be expressed with current public methods.

Acceptance criteria:
- Either: unbounded regression test exists and behaves analogously to bounded; or: an explicit, code-adjacent explanation is added for why it cannot be tested without internal APIs.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add bounded regression test to `tokio/tests/sync_mpsc.rs`
    - current (in progress task): Add unbounded regression test (or document why not possible via public API) <-
    - upcoming (not yet): Locate implementations of `len()` and `is_empty()` for bounded/unbounded receivers
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add an unbounded-channel regression test analogous to the bounded one, validating `UnboundedReceiver::is_empty()` after each `recv()` in a >=256-iteration loop. If the public API does not allow expressing the same `len()==0` vs `is_empty()` invariant (e.g., missing `len()` or `is_empty()`), document this in a short, code-adjacent comment in the test file referencing the upstream issue and the specific API limitation.

##### Technical Specs
- **Target**: `tokio::sync::mpsc::unbounded_channel()`
- **Test behavior**:
  - Send then receive in a tight loop (>= 256 iterations).
  - Assert `rx.is_empty()` after each `recv()`.
  - If `len()` exists, include it in diagnostics and/or assertions; otherwise, keep diagnostics focused on `is_empty()` and iteration value.

##### Implementation Checklist
- [ ] Check whether `UnboundedReceiver` exposes:
  - `is_empty()`
  - `len()`
- [ ] If both exist:
  - [ ] Add `#[tokio::test]` that mirrors the bounded test structure and includes both `value` and `rx.len()` in assertion diagnostics.
- [ ] If only `is_empty()` exists:
  - [ ] Add the regression test asserting `is_empty()` post-recv with diagnostics including the iteration `value`.
- [ ] If the needed methods are not publicly available to express the regression:
  - [ ] Add a short comment in `tokio/tests/sync_mpsc.rs` near the bounded regression referencing the upstream issue and stating precisely why unbounded cannot be covered via public API (name the missing method(s)).

##### Success Criteria
- [ ] Either:
  - An unbounded regression test exists and behaves analogously (>=256 iterations, assert post-recv `is_empty()`), **or**
  - A clear, code-adjacent explanation exists documenting why unbounded coverage is not possible without internal APIs.
- [ ] Existing `sync_mpsc` tests remain passing after adding the test/comment.

##### Files to Modify
- `tokio/tests/sync_mpsc.rs`

---


### 5. Locate implementations of `len()` and `is_empty()` for bounded/unbounded receivers (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

In `tokio/src/sync/mpsc/*`, identify:
- Where `Receiver::len()` reads its state.
- Where `Receiver::is_empty()` reads its state.
- The analogous methods for unbounded receiver (if present).

Capture in code comments or PR description:
- Which internal atomics/bitfields/indices are used.
- Any batching, masking, or wraparound logic (look for boundaries consistent with 32).

Acceptance criteria:
- Clear mapping of both public methods to the internal state they read, sufficient to reason about divergence.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add unbounded regression test (or document why not possible via public API)
    - current (in progress task): Locate implementations of `len()` and `is_empty()` for bounded/unbounded receivers <-
    - upcoming (not yet): Add test-only instrumentation to capture raw internal state at failure point
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate and document (in code comments or PR description notes stored near the relevant code) the implementations of `len()` and `is_empty()` for both bounded and unbounded receivers, and identify exactly which internal state each method reads (atomics/bitfields/indices). Pay special attention to any batching/masking/wraparound behavior that could create a 32-message periodic artifact.

##### Technical Specs
- **Code area**: `tokio/src/sync/mpsc/**`
- **Deliverable**: a “mapping” from:
  - `Receiver::len()` → internal fields/state reads (with file + type/struct names)
  - `Receiver::is_empty()` → internal fields/state reads
  - `UnboundedReceiver::{len,is_empty}` equivalents (if present)
- **What to capture**:
  - The specific atomic variables / counters / indices used (names + where defined).
  - Memory ordering used for relevant loads/stores (e.g., Acquire/Relaxed).
  - Any bit packing, masks, shifts, wraparound modulus, ring-buffer sizing logic.
  - Any constants or behavior that align with “32” (e.g., `& 31`, `>> 5`, chunk sizes).

##### Implementation Checklist
- [ ] Find bounded receiver `len()` implementation and record:
  - file path, struct, and the internal field(s) read
  - atomic orderings and any derived computations
- [ ] Find bounded receiver `is_empty()` implementation and record the same details.
- [ ] Repeat for unbounded receiver (or confirm absence of one/both methods).
- [ ] Add minimal documentation in one of:
  - a concise comment near the relevant implementations, or
  - a dedicated internal comment block near shared helpers/state definitions
  The documentation must be sufficient for a reviewer to understand how divergence could occur.
- [ ] Note any 32-related batching/masking/wrap logic explicitly (even if believed correct).

##### Success Criteria
- [ ] Clear, reviewable mapping exists for bounded and unbounded methods, sufficient to reason about how `len()` and `is_empty()` could diverge (different state vs stale read vs masking bug).
- [ ] The documentation is localized and does not add noisy logs or test-only hacks in production code paths.

##### Files to Read (minimum)
- `tokio/src/sync/mpsc/**`

##### Files to Modify
- `tokio/src/sync/mpsc/**` (comments only, unless small refactors are required to make the mapping clear)


### 6. Add test-only instrumentation to capture raw internal state at failure point (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Add minimal, removable instrumentation to confirm the divergence mechanism.

Implementation guidance:
- Use `#[cfg(test)]` gated helpers or debug assertions.
- Prefer exposing a debug snapshot function within the mpsc module (private) that returns relevant raw counters/flags.
- Use it from the regression test when an assertion is about to fail (or via additional asserts) to print raw state.

Acceptance criteria:
- When the regression triggers on Windows pre-fix, logs/diagnostics clearly show the two sources-of-truth disagreeing (or a memory ordering stale read).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate implementations of `len()` and `is_empty()` for bounded/unbounded receivers
    - current (in progress task): Add test-only instrumentation to capture raw internal state at failure point <-
    - upcoming (not yet): Implement fix: align `is_empty()` with the same source-of-truth as `len()` and correct atomic ordering
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add **test-only instrumentation** to Tokio `sync::mpsc` to capture the **raw internal state** needed to explain why `Receiver::is_empty()` can return `false` while `len()==0` (Windows, periodic every 32 messages).

##### Technical Specs
- **Scope**: Instrumentation only; do not change runtime behavior outside tests.
- **Where**: `tokio/src/sync/mpsc/*` modules implementing bounded/unbounded channels (where `len()` / `is_empty()` read state).
- **How**:
  - Add a **private** helper under `#[cfg(test)]` (or `cfg(any(test, feature = "tokio-internal-debug"))` if already used in repo) that returns a **snapshot struct** containing relevant counters/flags used by both `len()` and `is_empty()`.
  - Use **non-mutating** reads only (atomic loads) with the same orderings those methods use (and/or include both “current ordering” and “stronger ordering” loads if needed to confirm stale reads).
  - Ensure the helper is callable from `tokio/tests/sync_mpsc.rs` without exposing new public API (keep visibility crate-private or module-private and access via existing test-only paths/patterns used in Tokio).

##### Implementation Checklist
- [ ] Identify the minimal set of internal fields that explain divergence (e.g., message count, queue indices, flags, waker state, closed bits, bit-packed words).
- [ ] Create a `#[cfg(test)]` “debug snapshot” struct (derive `Debug`, `Clone`, `Copy` if practical) and a function to capture it for:
  - [ ] bounded `mpsc::Receiver`
  - [ ] unbounded `mpsc::UnboundedReceiver` (if it shares machinery, reuse snapshot plumbing)
- [ ] Update the new regression test(s) to print snapshot details **only on failure** (e.g., build an error message string that includes `len()`, `is_empty()`, and the snapshot).
- [ ] Keep instrumentation minimal, localized, and easy to delete; avoid adding persistent logging.

##### Success Criteria
- [ ] When the regression triggers on Windows pre-fix, assertion output includes a snapshot that clearly shows either:
  - [ ] `len()` and `is_empty()` are reading **different sources-of-truth**, or
  - [ ] the same source-of-truth is read but a **stale/ordering** discrepancy is observable.
- [ ] No existing tests become noisy; diagnostics appear only when an assertion fails (or behind `RUST_LOG` if Tokio already has a test logging convention).

##### Files to modify (expected)
- `tokio/src/sync/mpsc/**.rs` (exact file depends on where receiver state lives)
- `tokio/tests/sync_mpsc.rs` (augment failure diagnostics for the regression test)


### 7. Implement fix: align `is_empty()` with the same source-of-truth as `len()` and correct atomic ordering (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Modify the mpsc internals so that `is_empty()` cannot observe a non-empty state when `len()` reports 0 after the receiver has drained the message.

Implementation guidance (choose the smallest safe change confirmed by prior subtasks):
- If `is_empty()` reads a different counter/flag than `len()`, switch it to derive emptiness from the same counter.
- If both read the same counter but with different memory ordering/atomic load semantics, unify ordering to ensure post-recv state is visible.
- If state is bit-packed and a 32-period artifact indicates masking/shifting bug, correct the mask/shift/wrap logic.

Constraints:
- Preserve existing concurrency semantics: `len()` remains a snapshot; do not introduce locks.
- Keep fast-path performance (single/few atomic ops).

Acceptance criteria:
- New regression tests pass.
- No other mpsc tests regress.
- Fix is localized with a comment describing the invariant.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Add test-only instrumentation to capture raw internal state at failure point
    - current (in progress task): Implement fix: align `is_empty()` with the same source-of-truth as `len()` and correct atomic ordering <-
    - upcoming (not yet): Clean up instrumentation and add invariant comments/assertions
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Implement a **localized bugfix** in Tokio `sync::mpsc` so that `Receiver::is_empty()` (and unbounded equivalent where applicable) **cannot return `false` when `len()==0`** after the receiver has drained a message. Fix must be **thread-safe**, **cross-platform**, and **fast-path friendly** (no locks, no breaking changes).

##### Technical Specs
- **Invariant to enforce (steady state after drain)**: if `len()` observes `0`, `is_empty()` must return `true` for the same receiver state.
- **Approach** (pick the smallest safe change supported by inspection/instrumentation):
  - Unify `is_empty()` to use the **same internal counter/state** as `len()`, or
  - Align **atomic load orderings** so that `is_empty()` cannot observe stale “not empty” state once a drain is visible, or
  - Fix any **bit packing / masking / wraparound** bug consistent with the “every 32 messages” artifact.
- **Performance**: keep to one/few atomic ops on the hot path; no heavy synchronization.

##### Implementation Checklist
- [ ] In the receiver implementation(s), locate `len()` and `is_empty()` and document (in-code comment near the fix) the exact internal variables they read.
- [ ] Make `is_empty()` derive emptiness from the same source-of-truth as `len()` (preferred), or ensure both use compatible ordering.
- [ ] If adjusting orderings, justify with a short comment (why the chosen ordering is sufficient and does not change intended concurrency semantics beyond removing the inconsistency).
- [ ] Ensure bounded and unbounded receivers are both addressed if they share the same flawed logic (or explicitly limit scope with code comments if unbounded differs).
- [ ] Run and keep passing all existing `sync_mpsc` tests plus the new regression test(s).

##### Success Criteria
- [ ] New regression test(s) pass reliably after fix (including on Windows).
- [ ] Existing `tokio/tests/sync_mpsc.rs` remains passing.
- [ ] Fix is localized and includes a short comment describing the invariant and the reason for the chosen source-of-truth / ordering.


### 8. Clean up instrumentation and add invariant comments/assertions (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Remove temporary logging not appropriate for long-term.

Optionally keep:
- Debug assertions under `cfg(test)` or `debug_assert!` that enforce `len()==0 => is_empty()` in the relevant post-recv state, if it does not violate concurrency expectations.
- A short comment near the empty-check logic referencing the Windows/32-msg regression and why the chosen ordering/state is correct.

Acceptance criteria:
- Codebase remains clean; no noisy logs in normal test runs.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement fix: align `is_empty()` with the same source-of-truth as `len()` and correct atomic ordering
    - current (in progress task): Clean up instrumentation and add invariant comments/assertions <-
    - upcoming (not yet): Run `sync_mpsc` tests and repeat regression to ensure stability (Windows-focused)
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Remove temporary instrumentation/logging added during investigation and keep only **minimal, maintainable invariants** (comments and optional debug assertions) to prevent regressions, without producing noisy output in normal test runs.

##### Technical Specs
- **Remove**: any unconditional `println!`, `eprintln!`, or noisy debug tracing introduced solely to reproduce the bug.
- **Keep (optional)**:
  - `debug_assert!` / `debug_assert_eq!` or `#[cfg(test)]` assertions that enforce a safe invariant such as: in the relevant post-recv state, `len()==0` implies `is_empty()==true`.
  - A concise comment near the fixed logic referencing the **Windows / 32-msg** regression and why the empty-check is implemented this way.

##### Implementation Checklist
- [ ] Delete/strip all investigation-only logs or temporary helpers that aren’t needed by the regression test failure message.
- [ ] If a snapshot helper remains, ensure it is `#[cfg(test)]` and not reachable in non-test builds.
- [ ] Add/keep a short explanatory comment next to the `is_empty()` / state-read logic documenting:
  - [ ] the previous inconsistency,
  - [ ] the chosen source-of-truth or ordering,
  - [ ] the intended invariant.
- [ ] Ensure `cargo test -p tokio --test sync_mpsc` output stays clean (no extra logs on success).

##### Success Criteria
- [ ] Codebase has no noisy logs in passing test runs.
- [ ] Any retained assertions are debug/test-only and do not change release behavior.
- [ ] Fix remains understandable via localized comments.


### 9. Run `sync_mpsc` tests and repeat regression to ensure stability (Windows-focused) (Epic: Fix Tokio mpsc `Receiver::is_empty()` inconsistency with `len()==0` on Windows (every 32 msgs))

#### Description

Execute test suite to validate correctness and guard against flakiness.

Commands (adjust to workspace layout):
- `cargo test -p tokio --test sync_mpsc`
- Run the new regression test(s) repeatedly (loop or test runner repeat) to confirm stability.

Acceptance criteria:
- All `sync_mpsc` tests pass.
- Regression test(s) pass reliably after fix, including on Windows.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Clean up instrumentation and add invariant comments/assertions
    - current (in progress task): Run `sync_mpsc` tests and repeat regression to ensure stability (Windows-focused) <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Verify stability of the fix and regression coverage by running the `sync_mpsc` test suite and repeating the new regression test(s), with emphasis on Windows reliability (non-flaky, consistent pass post-fix).

##### Execution Checklist
- [ ] Run the full test file:
  - `cargo test -p tokio --test sync_mpsc`
- [ ] Re-run the specific regression test repeatedly to guard against intermittency:
  - `cargo test -p tokio --test sync_mpsc test_is_empty_32_msgs -- --nocapture`
  - Repeat in a loop (shell loop or CI retry strategy) sufficient to build confidence (e.g., 50–200 iterations depending on runtime).
- [ ] If an unbounded regression test exists, repeat it similarly.
- [ ] Confirm no additional failures appear on non-Windows platforms (at minimum: ensure local/CI non-Windows run remains green).

##### Reporting / Verification Artifacts
- [ ] Record the command lines used and the observed stability (number of consecutive passes).
- [ ] If any flakes remain, capture the failing output (including diagnostics from the regression test) and ensure it is actionable.

##### Success Criteria
- [ ] All `sync_mpsc` tests pass.
- [ ] Regression test(s) pass reliably after fix, including on Windows (no intermittent failures across repeated runs).
