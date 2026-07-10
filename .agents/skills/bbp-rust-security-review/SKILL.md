---
name: bbp-rust-security-review
description: Audit Rust codebases for security vulnerabilities in authorized bug bounty targets. Covers unsafe code review, memory safety, concurrency bugs, dependency auditing, and common Rust security footguns.
---

# BBP Rust Security Review

## Focus Areas

### Unsafe Code
- Every `unsafe` block: verify pointer dereferences are valid, no null/dangling, no uninitialized memory.
- FFI calls: check buffer sizes, null terminators, error handling.
- Raw pointer arithmetic: no out-of-bounds, no use-after-free.

### Memory Safety
- `unwrap()` / `expect()` on untrusted input — can cause panics/DoS.
- `as` casts between integer types — truncation or sign issues.
- `transmute()` between incompatible types.
- `ManuallyDrop` / `forget()` — resource leaks.

### Concurrency
- `Mutex` / `RwLock` poisoning.
- `Send` / `Sync` impls on types with `*const T` or `*mut T`.
- Data races through interior mutability (`Cell`, `RefCell`, `UnsafeCell`) across threads.

### Common Footguns
- Path traversal in file operations.
- Command injection via `std::process::Command` with unsanitized args.
- Timing side-channels in constant-time comparisons (use `subtle` crate).
- `regex` crate ReDoS with untrusted patterns.
- `serde` deserialization of untrusted data.

### Dependency Audit
```bash
cargo audit       # known vulnerabilities
cargo deny check  # license + advisory
cargo outdated    # outdated deps
```

## File Targets

Focus on:

- `src/unsafe.rs`, any file with `#[allow(unsafe_code)]`
- `build.rs` — build script injection
- `proc-macro/` — proc macro code execution
- Cargo.toml dependency versions
- `**/ffi.rs`, `**/bindings.rs` — FFI boundaries

## Evidence

Save as:

```text
C:\BugBounty\programs\<program>\evidence\<finding>/
```

Include: source excerpt with line numbers, `cargo audit` output, unsafe block analysis.
