# Rust Security Review — Deep Workflows

Companion to SKILL.md. unsafe auditing, panic hunting, dependency audit.

## Step 1: Dependency audit first

```bash
cargo install cargo-audit cargo-deny 2>/dev/null
cargo audit                          # RUSTSEC advisory DB match
cargo deny check advisories bans licenses sources
cargo tree -d                        # duplicate versions (divergent types!)
```

## Step 2: unsafe block census

```bash
rg -n "unsafe" --type rust -g '!target' | wc -l
# Focus order:
rg -n "unsafe \{|unsafe fn|unsafe impl|mem::transmute|\*const |\*mut " src/
# For each site answer: which invariant does safe Rust rely on us to hold?
```

```text
Common real bugs:
- transmute between differently-sized/lifetime'd types -> UB
- raw pointer deref without provenance guarantee after move
- FFI boundary: C string not NUL-terminated, struct layout mismatch
- Send/Sync unsafe impl for non-threadsafe type -> data race
```

## Step 3: Panic & overflow hunting

```bash
rg -n "\.unwrap\(|\.expect\(|panic!|unreachable!|assert!" src/ | grep -v test
# Arithmetic: release builds WRAP silently unless checked:
rg -n "[a-z_]\s*\+|\*|<<" src/ | rg "as u(8|16|32)|usize"   # cast-heavy spots
# Indexing slices with attacker-controlled index panics -> DoS in services.
```

## Step 4: Crypto & randomness misuse

```bash
rg -n "rand::thread_rng|OsRng|rand\(0\.\." src/
# Non-crypto RNG (SmallRng, Pcg) used for tokens/nonces = finding.
rg -n "block_padding|Aes.*ECB|des\(|md5|sha1" src/
```

## Step 5: Deserialization & parser surfaces

```bash
rg -n "serde_yaml::from_|serde_json::from_|bincode::deserialize|from_str" src/
# Untrusted input into recursive formats -> stack exhaustion DoS.
rg -n "std::fs::|File::open|PathBuf::from" src/ | rg "user|request|param"
# Path traversal joins on user paths.
```

## Step 6: Async pitfalls

```text
- Blocking calls inside async fn (reqwest::blocking, std::fs heavy IO)
  stall the executor -> trivial DoS under concurrency.
- tokio::spawn of !Send futures / holding std Mutex across await ->
  deadlock or race; note reachable-from-request ones only.
```

## False-positive elimination

1. unsafe != vulnerability: prove the violated invariant + reachable path.
2. unwrap in startup-only code (config parse at boot) is not a finding.
3. Advisory hits need version verification against Cargo.lock actual.

Report template: assets/report-template.md.
