# Plan Name: Debug Redis CSV Task - Locate and Analyze

## Tasks

### 1. Locate BZMPOP implementation and current key-extraction path (Epic: Fix BZMPOP key-argument detection so blocking/unblocking ignores non-key args)

#### Description

In the checked-out `redis/redis` sources, locate:
- The `bzmpop` command definition (command table/commands metadata).
- The implementation function(s) (often in `src/t_zset.c`), and any shared helper used for blocking pops.
- Where keys are extracted/registered for: (a) command key tracking (getkeys/key-spec) and (b) blocked client wakeups.

Acceptance:
- Identify the exact functions/files to edit for (1) argument parsing and (2) key-spec/getkeys.
- Note the current (buggy) behavior: which argv positions are mistakenly treated as keys and why.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Locate BZMPOP implementation and current key-extraction path <-
    - upcoming (not yet): Fix BZMPOP parsing: build keys list from NUMKEYS only
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Locate the BZMPOP implementation and trace the current key-extraction path(s) that lead to the bug (non-key arguments being treated as keys for blocking/unblocking and/or key tracking).

##### Technical Specs
- Repo: `redis/redis`
- Scope: Source inspection + written findings (no behavior changes in this task)
- Output: A short, concrete “map” of files/functions responsible for:
  1) `bzmpop` argument parsing & blocking registration
  2) key extraction for introspection/key tracking (`COMMAND GETKEYS` / key-spec / getkeys_proc)

##### Implementation Checklist
- [ ] Locate the command definition for `bzmpop`:
  - Find where command metadata is declared (commonly `src/commands.def`, generated command table sources, or equivalent for this Redis version).
  - Record the command’s declared arity, flags (blocking, etc.), and any key-spec / getkeys hooks.
- [ ] Locate the runtime implementation:
  - Find the function that executes `bzmpop` (often in `src/t_zset.c`, but verify).
  - Identify any shared helpers used by blocking pops (e.g., a generic “blocking pop” helper used by list/zset variants).
- [ ] Trace key extraction for two separate concerns and record call paths:
  1) **Key tracking/introspection**: where `COMMAND GETKEYS` (or the internal equivalent) derives key positions for `bzmpop`.
  2) **Blocked client registration / wakeup**: where the server registers the blocked client on keys and later matches writes to wake it.
- [ ] Document the buggy behavior precisely:
  - Identify which argv indices/arguments are currently being included as keys and why (e.g., “all args after position X are treated as keys” or “range-based key-spec includes options/tokens”).
  - Tie the bug to the failing scenario: tokens/values such as `timeout=0`, `numkeys=1/2`, `MIN/MAX`, `COUNT`, and `COUNT <n>` being misinterpreted as keys.

##### Success Criteria
- [ ] Provide an explicit list of the **exact files and functions** that must be edited for:
  - (a) fixing parsing / building the “keys list” used for blocking/lookup
  - (b) fixing key-spec/getkeys so only real keys are returned
- [ ] Provide a concise description of the **current incorrect key-identification rule** (what range/spec is used today) and how it results in registering/waiting on non-key arguments.
- [ ] Findings are specific enough that another engineer can implement tasks (3) and (4) without additional discovery work.

##### Notes / Constraints
- Do not change protocol replies or behavior in this task; this is discovery-only.
- Assume Redis version differences; prefer recording “what exists in this checkout” over relying on upstream knowledge.

---


### 2. Fix BZMPOP key-argument detection so blocking/unblocking ignores non-key args

#### Description

BZMPOP currently registers/waits on non-key arguments (timeout, numkeys, MIN/MAX, COUNT and COUNT value), which can cause blocked clients to be unblocked by writes to keys named like those tokens ("0", "1", "min", "max", "count", "10"). Update BZMPOP parsing + getkeys/key-tracking so only the real key arguments (the NUMKEYS keys) are considered for blocking/unblocking and command key extraction.

Definition of done:
- New test `tests/unit/type/zset.tcl` "BZMPOP should not blocks on non key arguments - #10762" passes.
- Full unit test suite remains green.
- No protocol reply changes; behavior for BZPOP/BZMPOP/BZ[M]POP remains correct (incl. keyspace notifications and blocked client wakeups only on real keys).


### 3. Fix BZMPOP parsing: build keys list from NUMKEYS only (Epic: Fix BZMPOP key-argument detection so blocking/unblocking ignores non-key args)

#### Description

Modify the BZMPOP command parsing so that the list of keys used for blocking/lookup is *exactly* the `numkeys` arguments after `timeout` and `numkeys`.

Must hold:
- `timeout` (argv[1]) and `numkeys` (argv[2]) are never treated as keys.
- `MIN`/`MAX` token is never treated as a key.
- Optional `COUNT` token and its numeric value are never treated as keys.

Acceptance:
- With the new zset.tcl test, creating keys named "0", "1", "min", "max", "count", "10" does not wake blocked clients.
- Existing BZ*/blocking pop behavior remains unchanged for real keys.

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Locate BZMPOP implementation and current key-extraction path
    - current (in progress task): Fix BZMPOP parsing: build keys list from NUMKEYS only <-
    - upcoming (not yet): Fix BZMPOP key-spec/getkeys: expose only real keys for key tracking
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Fix `BZMPOP` parsing so the list of keys used for blocking/lookup is built from **exactly** the `numkeys` key arguments, and never from non-key arguments (`timeout`, `numkeys`, `MIN/MAX`, `COUNT`, `COUNT value`).

##### Technical Specs
- Area: `BZMPOP` runtime parsing and the construction of the key list used to:
  - (a) look up keys for pop attempts
  - (b) register blocked clients on keys
- Required invariant:
  - Keys considered for blocking/unblocking must be **only** the `numkeys` keys starting at `argv[3]` (i.e., immediately after `timeout` and `numkeys`), and exactly `numkeys` long.

##### Implementation Checklist
- [ ] Identify where `bzmpop` parses its arguments and/or constructs an array/list of keys for subsequent operations.
- [ ] Update parsing logic to:
  - [ ] Treat `argv[1]` (`timeout`) as a scalar only; never add to keys list.
  - [ ] Treat `argv[2]` (`numkeys`) as a scalar only; never add to keys list.
  - [ ] Build `keys = argv[3 .. 3+numkeys-1]` and use this keys list consistently for:
    - initial immediate pop attempt(s)
    - blocked-client registration
  - [ ] Parse `MIN`/`MAX` token *after* the keys section; ensure it is never placed into any key array / key registration.
  - [ ] Parse optional `COUNT <n>` *after* `MIN/MAX`; ensure neither `COUNT` nor its numeric value is ever placed into any key array / key registration.
- [ ] Validate argument bounds carefully:
  - [ ] Ensure the implementation rejects malformed requests (e.g., not enough args for `numkeys`, missing `MIN/MAX`, `COUNT` without value) using existing Redis-style error replies (no new reply text; reuse existing patterns).
  - [ ] Ensure `numkeys` influences only the key segment length, not any option parsing.
- [ ] Confirm blocked-client registration uses the corrected key list:
  - [ ] Locate the point where the client is set to blocked state and associated with keys.
  - [ ] Ensure the key list passed/registered is precisely the derived `numkeys` keys.

##### Success Criteria
- [ ] The new test `tests/unit/type/zset.tcl` “BZMPOP should not blocks on non key arguments - #10762” passes:
  - Creating keys named `"0"`, `"1"`, `"min"`, `"max"`, `"count"`, `"10"` does **not** wake blocked `bzmpop` clients.
  - Writes to the real zset keys **do** wake the blocked clients and return the expected key/value.
- [ ] Existing blocking pop behavior for real keys (BZPOPMIN/BZPOPMAX/BZMPOP family) remains unchanged.
- [ ] No protocol reply changes (RESP2/RESP3) compared to baseline behavior for valid/invalid inputs.

##### Dependencies
- Discovery from task (2): exact functions/files to edit.

---


### 4. Fix BZMPOP key-spec/getkeys: expose only real keys for key tracking (Epic: Fix BZMPOP key-argument detection so blocking/unblocking ignores non-key args)

#### Description

Update the command key extraction mechanism used by Redis for key tracking/introspection so that only the `numkeys` key arguments are returned.

Depending on Redis version, this may mean updating:
- `commands.def`/command metadata key-spec (variable-length based on `numkeys`), or
- a per-command `getkeys_proc` implementation.

Acceptance:
- `COMMAND GETKEYS` for `bzmpop` (or internal equivalent) returns only the `numkeys` keys, not tokens/options.
- Blocked-client key registration relies on those same real keys (no spurious keys).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Fix BZMPOP parsing: build keys list from NUMKEYS only
    - current (in progress task): Fix BZMPOP key-spec/getkeys: expose only real keys for key tracking <-
    - upcoming (not yet): Run regression + targeted Redis tests and confirm no behavior regressions
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Fix `BZMPOP` key-spec / getkeys so key extraction for key tracking and introspection returns **only** the `numkeys` real keys and never includes non-key args or option tokens/values.

##### Technical Specs
- Goal: `COMMAND GETKEYS bzmpop ...` (or the internal key extraction path used by Redis) must output only the key arguments: the `numkeys` keys following `timeout` and `numkeys`.
- Implementation must match this repo’s mechanism:
  - Either update command metadata key-spec (variable-length dependent on `numkeys`)
  - Or implement/fix a per-command `getkeys_proc`

##### Implementation Checklist
- [ ] Determine current key extraction mechanism for `bzmpop` in this checkout:
  - [ ] If metadata-driven: locate `bzmpop` entry in command definitions and its key-spec fields (begin/last/step or more complex specs).
  - [ ] If function-driven: locate `getkeys_proc` (or equivalent) for `bzmpop`.
- [ ] Update key extraction to match the true key grammar:
  - `BZMPOP timeout numkeys key [key ...] <MIN|MAX> [COUNT count]`
  - Keys returned must be: `argv[3 .. 3+numkeys-1]`
- [ ] Ensure the key extractor does not “overrun” into:
  - `MIN` / `MAX`
  - `COUNT`
  - `count` value
  - Any other trailing arguments
- [ ] Confirm the corrected getkeys result is used consistently:
  - [ ] Verify blocked-client key registration relies on the same “real keys” set (directly or indirectly via shared helpers).
  - [ ] Ensure no spurious keys are registered for tracking, notifications, or blocking.

##### Success Criteria
- [ ] `COMMAND GETKEYS` (or equivalent introspection tool available in this checkout) for `bzmpop` returns only the `numkeys` keys, not tokens/options.
- [ ] Writes to keys named like non-key tokens/values (e.g., `"0"`, `"1"`, `"min"`, `"max"`, `"count"`, `"10"`) do not cause blocked `bzmpop` clients to be woken due to incorrect key registration.
- [ ] No change to protocol replies for `bzmpop`; this is strictly correcting key identification.

##### Dependencies
- Task (2) findings: where key-spec or getkeys_proc is defined for `bzmpop`.
- Task (3) may be complementary; ensure both paths (runtime blocking + introspection) agree on key positions.

---


### 5. Run regression + targeted Redis tests and confirm no behavior regressions (Epic: Fix BZMPOP key-argument detection so blocking/unblocking ignores non-key args)

#### Description

Run the new regression test and relevant existing tests.

Acceptance:
- `tests/unit/type/zset.tcl` includes and passes: "BZMPOP should not blocks on non key arguments - #10762".
- Existing tests for BZMPOP/BZPOPMIN/BZPOPMAX/related blocking semantics remain green.
- No protocol reply changes were introduced (RESP2/RESP3 outputs unchanged).

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Fix BZMPOP key-spec/getkeys: expose only real keys for key tracking
    - current (in progress task): Run regression + targeted Redis tests and confirm no behavior regressions <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Run the new regression test and relevant Redis tests, confirm the fix is correct, and verify no regressions or protocol reply changes were introduced.

##### Technical Specs
- Test framework: Redis TCL test suite
- Primary new test: `tests/unit/type/zset.tcl` — “BZMPOP should not blocks on non key arguments - #10762”
- Focus areas: blocked client wakeups, zset blocking pops, key tracking/getkeys correctness, protocol output stability (RESP2/RESP3)

##### Implementation Checklist
- [ ] Run the targeted new regression test (as supported by this repo’s test runner conventions):
  - [ ] Ensure the test is discovered and executed.
  - [ ] Capture output logs sufficient to diagnose failures (if any).
- [ ] Run a focused subset of related tests:
  - [ ] zset unit tests (including other BZPOPMIN/BZPOPMAX/BZMPOP coverage)
  - [ ] blocking semantics tests (if present separately)
- [ ] Run full unit test suite (or the standard CI-equivalent suite for this repo) to confirm no unrelated breakage.
- [ ] Verify protocol reply stability:
  - [ ] Ensure no changes in reply shape/content for RESP2/RESP3 for BZMPOP/BZPOPMIN/BZPOPMAX in both success and error paths.
  - [ ] Confirm only the key-selection behavior changed (i.e., elimination of spurious key registration), not the command’s public output.

##### Success Criteria
- [ ] The new test “BZMPOP should not blocks on non key arguments - #10762” passes reliably.
- [ ] Existing tests for BZMPOP/BZPOPMIN/BZPOPMAX and related blocking behavior remain green.
- [ ] No protocol reply changes observed (RESP2/RESP3 outputs unchanged for equivalent inputs), confirmed via test expectations and/or rigorous diff-based review of relevant code paths.
