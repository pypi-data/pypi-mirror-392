# Usage Guide - STC v0.3.0

Complete practical guide for using Seigr Toolset Crypto v0.3.0 "Adaptive Security & Transparency" with entropy health monitoring, polymorphic decoys, streaming support, and adaptive security features.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Encryption](#basic-encryption)
3. [New Features in v0.3.0](#new-features-in-v030)
4. [Advanced Usage](#advanced-usage)
5. [Practical Examples](#practical-examples)
6. [Performance Optimization](#performance-optimization)
7. [Security Best Practices](#security-best-practices)
8. [Error Handling](#error-handling)
9. [Testing](#testing)

---

## Quick Start

### Basic Encryption with Full Security (v0.3.0)

```python
from stc import STCContext

# Initialize context with seed
ctx = STCContext('my-unique-seed')

# v0.3.0: Encrypt with ALL security features enabled by default
encrypted, metadata = ctx.encrypt(
    "Secret message",
    password="strong_password"
    # use_decoys=True (default)
    # variable_decoy_sizes=True (default)
    # randomize_decoy_count=True (default)
    # adaptive_morphing=True (default)
    # adaptive_difficulty=True (default)
)

# Decrypt with automatic MAC verification and decoy selection
try:
    decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")
    print(decrypted)  # "Secret message"
except ValueError:
    print("Wrong password or data tampered!")
```

**v0.3.0 Security Features Applied:**

- ✓ 3-7 polymorphic decoy lattices (attacker can't identify real CEL)
- ✓ Variable decoy sizes (32×3 to 96×5)
- ✓ Randomized decoy count (±2 variation)
- ✓ CEL-delta adaptive morphing (50/100/200 op intervals)
- ✓ Oracle attack detection with adaptive PHE difficulty
- ✓ Metadata compression (51% size reduction)
- ✓ MAC verification for tamper detection

### Minimal Encryption (Not Recommended)

```python
# v0.3.0: Can disable features, but NOT RECOMMENDED
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    use_decoys=False,              # Disables polymorphic obfuscation
    adaptive_morphing=False,       # Disables CEL-delta morphing
    adaptive_difficulty=False      # Disables oracle attack detection
)

# Performance: ~0.9s vs 1.8s with full security
# Security: SIGNIFICANTLY WEAKER
```

**Warning:** Only disable security features if you have specific performance requirements and understand the security implications. See [security-guide.md](security-guide.md) for threat model.

---

## Basic Encryption

### Password-Based Encryption

```python
from stc import STCContext

# Initialize context
ctx = STCContext('my-seed')

# Encrypt with password (includes MAC for tamper detection)
encrypted, metadata = ctx.encrypt(
    "Secret message",
    password="strong_password"
)

# Decrypt with password (MAC automatically verified)
try:
    decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")
    print(decrypted)  # "Secret message"
except ValueError:
    print("Wrong password or data tampered!")
```

### Binary Data Encryption

```python
# Works with bytes
binary_data = b'\x00\x01\x02\xFF\xFE\xFD'
encrypted, metadata = ctx.encrypt(binary_data, password="pw")
decrypted = ctx.decrypt(encrypted, metadata, password="pw")

assert decrypted == binary_data
```

### Custom Lattice Parameters

```python
# Smaller lattice = faster but less security
ctx = STCContext(
    seed="my-seed",
    lattice_size=64,   # Default: 128 (range: 16-256)
    depth=4,           # Default: 6 (range: 2-8)
    morph_interval=50  # Default: 100 (PCF morphing frequency)
)

# Encrypt with custom parameters
encrypted, metadata = ctx.encrypt("data", password="pw")
```

**Performance vs Security Trade-off:**

- `lattice_size=64, depth=4`: ~0.5s encryption, ~150KB metadata (fast, moderate security)
- `lattice_size=128, depth=6`: ~1.8s encryption, ~486KB metadata (balanced - **default**)
- `lattice_size=256, depth=8`: ~8s encryption, ~1.8MB metadata (slow, maximum security)

### Saving Encrypted Files

```python
import pickle

# Encrypt data
encrypted, metadata = ctx.encrypt("sensitive data", password="pw")

# Save encrypted data (binary)
with open('data.enc', 'wb') as f:
    f.write(encrypted)

# Save metadata (pickle format)
with open('data.enc.meta', 'wb') as f:
    pickle.dump(metadata, f)

print(f"Encrypted: {len(encrypted)} bytes")
print(f"Metadata: {len(pickle.dumps(metadata))} bytes (~486KB compressed)")
```

### Loading Encrypted Files

```python
import pickle

# Load files
with open('data.enc', 'rb') as f:
    encrypted = f.read()

with open('data.enc.meta', 'rb') as f:
    metadata = pickle.load(f)

# Decrypt
ctx = STCContext('my-seed')
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
```

---

## New Features in v0.3.0

### 1. Entropy Health Monitoring

Monitor CEL entropy quality to ensure encryption strength:

```python
ctx = STCContext('my-seed')

# Check entropy health
health = ctx.get_entropy_health()

print(f"Quality Score: {health['quality_score']:.2f}")  # 0.0-1.0
print(f"Status: {health['status']}")  # excellent/good/fair/poor
print(f"Unique Ratio: {health['unique_ratio']:.2f}")
print(f"Distribution: {health['distribution_score']:.2f}")
print(f"Updates: {health['update_count']}")

# Check recommendations
if health['recommendations']:
    print("\nRecommendations:")
    for rec in health['recommendations']:
        print(f"  - {rec}")

# Force update if quality is poor
if health['quality_score'] < 0.5:
    ctx.cel.update()
    print("CEL entropy refreshed!")
```

**Quality Thresholds:**

- **Excellent** (≥0.85): Ideal for encryption, no action needed
- **Good** (0.70-0.84): Acceptable for normal operation
- **Fair** (0.50-0.69): Marginal, consider updating CEL
- **Poor** (<0.50): Do not encrypt - force CEL update first

**Best Practice:**

```python
# Check health before important operations
health = ctx.get_entropy_health()
if health['quality_score'] < 0.7:
    ctx.cel.update()
    print("Entropy refreshed for optimal security")

# Now encrypt with confidence
encrypted, metadata = ctx.encrypt("critical data", password="pw")
```

### 2. Polymorphic Decoys

Decoys make it impossible for attackers to identify the real CEL:

```python
# Default configuration (recommended)
encrypted, metadata = ctx.encrypt(
    "Secret data",
    password="pw",
    use_decoys=True,              # Enable decoys
    num_decoys=3,                 # Base count (actual: 1-5 with randomization)
    variable_decoy_sizes=True,    # Random sizes: 32×3, 48×3, 64×4, 80×4, 96×5
    randomize_decoy_count=True    # Randomize count: num_decoys ± 2
)

# High security configuration
encrypted, metadata = ctx.encrypt(
    "Top secret",
    password="pw",
    num_decoys=5,                 # Base 5 decoys (actual: 3-7)
    variable_decoy_sizes=True,
    randomize_decoy_count=True
)

# Fixed configuration (for testing)
encrypted, metadata = ctx.encrypt(
    "Test data",
    password="pw",
    num_decoys=3,
    variable_decoy_sizes=False,   # All decoys 64×64×4
    randomize_decoy_count=False   # Exactly 3 decoys
)
```

**Decoy Security Properties:**

- Decoys are cryptographically indistinguishable from real CEL
- Generated using same seed derivation mechanism
- Same metadata structure and serialization format
- Trial decryption required (attacker must try all)
- Performance: 64×64×4 decoys are 5.8x faster than 128×128×6 real CEL

**Decryption Behavior:**

```python
# Decryption automatically tries all CEL snapshots
decrypted = ctx.decrypt(encrypted, metadata, password="pw")

# Internally:
# 1. Tries CEL snapshot #1 → fails
# 2. Tries CEL snapshot #2 → fails
# 3. Tries CEL snapshot #3 → SUCCESS (real CEL)
# Returns decrypted data
```

### 3. Timing Randomization (Opt-in)

Add random delays to obscure timing patterns:

```python
# Enable timing randomization (adds 0.1-1.0ms per decoy)
encrypted, metadata = ctx.encrypt(
    "High-value data",
    password="pw",
    timing_randomization=True  # Adds random delay
)

# Performance impact: ~0.5ms average per decoy
# Security benefit: Prevents timing-based CEL identification
```

**Use Case:** Extra protection against side-channel timing attacks. Only enable for high-security scenarios where slight performance penalty is acceptable.

### 4. Context-Adaptive Morphing

PCF morphing interval adapts based on CEL entropy changes:

```python
# Enabled by default
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    adaptive_morphing=True  # Default
)

# How it works:
# - High entropy change (CEL-delta < 0.3): Morph every 50 ops
# - Medium entropy change (CEL-delta 0.3-0.7): Morph every 100 ops
# - Low entropy change (CEL-delta > 0.7): Morph every 200 ops

# Disable for fixed morphing interval
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    adaptive_morphing=False  # Uses fixed morph_interval from context
)
```

**Benefit:** Optimizes security vs performance based on actual entropy evolution, not arbitrary operation count.

### 5. Adaptive Difficulty Scaling

PHE automatically increases difficulty on oracle attack detection:

```python
# Enabled by default
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    adaptive_difficulty=True  # Default
)

# How it works:
# Normal operation: 7 PHE paths
# Oracle attack detected: Scales to 15 PHE paths (2x computation)
# Detection criteria:
#   - >10 hash requests in <1 second
#   - Identical context_data with different inputs
#   - High request frequency patterns

# Disable for fixed difficulty
encrypted, metadata = ctx.encrypt(
    "Data",
    password="pw",
    adaptive_difficulty=False  # Always 7 paths
)
```

**Security Benefit:** Automatically mitigates oracle attacks without user intervention.

### 6. Streaming Encryption

Process large files without loading into memory:

```python
# Encrypt large file (e.g., 500 MB video)
def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}%", end='\r')

metadata = ctx.encrypt_stream(
    input_path="large_file.bin",
    output_path="encrypted.bin",
    password="strong_pw",
    chunk_size=1048576,  # 1 MB chunks (default)
    progress_callback=progress_callback
)

# Save metadata separately
import pickle
with open('encrypted.bin.meta', 'wb') as meta_file:
    pickle.dump(metadata, meta_file)

print("\nEncryption complete!")
```

**Streaming Decryption:**

```python
import pickle

# Load metadata
with open('encrypted.bin.meta', 'rb') as meta_file:
    metadata = pickle.load(meta_file)

# Decrypt large file
def progress_callback(current, total):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}%", end='\r')

ctx.decrypt_stream(
    input_path='encrypted.bin',
    metadata=metadata,
    output_path='decrypted.bin',
    password="strong_pw",
    chunk_size=1048576,
    progress_callback=progress_callback
)

print("\nDecryption complete!")
```

**Memory Usage:**

- Constant ~8 MB regardless of file size
- Suitable for files >1 GB
- Progress callbacks for user feedback

**Known Issue (v0.3.0):**

Streaming decrypt may fail on files >100 MB. Workaround: use standard `decrypt()` for large files. Fixed in v0.3.1.

### 7. Metadata Compression

Automatic RLE + varint compression (51% reduction):

```python
# Compression is automatic in v0.3.0
encrypted, metadata = ctx.encrypt("Data", password="pw")

# Metadata is compressed automatically
# - Original size: ~950 KB
# - Compressed size: ~486 KB
# - Decompression overhead: <10ms

# No user action required
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
# Decompression happens automatically
```

**Compression Details:**

- **RLE**: Run-length encoding for repeated values
- **Varint**: Variable-length integer encoding
- **Ratio**: Typically 51% size reduction
- **Speed**: <10ms decompression overhead
- **Compatibility**: Auto-detected on decrypt

---

## Advanced Usage

### Context Data for Key Derivation

```python
# Context data influences key generation
encrypted1, meta1 = ctx.encrypt(
    "Secret message",
    password="pw",
    context_data={"user": "alice", "session": "abc123"}
)

# Different context = different ciphertext (even with same password)
encrypted2, meta2 = ctx.encrypt(
    "Secret message",
    password="pw",
    context_data={"user": "bob", "session": "xyz789"}
)

assert encrypted1 != encrypted2

# Must use matching context for decryption
decrypted1 = ctx.decrypt(
    encrypted1,
    meta1,
    password="pw",
    context_data={"user": "alice", "session": "abc123"}
)
```

**Wrong context = decryption failure:**

```python
try:
    decrypted = ctx.decrypt(
        encrypted1,
        meta1,
        password="pw",
        context_data={"user": "bob", "session": "xyz789"}  # Wrong context!
    )
except (ValueError, Exception) as e:
    print("Context mismatch - decryption failed")
```

**Use Cases:**

- **Multi-user systems**: Include user ID in context
- **Session-based encryption**: Include session ID
- **Time-based encryption**: Include timestamp/expiry
- **Role-based access**: Include user role

### Probabilistic Hashing

```python
ctx = STCContext('hash-seed')

# Each hash is different due to CEL evolution
hash1 = ctx.hash("same data")
hash2 = ctx.hash("same data")

assert hash1 != hash2  # Non-deterministic
assert len(hash1) == 32  # 32-byte output

# With context data
hash_ctx = ctx.hash("data", context_data={'user': 'alice'})

# v0.3.0: Adaptive difficulty scales on oracle attack detection
# Normal: 7 PHE paths
# Under attack: Up to 15 PHE paths
```

**Note:** Not suitable for password hashing unless CEL state is frozen. Use for:

- Message authentication codes (with fixed CEL state)
- Data fingerprinting (with CEL evolution)
- Challenge-response protocols

### Key Derivation

```python
ctx = STCContext('my-seed')

# Derive 32-byte key (default)
key = ctx.derive_key()
assert len(key) == 32

# Derive 64-byte key
key_64 = ctx.derive_key(length=64)

# With context data
key_user = ctx.derive_key(
    length=32,
    context_data={'user': 'alice', 'purpose': 'file-encryption'}
)

# Each call produces different key (CEL evolves)
key2 = ctx.derive_key()
assert key != key2
```

### State Management

```python
ctx = STCContext('my-seed')

# Perform operations
ctx.hash("data1")
ctx.hash("data2")
encrypted, meta = ctx.encrypt("data3", password="pw")

# Save complete state
state = ctx.save_state()
print(f"State keys: {list(state.keys())}")
# ['cel_state', 'phe_state', 'pcf_state']

# Create new context and restore state
ctx2 = STCContext('my-seed')
ctx2.load_state(state)

# ctx2 now has identical state to ctx
# Same CEL, PHE, PCF state
```

**Use Cases:**

- Checkpoint long-running processes
- Synchronize state across processes
- Rollback to previous state
- Debugging and testing

---

## Practical Examples

### Password Manager with v0.3.0 Security

```python
import json
from datetime import datetime
from stc import STCContext

class SecurePasswordVault:
    def __init__(self, master_password: str):
        self.ctx = STCContext(f"vault-{master_password}")
        self.password = master_password
        self.vault = {}
    
    def store_credential(self, service: str, username: str, password: str):
        """Store credential with full v0.3.0 security"""
        credential = {
            'service': service,
            'username': username,
            'password': password,
            'created': datetime.now().isoformat()
        }
        
        credential_json = json.dumps(credential)
        
        # v0.3.0: Full security with decoys, adaptive features
        encrypted, metadata = self.ctx.encrypt(
            credential_json,
            password=self.password,
            context_data={'service': service}  # Service-specific context
        )
        
        self.vault[service] = {
            'encrypted': encrypted.hex(),
            'metadata': metadata  # Stored as dict (pickle-able)
        }
    
    def retrieve_credential(self, service: str) -> dict:
        """Retrieve and decrypt credential"""
        if service not in self.vault:
            raise ValueError(f"No credential for {service}")
        
        entry = self.vault[service]
        encrypted = bytes.fromhex(entry['encrypted'])
        metadata = entry['metadata']
        
        # Decrypt with service-specific context
        decrypted = self.ctx.decrypt(
            encrypted,
            metadata,
            password=self.password,
            context_data={'service': service}
        )
        
        return json.loads(decrypted)
    
    def save_vault(self, filepath: str):
        """Save encrypted vault to disk"""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(self.vault, f)
    
    def load_vault(self, filepath: str):
        """Load encrypted vault from disk"""
        import pickle
        with open(filepath, 'rb') as f:
            self.vault = pickle.load(f)

# Usage
vault = SecurePasswordVault("master_password_strong_123")

# Store credentials
vault.store_credential("github.com", "user@example.com", "gh_token_xyz")
vault.store_credential("aws.amazon.com", "admin", "aws_secret_key_abc")

# Retrieve credentials
github_creds = vault.retrieve_credential("github.com")
print(f"GitHub username: {github_creds['username']}")

# Save to disk
vault.save_vault("password_vault.dat")
```

### Configuration Encryption with Entropy Health

```python
import json
from stc import STCContext

class ConfigEncryptor:
    def __init__(self, config_password: str):
        self.ctx = STCContext(f"config-{config_password}")
        self.password = config_password
    
    def encrypt_config(self, config: dict, output_file: str):
        """Encrypt configuration with entropy health check"""
        # v0.3.0: Check entropy health before encrypting
        health = self.ctx.get_entropy_health()
        print(f"Entropy Health: {health['status']} ({health['quality_score']:.2f})")
        
        if health['quality_score'] < 0.7:
            print("Refreshing entropy...")
            self.ctx.cel.update()
        
        config_json = json.dumps(config, indent=2)
        
        # Encrypt with full security
        encrypted, metadata = self.ctx.encrypt(
            config_json,
            password=self.password
        )
        
        # Save encrypted config
        with open(output_file, 'wb') as f:
            f.write(encrypted)
        
        # Save metadata separately
        import pickle
        with open(f"{output_file}.meta", 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Config encrypted: {len(encrypted)} bytes")
        print(f"Metadata size: {len(pickle.dumps(metadata))} bytes (~486 KB)")
    
    def decrypt_config(self, input_file: str) -> dict:
        """Decrypt configuration with MAC verification"""
        import pickle
        
        # Load encrypted config
        with open(input_file, 'rb') as f:
            encrypted = f.read()
        
        # Load metadata
        with open(f"{input_file}.meta", 'rb') as f:
            metadata = pickle.load(f)
        
        # Decrypt with automatic MAC verification
        try:
            config_json = self.ctx.decrypt(
                encrypted,
                metadata,
                password=self.password
            )
            return json.loads(config_json)
        except ValueError as e:
            raise ValueError(f"Config decryption failed: {e}")

# Usage
config = {
    'database': {
        'host': 'db.example.com',
        'port': 5432,
        'username': 'admin',
        'password': 'db_secret_password'
    },
    'api_keys': {
        'stripe': 'sk_live_xxxxx',
        'sendgrid': 'SG.xxxxx'
    }
}

encryptor = ConfigEncryptor("config_password_123")

# Encrypt config
encryptor.encrypt_config(config, "app_config.enc")

# Decrypt config
loaded_config = encryptor.decrypt_config("app_config.enc")
print(f"Database host: {loaded_config['database']['host']}")
```

### Large File Encryption with Streaming

```python
import os
from stc import STCContext

def encrypt_large_file(input_path: str, output_path: str, password: str):
    """Encrypt large file using streaming"""
    ctx = STCContext('file-encryption-seed')
    
    file_size = os.path.getsize(input_path)
    print(f"Encrypting {file_size / 1024 / 1024:.2f} MB file...")
    
    def progress(current, total):
        percent = (current / total) * 100
        mb_current = current / 1024 / 1024
        mb_total = total / 1024 / 1024
        print(f"Progress: {percent:.1f}% ({mb_current:.2f}/{mb_total:.2f} MB)", end='\r')
    
    # Encrypt with streaming
    metadata = ctx.encrypt_stream(
        input_path=input_path,
        output_path=output_path,
        password=password,
        chunk_size=1048576,  # 1 MB chunks
        progress_callback=progress
    )
    
    # Save metadata
    import pickle
    with open(f"{output_path}.meta", 'wb') as meta_file:
        pickle.dump(metadata, meta_file)
    
    print(f"\nEncrypted: {output_path}")
    print(f"Metadata: {output_path}.meta")

def decrypt_large_file(input_path: str, output_path: str, password: str):
    """Decrypt large file using streaming"""
    import pickle
    ctx = STCContext('file-encryption-seed')
    
    # Load metadata
    with open(f"{input_path}.meta", 'rb') as meta_file:
        metadata = pickle.load(meta_file)
    
    file_size = os.path.getsize(input_path)
    print(f"Decrypting {file_size / 1024 / 1024:.2f} MB file...")
    
    def progress(current, total):
        percent = (current / total) * 100
        mb_current = current / 1024 / 1024
        mb_total = total / 1024 / 1024
        print(f"Progress: {percent:.1f}% ({mb_current:.2f}/{mb_total:.2f} MB)", end='\r')
    
    # Decrypt with streaming
    ctx.decrypt_stream(
        input_path=input_path,
        metadata=metadata,
        output_path=output_path,
        password=password,
        chunk_size=1048576,
        progress_callback=progress
    )
    
    print(f"\nDecrypted: {output_path}")

# Usage
encrypt_large_file('video.mp4', 'video.mp4.enc', 'strong_password')
decrypt_large_file('video.mp4.enc', 'video_decrypted.mp4', 'strong_password')
```

---

## Performance Optimization

### Reuse Contexts

```python
# ❌ Slow - recreates CEL each time (expensive!)
for item in items:
    ctx = STCContext('same-seed')  # Don't do this!
    encrypted, meta = ctx.encrypt(item, password="pw")

# ✅ Fast - reuse context
ctx = STCContext('same-seed')  # Once
for item in items:
    encrypted, meta = ctx.encrypt(item, password="pw")
```

**Performance Impact:** 10-100x faster when reusing context.

### Monitor Entropy Health

```python
# Check health periodically
ctx = STCContext('my-seed')
operations = 0

for item in items:
    # Check every 100 operations
    if operations % 100 == 0:
        health = ctx.get_entropy_health()
        if health['quality_score'] < 0.7:
            ctx.cel.update()
    
    encrypted, meta = ctx.encrypt(item, password="pw")
    operations += 1
```

### Batch Encryption

```python
# ❌ High overhead - one metadata per item (~486 KB each)
for item in items:
    enc, meta = ctx.encrypt(item, password="pw")
    # Total metadata: 486 KB × len(items)

# ✅ Lower overhead - one metadata for all
import json
batch = json.dumps(items)
encrypted, metadata = ctx.encrypt(batch, password="pw")
# Total metadata: 486 KB (constant)

# Decrypt and unpack
decrypted_batch = ctx.decrypt(encrypted, metadata, password="pw")
items_restored = json.loads(decrypted_batch)
```

### Choose Appropriate Parameters

```python
# For non-critical data (logs, temporary files)
ctx_fast = STCContext('seed', lattice_size=64, depth=4)
# ~0.5s encryption, ~150 KB metadata

# For normal data (documents, images)
ctx_normal = STCContext('seed')  # Default: 128×128×6
# ~1.8s encryption, ~486 KB metadata

# For critical data (passwords, keys, financial)
ctx_secure = STCContext('seed', lattice_size=256, depth=8)
# ~8s encryption, ~1.8 MB metadata
```

### Use Streaming for Large Files

```python
# ❌ Memory exhaustion for large files
with open('large_file.bin', 'rb') as f:
    data = f.read()  # Loads entire file into memory!
encrypted, metadata = ctx.encrypt(data, password="pw")

# ✅ Constant memory usage with streaming
metadata = ctx.encrypt_stream(
    input_path='large_file.bin',
    output_path='encrypted.bin',
    password="pw"
)
# Memory usage: ~8 MB (constant)
```

---

## Security Best Practices

### 1. Always Use Strong Passwords

```python
# ✅ Good - high-entropy password
import getpass
password = getpass.getpass("Enter master password: ")
ctx = STCContext('unique-seed')
encrypted, metadata = ctx.encrypt(data, password=password)

# ❌ Bad - weak password
encrypted, metadata = ctx.encrypt(data, password="password123")

# ❌ Bad - hardcoded password in source
PASSWORD = "secret"  # Never do this!
```

### 2. Use Unique Seeds

```python
# ✅ Good - unique per user/application
import getpass
username = getpass.getuser()
ctx = STCContext(f"app-v1-{username}")

# ✅ Good - user-provided seed
seed = getpass.getpass("Enter encryption seed: ")
ctx = STCContext(seed)

# ❌ Bad - generic seed
ctx = STCContext("default")  # Same for all users!
```

### 3. Monitor Entropy Health

```python
# ✅ Good - check health regularly
health = ctx.get_entropy_health()
if health['quality_score'] < 0.7:
    ctx.cel.update()

encrypted, metadata = ctx.encrypt(data, password=pw)

# ❌ Bad - never check health
encrypted, metadata = ctx.encrypt(data, password=pw)
# May encrypt with poor entropy!
```

### 4. Use Context Data

```python
# ✅ Good - add context for additional security
import time
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    context_data={
        'user_id': user_id,
        'timestamp': int(time.time()),
        'purpose': 'file_encryption'
    }
)

# ❌ Bad - no context data
encrypted, metadata = ctx.encrypt(data, password=pw)
```

### 5. Enable All Security Features

```python
# ✅ Good - full security (default in v0.3.0)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw
    # use_decoys=True (default)
    # adaptive_morphing=True (default)
    # adaptive_difficulty=True (default)
)

# ❌ Bad - disabled security features
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    use_decoys=False,
    adaptive_morphing=False,
    adaptive_difficulty=False
)
```

### 6. Protect Metadata

```python
# Metadata contains CEL state - protect it!

# ✅ Good - same protection as encrypted data
import os
os.chmod("data.enc", 0o600)
os.chmod("data.enc.meta", 0o600)

# ❌ Bad - world-readable metadata
os.chmod("data.enc.meta", 0o644)  # Attacker can analyze CEL patterns
```

### 7. Don't Log Sensitive Data

```python
# ✅ Good - log encrypted data only
encrypted, metadata = ctx.encrypt(password, password=master_pw)
print(f"Encrypted {len(encrypted)} bytes")  # Safe

# ❌ Bad - log plaintext
print(f"Encrypting password: {password}")  # Never log plaintext!

# ✅ Good - mask sensitive fields
username = "alice@example.com"
masked = username[0] + '*' * 8 + username[-1]
print(f"User: {masked}")  # Shows "a********m"
```

---

## Error Handling

### Common Errors and Solutions

**1. Wrong Password:**

```python
try:
    decrypted = ctx.decrypt(encrypted, metadata, password="wrong_password")
except ValueError as e:
    if "MAC verification failed" in str(e):
        print("Wrong password or data tampered!")
    else:
        print(f"Decryption error: {e}")
```

**2. Poor Entropy Quality:**

```python
try:
    encrypted, metadata = ctx.encrypt("data", password="pw")
except ValueError as e:
    if "Entropy quality too low" in str(e):
        print("CEL entropy insufficient!")
        ctx.cel.update()
        # Try again
        encrypted, metadata = ctx.encrypt("data", password="pw")
```

**3. Corrupted Data:**

```python
try:
    decrypted = ctx.decrypt(corrupted_data, metadata, password="pw")
except Exception as e:
    print(f"Data corruption detected: {e}")
    # Check data integrity, restore from backup
```

**4. Context Mismatch:**

```python
# Encrypted with context
encrypted, metadata = ctx.encrypt(
    "data",
    password="pw",
    context_data={'user': 'alice'}
)

# Decrypt without context - will fail
try:
    decrypted = ctx.decrypt(encrypted, metadata, password="pw")
    # May produce garbage or raise exception
except:
    print("Context data required for decryption!")

# Correct: use matching context
decrypted = ctx.decrypt(
    encrypted,
    metadata,
    password="pw",
    context_data={'user': 'alice'}
)
```

---

## Testing

### Round-Trip Test

```python
def test_encryption_roundtrip():
    """Verify encryption/decryption works correctly"""
    ctx = STCContext('test-seed')
    
    test_data = "test message"
    password = "test_password"
    
    # Encrypt
    encrypted, metadata = ctx.encrypt(test_data, password=password)
    
    # Verify encrypted data differs
    assert encrypted != test_data.encode()
    assert len(metadata) > 0
    
    # Decrypt
    decrypted = ctx.decrypt(encrypted, metadata, password=password)
    
    # Verify round-trip
    assert decrypted == test_data
    
    print("✓ Round-trip test passed")

test_encryption_roundtrip()
```

### Test Different Data Types

```python
test_cases = [
    ("simple", "simple text"),
    ("unicode", "Hello 世界 🌍"),
    ("binary", b'\x00\xFF\xFE\xFD'),
    ("large", "x" * 100000),
    ("empty", ""),
]

ctx = STCContext('test-seed')

for name, data in test_cases:
    encrypted, metadata = ctx.encrypt(data, password="pw")
    decrypted = ctx.decrypt(encrypted, metadata, password="pw")
    assert decrypted == data
    print(f"✓ {name}: {len(str(data))} bytes")
```

### Test Entropy Health

```python
def test_entropy_health():
    """Verify entropy health monitoring works"""
    ctx = STCContext('test-seed')
    
    # Initial health
    health = ctx.get_entropy_health()
    assert 'quality_score' in health
    assert 0.0 <= health['quality_score'] <= 1.0
    assert health['status'] in ['excellent', 'good', 'fair', 'poor']
    
    print(f"✓ Initial health: {health['status']} ({health['quality_score']:.2f})")
    
    # Update and check again
    ctx.cel.update()
    health2 = ctx.get_entropy_health()
    assert health2['update_count'] > health['update_count']
    
    print(f"✓ After update: {health2['status']} ({health2['quality_score']:.2f})")

test_entropy_health()
```

---

## See Also

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Architecture](architecture.md)** - System design details
- **[Security Guide](security-guide.md)** - Threat model and best practices
- **[User Manual](user_manual/)** - Beginner-friendly guides
- **[Migration Guide](migration-guide.md)** - Upgrade from v0.2.x
- **[Core Modules](core-modules.md)** - Technical specifications
- **[Examples](../examples/)** - Working code examples
