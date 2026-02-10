# Plan Name: Locate and Plan Bug Fix for Tokio CSV Task

## Tasks

### 1. Implement UnwindSafe and RefUnwindSafe for UdpSocket (Epic: Fix UnwindSafe/RefUnwindSafe trait implementation for tokio network types)

#### Description

Add explicit trait implementations for std::panic::UnwindSafe and std::panic::RefUnwindSafe to tokio::net::UdpSocket.

**File to modify**: tokio/src/net/udp.rs

**Implementation**:
```rust
impl std::panic::UnwindSafe for UdpSocket {}
impl std::panic::RefUnwindSafe for UdpSocket {}
```

Add these impl blocks near the UdpSocket struct definition, following the pattern used by other tokio network types. This is safe because UdpSocket's invariants are maintained even if a panic occurs during operations.

**Testing**: The net_types_are_unwind_safe test should pass after this change, specifically the line `is_unwind_safe::<tokio::net::UdpSocket>();`

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): N/A
    - current (in progress task): Implement UnwindSafe and RefUnwindSafe for UdpSocket <-
    - upcoming (not yet): Implement UnwindSafe and RefUnwindSafe for UnixStream
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add UnwindSafe and RefUnwindSafe trait implementations to UdpSocket to enable panic-safe usage patterns.

##### Technical Specs:
- **File to modify**: `tokio/src/net/udp.rs`
- **Implementation**: Add two empty trait implementations near the UdpSocket struct definition
- **Trait bounds**: `std::panic::UnwindSafe` and `std::panic::RefUnwindSafe`
- **Safety justification**: UdpSocket's invariants remain valid even if a panic occurs during operations

##### Implementation Checklist:
- [ ] Locate the UdpSocket struct definition in tokio/src/net/udp.rs
- [ ] Add `impl std::panic::UnwindSafe for UdpSocket {}`
- [ ] Add `impl std::panic::RefUnwindSafe for UdpSocket {}`
- [ ] Place implementations near the struct definition, following conventions used by other tokio network types (TcpListener, TcpStream, etc.)
- [ ] Verify formatting matches project style

##### Success Criteria:
- [ ] Code compiles without warnings
- [ ] The `net_types_are_unwind_safe` test passes (specifically `is_unwind_safe::<tokio::net::UdpSocket>();`)
- [ ] Implementation matches the pattern used by other tokio network types
- [ ] No functional changes to UdpSocket behavior

##### Dependencies:
- Test file creation (ticket #4) should be completed first to verify the fix

---


### 2. Fix UnwindSafe/RefUnwindSafe trait implementation for tokio network types

#### Description

Fix the bug where tokio::net::UdpSocket and tokio::net::UnixStream cannot be used with std::panic::catch_unwind because they don't implement UnwindSafe and RefUnwindSafe traits. This blocks panic-safe code patterns. The fix involves adding explicit trait implementations following the pattern used by other tokio network types (TcpListener, TcpStream, etc.) that already pass the unwind safety tests.

**Root Cause**: UnsafeCell<AtomicUsize> within Arc<UdpSocket> doesn't implement RefUnwindSafe, which prevents the outer types from being UnwindSafe.

**Approach**: Add explicit impl blocks for std::panic::UnwindSafe and std::panic::RefUnwindSafe for both UdpSocket and UnixStream.

**Success Criteria**: Tests net_types_are_unwind_safe and unix_net_types_are_unwind_safe pass in the new test file tokio/tests/net_types_unwind.rs


### 3. Implement UnwindSafe and RefUnwindSafe for UnixStream (Epic: Fix UnwindSafe/RefUnwindSafe trait implementation for tokio network types)

#### Description

Add explicit trait implementations for std::panic::UnwindSafe and std::panic::RefUnwindSafe to tokio::net::UnixStream.

**File to modify**: tokio/src/net/unix/stream.rs

**Implementation**:
```rust
impl std::panic::UnwindSafe for UnixStream {}
impl std::panic::RefUnwindSafe for UnixStream {}
```

Add these impl blocks near the UnixStream struct definition. This implementation is Unix-specific (controlled by #[cfg(unix)] attribute in the parent module).

**Testing**: The unix_net_types_are_unwind_safe test should pass after this change, specifically the line `is_unwind_safe::<tokio::net::UnixStream>();`

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement UnwindSafe and RefUnwindSafe for UdpSocket
    - current (in progress task): Implement UnwindSafe and RefUnwindSafe for UnixStream <-
    - upcoming (not yet): Create test file for network type unwind safety
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Add UnwindSafe and RefUnwindSafe trait implementations to UnixStream to enable panic-safe usage patterns on Unix platforms.

##### Technical Specs:
- **File to modify**: `tokio/src/net/unix/stream.rs`
- **Implementation**: Add two empty trait implementations near the UnixStream struct definition
- **Trait bounds**: `std::panic::UnwindSafe` and `std::panic::RefUnwindSafe`
- **Platform-specific**: Unix-only (parent module already has #[cfg(unix)] attribute)
- **Safety justification**: UnixStream's invariants remain valid even if a panic occurs during operations

##### Implementation Checklist:
- [ ] Locate the UnixStream struct definition in tokio/src/net/unix/stream.rs
- [ ] Add `impl std::panic::UnwindSafe for UnixStream {}`
- [ ] Add `impl std::panic::RefUnwindSafe for UnixStream {}`
- [ ] Place implementations near the struct definition, following conventions used by other tokio network types
- [ ] Verify no additional #[cfg(unix)] attributes are needed (parent module already handles this)
- [ ] Verify formatting matches project style

##### Success Criteria:
- [ ] Code compiles without warnings on Unix platforms
- [ ] The `unix_net_types_are_unwind_safe` test passes (specifically `is_unwind_safe::<tokio::net::UnixStream>();`)
- [ ] Implementation matches the pattern used by other tokio network types
- [ ] No functional changes to UnixStream behavior

##### Dependencies:
- Test file creation (ticket #4) should be completed first to verify the fix

---


### 4. Create test file for network type unwind safety (Epic: Fix UnwindSafe/RefUnwindSafe trait implementation for tokio network types)

#### Description

Create a new test file to verify that tokio network types implement UnwindSafe and RefUnwindSafe traits correctly.

**File to create**: tokio/tests/net_types_unwind.rs

**Content**: The test file should include:
1. Proper test attributes: #![warn(rust_2018_idioms)] and #![cfg(feature = "full")]
2. Import statements: use std::panic::{RefUnwindSafe, UnwindSafe};
3. Test function `net_types_are_unwind_safe` - tests TcpListener, TcpSocket, TcpStream, and UdpSocket
4. Test function `unix_net_types_are_unwind_safe` with #[cfg(unix)] - tests UnixDatagram, UnixListener, and UnixStream
5. Test function `windows_net_types_are_unwind_safe` with #[cfg(windows)] - tests NamedPipeClient and NamedPipeServer
6. Helper function `is_unwind_safe<T: UnwindSafe + RefUnwindSafe>()` that enforces trait bounds

See the full test file content in the bug report context. This test file serves as both verification and regression prevention.

**Expected outcome**: 
- FAIL_TO_PASS: net_types_are_unwind_safe, unix_net_types_are_unwind_safe
- All tests should pass after the trait implementations are added

#### Prompt

<general>
These instructions are for a task that is part of a larger plan:
    <plan>
    - previous (completed): Implement UnwindSafe and RefUnwindSafe for UnixStream
    - current (in progress task): Create test file for network type unwind safety <-
    - upcoming (not yet): N/A
    </plan>
Within reason, stick to only the deliverables outlined in these instructions,
don't do extra work, and instead assume anything not mentioned is out of scope.
</general>

Create a comprehensive test file to verify UnwindSafe and RefUnwindSafe trait implementations for all tokio network types, serving as both immediate verification and regression prevention.

##### Technical Specs:
- **File to create**: `tokio/tests/net_types_unwind.rs`
- **Test framework**: Standard Rust test harness
- **Platform coverage**: Tests for Unix and Windows-specific types with appropriate cfg attributes
- **Helper function**: Generic `is_unwind_safe<T: UnwindSafe + RefUnwindSafe>()` to enforce trait bounds

##### Implementation Checklist:
- [ ] Create new file at `tokio/tests/net_types_unwind.rs`
- [ ] Add file-level attributes: `#![warn(rust_2018_idioms)]` and `#![cfg(feature = "full")]`
- [ ] Import necessary types: `use std::panic::{RefUnwindSafe, UnwindSafe};`
- [ ] Implement `net_types_are_unwind_safe` test function covering TcpListener, TcpSocket, TcpStream, and UdpSocket
- [ ] Implement `unix_net_types_are_unwind_safe` test with `#[cfg(unix)]` covering UnixDatagram, UnixListener, and UnixStream
- [ ] Implement `windows_net_types_are_unwind_safe` test with `#[cfg(windows)]` covering NamedPipeClient and NamedPipeServer
- [ ] Implement helper function `is_unwind_safe<T: UnwindSafe + RefUnwindSafe>()`
- [ ] Verify test file matches the exact specification from the bug report context

##### Success Criteria:
- [ ] File compiles successfully with feature flag "full"
- [ ] Initially: `net_types_are_unwind_safe` FAILS on UdpSocket check (expected failure)
- [ ] Initially: `unix_net_types_are_unwind_safe` FAILS on UnixStream check (expected failure)
- [ ] After trait implementations (tickets #2, #3): ALL tests PASS
- [ ] TcpListener, TcpSocket, TcpStream tests pass immediately (already implement traits)
- [ ] Test file serves as regression prevention for future changes

##### Files to read:
- Bug report context for exact test file specification
