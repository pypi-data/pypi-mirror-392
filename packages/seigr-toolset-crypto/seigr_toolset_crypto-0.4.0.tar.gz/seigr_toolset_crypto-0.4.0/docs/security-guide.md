# Security Guide - STC v0.3.0

Comprehensive security guide for Seigr Toolset Crypto v0.3.0 "Adaptive Security & Transparency" covering threat model, best practices, known limitations, and security recommendations.

## Table of Contents

1. [Threat Model](#threat-model)
2. [Security Features](#security-features)
3. [Best Practices](#best-practices)
4. [Known Limitations](#known-limitations)
5. [Attack Mitigation](#attack-mitigation)
6. [Security Checklist](#security-checklist)
7. [Incident Response](#incident-response)

---

## Threat Model

### What STC Protects Against

✅ **Confidentiality Attacks**:

- **Passive eavesdropping**: Encrypted data reveals no plaintext
- **Ciphertext-only attacks**: Strong CEL entropy prevents pattern analysis
- **Known-plaintext attacks**: CEL state + context prevent key derivation
- **Chosen-plaintext attacks**: Polymorphic decoys prevent CEL identification

✅ **Integrity Attacks**:

- **Data tampering**: MAC verification detects modifications
- **Bit-flip attacks**: CEL-dependent encryption cascades changes
- **Replay attacks**: Context data can include timestamps
- **Metadata manipulation**: Encrypted metadata prevents analysis

✅ **Availability Attacks**:

- **Oracle attacks**: Adaptive difficulty scaling increases cost
- **Timing attacks**: Optional timing randomization
- **Memory exhaustion**: Streaming support for large files

### What STC Assumes

⚠️ **Attacker Capabilities** (Kerckhoffs's Principle):

- **Has access to**: Ciphertext, metadata, algorithm source code
- **Can attempt**: Trial decryption, timing analysis, statistical analysis
- **May perform**: Oracle attacks, chosen-plaintext attacks

⚠️ **Attacker Does NOT Have**:

- **Password**: Must remain secret (user responsibility)
- **Context data**: Must be kept confidential
- **Timing oracle**: perf_counter entropy is unpredictable
- **Quantum computer**: Current implementation vulnerable to Shor's algorithm

### Security Goals

1. **Confidentiality**: Data unreadable without password + context
2. **Integrity**: Tampering detected via MAC verification
3. **Authenticity**: Password verifies authorized decryption
4. **Forward security**: Old ciphertexts remain secure if password changed
5. **Obfuscation**: Decoys prevent CEL state identification

---

## Security Features

### 1. Entropy Health Monitoring (v0.3.0)

**Purpose**: Prevent encryption with poor-quality entropy

**How It Works**:

```python
health = ctx.get_entropy_health()
if health['quality_score'] < 0.5:
    raise ValueError("Entropy quality too low - cannot encrypt safely")
```

**Security Benefit**:

- Prevents weak encryption from degraded CEL state
- Forces entropy refresh before critical operations
- Provides early warning of entropy quality issues

**Recommended Thresholds**:

- **Critical data** (passwords, keys): quality ≥ 0.85
- **Normal data** (documents, files): quality ≥ 0.70
- **Non-sensitive data** (logs, cache): quality ≥ 0.50

### 2. Polymorphic Decoy Obfuscation (v0.3.0)

**Purpose**: Prevent attacker from identifying real CEL

**How It Works**:

- Generate 3-7 decoy CEL lattices alongside real CEL
- Variable sizes (32×3 to 96×5) prevent size-based identification
- Randomized count (±2) prevents pattern recognition
- Cryptographically indistinguishable from real CEL

**Security Benefit**:

- Attacker must try all CEL snapshots (trial decryption)
- No way to determine which is real without password
- Increases attack computational cost by factor of (num_decoys + 1)

**Attack Resistance**:

```text
Without decoys:
- Attacker tries 1 CEL → immediate feedback
- Success: Decrypt works
- Failure: Wrong password

With 3 decoys (4 total snapshots):
- Attacker tries 4 CELs → must try all before determining failure
- Average trials: 2.5 per attempt
- Success: Decrypt works (but which CEL was real?)
- Failure: Wrong password OR wrong CEL (no way to tell)
```

### 3. Context-Adaptive Morphing (v0.3.0)

**Purpose**: Adapt algorithm behavior based on entropy evolution

**How It Works**:

- PCF monitors CEL entropy delta
- High change (Δ < 0.3) → frequent morphing (50 ops)
- Medium change (Δ 0.3-0.7) → normal morphing (100 ops)
- Low change (Δ > 0.7) → infrequent morphing (200 ops)

**Security Benefit**:

- Prevents predictable algorithm behavior
- Optimizes security based on actual entropy quality
- Reduces attack surface for pattern analysis

### 4. Adaptive Difficulty Scaling (v0.3.0)

**Purpose**: Mitigate oracle attacks on PHE

**How It Works**:

```python
# Normal operation
num_paths = 7  # ~50ms hash time

# Oracle attack detected
num_paths = 15  # ~100ms hash time (2x cost)
timing_jitter = random.uniform(0.0001, 0.001)  # Random delay
```

**Detection Criteria**:

- >10 hash requests in <1 second
- Identical context_data with different inputs
- High request frequency patterns

**Security Benefit**:

- Makes oracle attacks computationally expensive
- Prevents PHE state enumeration
- Automatic without user intervention

### 5. Message Authentication Code (MAC)

**Purpose**: Detect tampering and verify password

**How It Works**:

```python
# During encryption
phe_hash = phe.digest(plaintext + password + context)
metadata['phe_hash'] = phe_hash

# During decryption
expected_hash = phe.digest(decrypted + password + context)
if expected_hash != metadata['phe_hash']:
    raise ValueError("MAC verification failed")
```

**Security Benefit**:

- Detects any modification to ciphertext or metadata
- Verifies password correctness
- Prevents unauthorized decryption

### 6. Metadata Compression (v0.3.0)

**Purpose**: Reduce metadata size without leaking information

**How It Works**:

- RLE + varint compression on CEL lattice data
- 51% size reduction (950 KB → 465 KB)
- No plaintext leakage from compression patterns

**Security Benefit**:

- Smaller metadata = less storage/transmission overhead
- Compression based on numeric patterns, not plaintext
- Decompression overhead minimal (<10ms)

---

## Best Practices

### Password Management

✅ **DO**:

```python
# High-entropy passwords
import secrets
password = secrets.token_urlsafe(32)  # 256-bit entropy

# User-provided passwords with entropy check
import getpass
password = getpass.getpass("Enter master password: ")
if len(password) < 12:
    print("Password too short - use at least 12 characters")

# Password strengthening
import hashlib
strengthened = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode(),
    b'salt',
    100000
).hex()
```

❌ **DON'T**:

```python
# Hardcoded passwords
PASSWORD = "password123"  # NEVER

# Weak passwords
password = "1234"  # Too short

# Passwords in source code
encrypted, metadata = ctx.encrypt(data, password="secret")  # Exposed

# Logged passwords
print(f"Password: {password}")  # NEVER log
```

### Seed Selection

✅ **DO**:

```python
# User-specific seeds
import getpass
username = getpass.getuser()
ctx = STCContext(f"app-v1-{username}-{device_id}")

# High-entropy seeds
import secrets
seed = secrets.token_bytes(32)
ctx = STCContext(seed)

# Derived seeds
import hashlib
seed = hashlib.sha256(b"master-seed" + user_id.encode()).digest()
ctx = STCContext(seed)
```

❌ **DON'T**:

```python
# Generic seeds
ctx = STCContext("default")  # Same for all users!

# Low-entropy seeds
import random
seed = str(random.randint(0, 999))  # Only 1000 possibilities

# Predictable seeds
import time
seed = str(int(time.time()))  # Attackable with timestamp knowledge
```

### Context Data Usage

✅ **DO**:

```python
# Include user identity
context_data = {
    'user_id': user_id,
    'session': session_id,
    'timestamp': int(time.time())
}

# Include purpose
context_data = {
    'purpose': 'file_encryption',
    'file_path': '/path/to/file',
    'version': 'v1.0'
}

# Include expiration
context_data = {
    'expires': int(time.time()) + 86400,  # 24 hours
    'created': int(time.time())
}
```

❌ **DON'T**:

```python
# No context data (weaker security)
encrypted, metadata = ctx.encrypt(data, password=pw)  # context_data=None

# Static context (no uniqueness)
context_data = {'app': 'myapp'}  # Same for all operations

# Sensitive data in context (logged/stored)
context_data = {'password': user_password}  # Never!
```

### Entropy Health Monitoring

✅ **DO**:

```python
# Check health before critical operations
health = ctx.get_entropy_health()
if health['quality_score'] < 0.7:
    ctx.cel.update()
    print("Entropy refreshed")

encrypted, metadata = ctx.encrypt(critical_data, password=pw)

# Periodic health checks
operations = 0
for item in items:
    if operations % 100 == 0:
        health = ctx.get_entropy_health()
        if health['status'] == 'poor':
            ctx.cel.update()
    
    encrypted, metadata = ctx.encrypt(item, password=pw)
    operations += 1

# Enforce minimum quality
MIN_QUALITY = 0.85  # For high-security operations
health = ctx.get_entropy_health()
if health['quality_score'] < MIN_QUALITY:
    raise SecurityError("Insufficient entropy quality")
```

❌ **DON'T**:

```python
# Never check health (risky)
encrypted, metadata = ctx.encrypt(data, password=pw)  # May use poor entropy

# Ignore warnings
health = ctx.get_entropy_health()
# Proceed anyway even if poor
encrypted, metadata = ctx.encrypt(data, password=pw)
```

### Metadata Protection

✅ **DO**:

```python
# Protect metadata as carefully as ciphertext
import os
os.chmod("data.enc", 0o600)
os.chmod("data.enc.meta", 0o600)

# Store metadata securely
with open("data.enc.meta", 'wb') as f:
    f.write(metadata)
os.chmod("data.enc.meta", 0o600)

# Separate storage
# Store metadata in different location from ciphertext
metadata_storage = "/secure/metadata/location/"
ciphertext_storage = "/data/location/"
```

❌ **DON'T**:

```python
# World-readable metadata
os.chmod("data.enc.meta", 0o644)  # Attacker can analyze CEL patterns

# Store metadata in plaintext database
db.execute("INSERT INTO metadata VALUES (?)", (metadata,))  # Exposed

# Send metadata over unencrypted channel
requests.post("http://example.com/api", data=metadata)  # Use HTTPS!
```

### Data Sanitization

✅ **DO**:

```python
# Mask sensitive output
username = "alice@example.com"
masked = username[0] + '*' * 8 + username[-1]
print(f"User: {masked}")  # Shows "a********m"

# Log encrypted data only
encrypted, metadata = ctx.encrypt(password, password=master_pw)
print(f"Encrypted {len(encrypted)} bytes")  # Safe

# Clear sensitive variables
sensitive_data = "secret"
encrypted, metadata = ctx.encrypt(sensitive_data, password=pw)
sensitive_data = None  # Clear reference
del sensitive_data
```

❌ **DON'T**:

```python
# Log plaintext
print(f"Encrypting password: {password}")  # NEVER

# Debug print sensitive data
print(f"Debug: {decrypted}")  # Exposed in logs

# Store plaintext longer than needed
plaintext = decrypt(encrypted, metadata, password=pw)
# ... long processing ...
# plaintext still in memory
```

### Enable All Security Features

✅ **DO**:

```python
# Full security (v0.3.0 defaults)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw
    # use_decoys=True (default)
    # variable_decoy_sizes=True (default)
    # randomize_decoy_count=True (default)
    # adaptive_morphing=True (default)
    # adaptive_difficulty=True (default)
)

# High-security configuration
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    num_decoys=5,  # More decoys
    timing_randomization=True,  # Timing obfuscation
    context_data=context  # Additional context
)
```

❌ **DON'T**:

```python
# Disable security features (weak!)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    use_decoys=False,  # No obfuscation
    adaptive_morphing=False,  # Predictable behavior
    adaptive_difficulty=False  # Vulnerable to oracle attacks
)
```

---

## Known Limitations

### 1. CEL Snapshot Exposure

**Issue**: Metadata contains full CEL state (necessary for decryption)

**Impact**: Attacker with metadata sees CEL lattice values

**Mitigation**:

- Protect metadata as carefully as ciphertext
- Use polymorphic decoys (attacker can't tell which is real)
- Consider encrypting metadata with separate key (future enhancement)

**Risk Level**: Medium (mitigated by decoys in v0.3.0)

### 2. Context Data Management

**Issue**: context_data must be managed separately and kept secret

**Impact**: Wrong or exposed context → decryption failure or security breach

**Mitigation**:

- Store context data securely (encrypted or in secure vault)
- Use predictable context patterns (user_id, timestamp, purpose)
- Document context requirements clearly

**Risk Level**: Medium (user responsibility)

### 3. No Forward Secrecy

**Issue**: Same password + context_data + CEL state → same keys

**Impact**: Compromised password reveals all past ciphertexts

**Mitigation**:

- Rotate passwords regularly
- Include timestamps in context_data
- Re-encrypt critical data periodically

**Risk Level**: Medium (standard for symmetric encryption)

### 4. Timing Side Channels

**Issue**: `perf_counter()` timing may leak information on some systems

**Impact**: Attacker with precise timing access may infer CEL updates

**Mitigation**:

- Enable timing_randomization for high-security scenarios
- Run on dedicated hardware (minimize timing interference)
- Use constant-time operations where possible (future enhancement)

**Risk Level**: Low (requires local access + precise timing)

### 5. Not Quantum-Resistant

**Issue**: Uses modular arithmetic vulnerable to Shor's algorithm

**Impact**: Quantum computer with sufficient qubits can break encryption

**Mitigation**:

- Monitor quantum computing developments
- Plan migration to post-quantum algorithms
- Use quantum-resistant algorithms for long-term storage (e.g., Kyber, NTRU)

**Risk Level**: Low (no practical quantum threat currently)

### 6. Streaming Decrypt Issue (v0.3.0)

**Issue**: Streaming decryption may fail on files >100 MB

**Impact**: Large file decryption requires fallback to standard decrypt()

**Mitigation**:

- Use standard decrypt() for files >100 MB
- Fixed in v0.3.1 (planned)

**Risk Level**: Low (workaround available)

### 7. Thread Safety

**Issue**: CEL, PHE, PCF not thread-safe

**Impact**: Concurrent access causes race conditions

**Mitigation**:

- Use separate STCContext per thread
- Implement external locking for shared contexts
- Use thread-local storage

**Risk Level**: Medium (common issue, easy to mitigate)

---

## Attack Mitigation

### Oracle Attacks on PHE

**Attack**: Attacker sends many hash requests to enumerate PHE state

**Detection**:

- >10 requests per second
- Identical context_data with different inputs
- High request frequency patterns

**Mitigation**:

```python
# Automatic in v0.3.0
# PHE scales from 7 → 15 paths on attack detection
# Timing jitter adds 0.1-1.0ms random delay
# Cooldown after attack stops
```

**Manual Mitigation**:

```python
# Rate limiting
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=10, window=1.0):
        self.requests = defaultdict(list)
        self.max_requests = max_requests
        self.window = window
    
    def check(self, client_id):
        now = time.time()
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            raise SecurityError("Rate limit exceeded")
        
        self.requests[client_id].append(now)

limiter = RateLimiter()
limiter.check(client_id)
hash_value = ctx.hash(data)
```

### Timing Attacks

**Attack**: Attacker measures decryption time to infer correctness

**Detection**: Unusual timing measurement patterns

**Mitigation**:

```python
# Enable timing randomization
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    timing_randomization=True  # Adds random delay
)

# Constant-time comparison for MAC
import hmac

def constant_time_compare(a, b):
    """Constant-time comparison to prevent timing attacks"""
    return hmac.compare_digest(a, b)

# Use in decryption
if not constant_time_compare(computed_mac, stored_mac):
    raise ValueError("MAC verification failed")
```

### Brute Force Attacks

**Attack**: Attacker tries all possible passwords

**Detection**: High decryption attempt frequency

**Mitigation**:

```python
# Use strong passwords (high entropy)
import secrets
password = secrets.token_urlsafe(32)  # 256-bit entropy

# Password strengthening with PBKDF2
import hashlib

def strengthen_password(password, salt=b'salt', iterations=100000):
    """Strengthen password with key derivation"""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        iterations
    ).hex()

strong_pw = strengthen_password("user_password")
encrypted, metadata = ctx.encrypt(data, password=strong_pw)

# Implement attempt limiting
class DecryptionLimiter:
    def __init__(self, max_attempts=3, lockout_time=300):
        self.attempts = defaultdict(int)
        self.lockout_until = defaultdict(float)
        self.max_attempts = max_attempts
        self.lockout_time = lockout_time
    
    def check(self, resource_id):
        now = time.time()
        
        # Check if locked out
        if now < self.lockout_until[resource_id]:
            raise SecurityError("Account locked due to too many failed attempts")
        
        # Check attempt count
        if self.attempts[resource_id] >= self.max_attempts:
            self.lockout_until[resource_id] = now + self.lockout_time
            raise SecurityError("Too many failed attempts - locked out")
    
    def record_failure(self, resource_id):
        self.attempts[resource_id] += 1
    
    def record_success(self, resource_id):
        self.attempts[resource_id] = 0
        self.lockout_until[resource_id] = 0

limiter = DecryptionLimiter()
try:
    limiter.check(resource_id)
    decrypted = ctx.decrypt(encrypted, metadata, password=pw)
    limiter.record_success(resource_id)
except ValueError:
    limiter.record_failure(resource_id)
    raise
```

### Replay Attacks

**Attack**: Attacker reuses old ciphertext + metadata

**Detection**: Timestamp validation, nonce checking

**Mitigation**:

```python
# Include timestamp in context
import time

context_data = {
    'timestamp': int(time.time()),
    'nonce': secrets.token_hex(16),
    'user_id': user_id
}

encrypted, metadata = ctx.encrypt(data, password=pw, context_data=context_data)

# Validate on decryption
def decrypt_with_expiry(encrypted, metadata, password, max_age=86400):
    """Decrypt with timestamp validation"""
    # Extract context from metadata (implementation-specific)
    timestamp = extract_timestamp(metadata)
    
    if time.time() - timestamp > max_age:
        raise SecurityError("Ciphertext expired")
    
    return ctx.decrypt(encrypted, metadata, password=password, context_data=context_data)
```

---

## Security Checklist

### Development Phase

- [ ] Use high-entropy passwords (≥128 bits)
- [ ] Never hardcode passwords or seeds in source code
- [ ] Implement password strengthening (PBKDF2/Argon2)
- [ ] Use context_data for all operations
- [ ] Enable all security features (decoys, adaptive features)
- [ ] Implement entropy health monitoring
- [ ] Protect metadata as carefully as ciphertext
- [ ] Use streaming for large files (>100 MB)
- [ ] Implement proper error handling (no info leakage)
- [ ] Clear sensitive data from memory after use

### Deployment Phase

- [ ] Store metadata securely (file permissions, encryption)
- [ ] Use HTTPS for metadata/ciphertext transmission
- [ ] Implement rate limiting for PHE operations
- [ ] Set up monitoring for attack patterns
- [ ] Configure appropriate lattice sizes for security needs
- [ ] Document context_data requirements
- [ ] Plan password rotation schedule
- [ ] Implement backup and recovery procedures
- [ ] Set up security logging (without sensitive data)
- [ ] Test disaster recovery procedures

### Operational Phase

- [ ] Monitor entropy health regularly
- [ ] Rotate passwords on schedule
- [ ] Update to latest STC version
- [ ] Review security logs for anomalies
- [ ] Perform periodic security audits
- [ ] Re-encrypt critical data periodically
- [ ] Test decryption procedures regularly
- [ ] Maintain secure backup of metadata
- [ ] Document security incidents
- [ ] Keep dependencies updated

---

## Incident Response

### Suspected Password Compromise

**Actions**:

1. **Immediate**:
   - Rotate compromised password immediately
   - Re-encrypt all data with new password
   - Audit access logs for unauthorized access
   - Invalidate old ciphertexts (if possible)

2. **Investigation**:
   - Determine compromise source
   - Identify affected data
   - Check for unauthorized decryptions
   - Review security logs

3. **Recovery**:
   - Generate new high-entropy password
   - Re-encrypt all sensitive data
   - Update password across all systems
   - Document incident

### Metadata Exposure

**Actions**:

1. **Immediate**:
   - Assess exposure scope (which CEL snapshots?)
   - Determine if password also compromised
   - If decoys enabled: Impact mitigated
   - If no decoys: Rotate immediately

2. **Investigation**:
   - Review metadata content
   - Check for pattern analysis attempts
   - Determine if real CEL identifiable
   - Assess context_data exposure

3. **Recovery**:
   - Re-encrypt with new context_data
   - Enable decoys if not already enabled
   - Consider increasing num_decoys
   - Implement stricter metadata protection

### Oracle Attack Detected

**Actions**:

1. **Immediate**:
   - Adaptive difficulty automatically increases (v0.3.0)
   - Rate limit attacker (if identifiable)
   - Monitor PHE request patterns
   - Log attack details

2. **Investigation**:
   - Identify attack source
   - Analyze request patterns
   - Determine if successful
   - Check for data exfiltration

3. **Recovery**:
   - Block attacker if identified
   - Increase base PHE difficulty
   - Enable timing_randomization
   - Review and strengthen defenses

### Data Integrity Failure

**Actions**:

1. **Immediate**:
   - Do not attempt to decrypt (may be ransomware)
   - Identify affected files
   - Restore from backup if available
   - Isolate corrupted data

2. **Investigation**:
   - Determine cause (tampering vs corruption)
   - Check MAC verification details
   - Review storage integrity
   - Assess damage scope

3. **Recovery**:
   - Restore from known-good backup
   - Verify backup integrity
   - Strengthen integrity checks
   - Document incident

---

## Security Contact

For security issues or vulnerabilities in STC:

- **GitHub Issues**: [Seigr-lab/SeigrToolsetCrypto/issues](https://github.com/Seigr-lab/SeigrToolsetCrypto/issues)
- **Security Policy**: See SECURITY.md (if available)
- **Responsible Disclosure**: Please disclose responsibly

**Do not**:

- Post sensitive security details publicly
- Exploit vulnerabilities against production systems
- Share vulnerabilities before patch available

---

## See Also

- **[Architecture](architecture.md)** - Security architecture details
- **[API Reference](api-reference.md)** - Security-related API calls
- **[Usage Guide](usage-guide.md)** - Secure usage patterns
- **[User Manual](user_manual/)** - Security for beginners
- **[Migration Guide](migration-guide.md)** - Security improvements in v0.3.0
