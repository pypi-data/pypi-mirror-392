# Migration Guide - v0.2.x to v0.3.0

Comprehensive guide for upgrading from STC v0.2.x to v0.3.0 "Adaptive Security & Transparency", including breaking changes, new features, compatibility notes, and upgrade procedures.

## Table of Contents

1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [New Features](#new-features)
4. [API Changes](#api-changes)
5. [Upgrade Steps](#upgrade-steps)
6. [Compatibility](#compatibility)
7. [Migration Examples](#migration-examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What's New in v0.3.0

**v0.3.0 "Adaptive Security & Transparency"** introduces:

1. **Entropy Health API**: Real-time CEL quality monitoring
2. **Polymorphic Decoy Obfuscation**: Variable-size decoys prevent pattern analysis
3. **Context-Adaptive Morphing**: CEL-delta-driven interval adjustment
4. **Adaptive Difficulty Scaling**: Automatic oracle attack mitigation
5. **Streaming Support**: encrypt_stream/decrypt_stream for large files
6. **Metadata Compression**: RLE + varint encoding (51% reduction)

### Compatibility Summary

✅ **Backward Compatible**:

- Standard encrypt/decrypt API (unchanged parameters)
- Decryption works for v0.2.x ciphertexts
- Metadata format readable (with decompression)
- Core algorithm behavior preserved

⚠️ **Optional Breaking Changes**:

- New parameters (all optional with defaults)
- Metadata size reduced (decoys add size if enabled)
- Streaming API new (fallback to standard methods)

❌ **Not Compatible**:

- v0.3.0 ciphertexts cannot be decrypted by v0.2.x (new metadata fields)

### Should You Upgrade?

**Upgrade if**:

- ✅ Need entropy quality monitoring
- ✅ Want polymorphic decoy obfuscation
- ✅ Require large file streaming (>100 MB)
- ✅ Concerned about oracle attacks
- ✅ Want automatic security enhancements

**Stay on v0.2.x if**:

- ⚠️ Need v0.2.x decryption compatibility (temporary)
- ⚠️ Extremely resource-constrained (v0.3.0 uses slightly more memory)

---

## Breaking Changes

### 1. Metadata Format

**Change**: Metadata now includes compressed CEL snapshots and new fields

**Impact**: v0.2.x cannot decrypt v0.3.0 ciphertexts

**Before (v0.2.x)**:

```python
metadata = {
    'cel_snapshot': [...],  # Uncompressed
    'phe_hash': b'...',
    'state_snapshot': {...}
}
```

**After (v0.3.0)**:

```python
metadata = {
    'cel_snapshot': [...],  # RLE + varint compressed
    'decoy_snapshots': [...],  # NEW: Polymorphic decoys
    'phe_hash': b'...',
    'state_snapshot': {...},  # Compressed
    'entropy_delta': 0.123,  # NEW: For adaptive morphing
    'version': '0.3.0'  # NEW: Version tracking
}
```

**Migration**:

- Re-encrypt data to upgrade metadata format
- Keep v0.2.x installation for decrypting old files temporarily

### 2. Decoy Behavior

**Change**: Decoys enabled by default in v0.3.0

**Impact**: Metadata size increases if not explicitly disabled

**Before (v0.2.x)**:

```python
# No decoys by default
encrypted, metadata = ctx.encrypt(data, password=pw)
# Metadata: ~950 KB
```

**After (v0.3.0)**:

```python
# Decoys enabled by default
encrypted, metadata = ctx.encrypt(data, password=pw)
# Metadata: ~1,500 KB (with 3 decoys)

# Disable if needed (NOT recommended)
encrypted, metadata = ctx.encrypt(data, password=pw, use_decoys=False)
# Metadata: ~465 KB (compressed)
```

**Migration**:

- Accept increased metadata size (worth security benefit)
- Adjust storage allocation accordingly
- Consider compression if metadata size critical

### 3. Streaming API Limitations

**Change**: Streaming decryption may fail for files >100 MB

**Impact**: Must use fallback for large file decryption

**Before (v0.2.x)**:

```python
# Standard decrypt only
decrypted = ctx.decrypt(encrypted, metadata, password=pw)
```

**After (v0.3.0)**:

```python
# Streaming encrypt works
ctx.encrypt_stream(
    input_path="large_file.bin",
    output_path="large_file.enc",
    password=pw
)

# Streaming decrypt may fail >100 MB
try:
    ctx.decrypt_stream(
        input_path="large_file.enc",
        metadata=metadata,
        output_path="large_file.bin",
        password=pw
    )
except Exception:
    # Fallback to standard decrypt
    with open("large_file.enc", 'rb') as f:
        encrypted = f.read()
    decrypted = ctx.decrypt(encrypted, metadata, password=pw)
    with open("large_file.bin", 'wb') as f:
        f.write(decrypted)
```

**Migration**:

- Use streaming for encryption (works reliably)
- Implement fallback for decryption failures
- Fixed in planned v0.3.1

### 4. PHE Adaptive Difficulty

**Change**: PHE automatically scales difficulty on attack detection

**Impact**: Hash operations may become slower under load

**Before (v0.2.x)**:

```python
# Constant 7 paths (~50ms)
hash_value = ctx.hash(data)
```

**After (v0.3.0)**:

```python
# 7 paths normally (~50ms)
hash_value = ctx.hash(data)

# 15 paths if oracle attack detected (~100ms)
# Automatic - no code change needed
```

**Migration**:

- No code changes required
- Monitor hash performance under high load
- Consider implementing request rate limiting

---

## New Features

### 1. Entropy Health Monitoring

**Purpose**: Monitor CEL quality before critical operations

**Usage**:

```python
# Get entropy health report
health = ctx.get_entropy_health()

print(f"Quality Score: {health['quality_score']:.2f}")  # 0.0-1.0
print(f"Status: {health['status']}")  # excellent/good/fair/poor
print(f"Recommendations: {health['recommendations']}")

# Enforce quality threshold
if health['quality_score'] < 0.7:
    print("Warning: Low entropy quality")
    ctx.cel.update()  # Refresh entropy
```

**Migration**:

- Add health checks before critical encryptions
- Implement periodic health monitoring
- Set quality thresholds based on security needs

### 2. Polymorphic Decoy Obfuscation

**Purpose**: Prevent attackers from identifying real CEL

**Usage**:

```python
# Full polymorphism (default)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    num_decoys=3,  # Default
    variable_decoy_sizes=True,  # Default
    randomize_decoy_count=True  # Default: 3±2 = 1-5 decoys
)

# High security configuration
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    num_decoys=5,  # More decoys
    variable_decoy_sizes=True,
    randomize_decoy_count=True
)

# Disable (NOT recommended)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    use_decoys=False
)
```

**Migration**:

- Accept defaults for standard security
- Increase num_decoys for high-security scenarios
- Monitor metadata size increase

### 3. Context-Adaptive Morphing

**Purpose**: Adjust morphing intervals based on entropy evolution

**Usage**:

```python
# Enable adaptive morphing (default)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    adaptive_morphing=True  # Default
)

# Morphing intervals adjust automatically:
# High CEL change (Δ < 0.3) → 50 ops
# Medium change (Δ 0.3-0.7) → 100 ops
# Low change (Δ > 0.7) → 200 ops
```

**Migration**:

- Enable by default (already enabled)
- No code changes needed
- Provides automatic security optimization

### 4. Streaming Encryption/Decryption

**Purpose**: Encrypt/decrypt large files without loading into memory

**Usage**:

```python
# Streaming encryption (recommended for >10 MB files)
metadata = ctx.encrypt_stream(
    input_path="large_file.bin",
    output_path="large_file.enc",
    password=pw,
    context_data=context,
    progress_callback=lambda b, t: print(f"{b}/{t} bytes")
)

# Streaming decryption (with fallback)
try:
    ctx.decrypt_stream(
        input_path="large_file.enc",
        metadata=metadata,
        output_path="large_file.bin",
        password=pw,
        context_data=context,
        progress_callback=lambda b, t: print(f"{b}/{t} bytes")
    )
except Exception as e:
    # Fallback for large files
    with open("large_file.enc", 'rb') as f:
        encrypted = f.read()
    decrypted = ctx.decrypt(encrypted, metadata, password=pw, context_data=context)
    with open("large_file.bin", 'wb') as f:
        f.write(decrypted)
```

**Migration**:

- Replace large file encryption with encrypt_stream
- Implement fallback for decrypt_stream failures
- Monitor memory usage (constant 8 MB with streaming)

### 5. Metadata Compression

**Purpose**: Reduce metadata size

**Usage**:

```python
# Automatic compression (no code changes)
encrypted, metadata = ctx.encrypt(data, password=pw)
# Metadata automatically compressed with RLE + varint

# Size comparison:
# v0.2.x: ~950 KB uncompressed
# v0.3.0: ~465 KB compressed (51% reduction)
# v0.3.0 + 3 decoys: ~1,500 KB (still smaller per snapshot)
```

**Migration**:

- No code changes needed
- Compression automatic
- Decompression transparent

---

## API Changes

### STCContext Constructor

**New Parameters**: None (fully compatible)

```python
# v0.2.x and v0.3.0 (identical)
ctx = STCContext(seed="my-seed")
```

### encrypt() Method

**New Parameters** (all optional with defaults):

```python
# v0.2.x
encrypted, metadata = ctx.encrypt(data, password=pw, context_data=context)

# v0.3.0 (backward compatible + new options)
encrypted, metadata = ctx.encrypt(
    data,
    password=pw,
    context_data=context,
    # NEW optional parameters:
    use_decoys=True,  # NEW: Enable decoy obfuscation
    num_decoys=3,  # NEW: Number of decoys (if use_decoys=True)
    variable_decoy_sizes=True,  # NEW: Randomize decoy sizes
    randomize_decoy_count=True,  # NEW: Randomize num_decoys ±2
    timing_randomization=False,  # NEW: Add timing jitter
    adaptive_morphing=True,  # NEW: CEL-delta-driven intervals
    adaptive_difficulty=True  # NEW: Oracle attack mitigation
)
```

**Migration**:

- No changes needed (defaults preserve v0.2.x behavior + enhancements)
- Explicitly set use_decoys=False to match v0.2.x exactly (not recommended)

### decrypt() Method

**Changes**: Automatic decoy selection (no API changes)

```python
# v0.2.x and v0.3.0 (identical)
decrypted = ctx.decrypt(encrypted, metadata, password=pw, context_data=context)

# v0.3.0 automatically:
# 1. Tries real CEL first
# 2. Falls back to decoys if decryption fails
# 3. Returns decrypted data (transparent)
```

**Migration**:

- No changes needed
- Decoy selection automatic

### New Methods

**encrypt_stream()** (NEW in v0.3.0):

```python
metadata = ctx.encrypt_stream(
    input_path="file.bin",
    output_path="file.enc",
    password=pw,
    context_data=context,
    chunk_size=1024*1024,  # 1 MB chunks
    progress_callback=None,  # Optional: (bytes_processed, total_size) -> None
    # All encrypt() parameters also supported
    use_decoys=True,
    num_decoys=3,
    # ...
)
```

**decrypt_stream()** (NEW in v0.3.0):

```python
ctx.decrypt_stream(
    input_path="file.enc",
    metadata=metadata,
    output_path="file.bin",
    password=pw,
    context_data=context,
    chunk_size=1024*1024,  # 1 MB chunks
    progress_callback=None  # Optional: (bytes_processed, total_size) -> None
)
```

**get_entropy_health()** (NEW in v0.3.0):

```python
health = ctx.get_entropy_health()
# Returns:
# {
#     'quality_score': 0.85,  # 0.0-1.0
#     'status': 'excellent',  # excellent/good/fair/poor
#     'recommendations': ['No action needed']
# }
```

---

## Upgrade Steps

### 1. Install v0.3.0

```bash
pip install --upgrade seigr-toolset-crypto
```

**Verify Installation**:

```python
import stc
print(stc.__version__)  # Should be 0.3.0
```

### 2. Update Code (Optional)

**Minimal Changes** (accept defaults):

```python
# v0.2.x code
from stc import STCContext

ctx = STCContext("my-seed")
encrypted, metadata = ctx.encrypt(data, password=pw)
decrypted = ctx.decrypt(encrypted, metadata, password=pw)

# v0.3.0 code (IDENTICAL - defaults provide enhancements)
from stc import STCContext

ctx = STCContext("my-seed")
encrypted, metadata = ctx.encrypt(data, password=pw)  # Now with decoys + adaptive features
decrypted = ctx.decrypt(encrypted, metadata, password=pw)  # Automatic decoy selection
```

**Recommended Changes** (use new features):

```python
from stc import STCContext

ctx = STCContext("my-seed")

# Add entropy health check
health = ctx.get_entropy_health()
if health['quality_score'] < 0.7:
    ctx.cel.update()

# Use streaming for large files
if file_size > 10 * 1024 * 1024:  # >10 MB
    metadata = ctx.encrypt_stream(
        input_path=input_file,
        output_path=output_file,
        password=pw,
        progress_callback=lambda b, t: print(f"Progress: {b/t*100:.1f}%")
    )
else:
    encrypted, metadata = ctx.encrypt(data, password=pw)
```

### 3. Re-encrypt Critical Data (Optional)

**Why**: Upgrade to compressed metadata + decoy obfuscation

**Procedure**:

```python
import os
from stc import STCContext

# v0.2.x decryption
ctx_old = STCContext("my-seed")
with open("data.enc", 'rb') as f:
    encrypted_old = f.read()
with open("data.enc.meta", 'rb') as f:
    metadata_old = pickle.load(f)

decrypted = ctx_old.decrypt(encrypted_old, metadata_old, password=pw)

# v0.3.0 re-encryption
ctx_new = STCContext("my-seed")
encrypted_new, metadata_new = ctx_new.encrypt(
    decrypted,
    password=pw,
    num_decoys=3,  # Enable decoys
    adaptive_morphing=True,
    adaptive_difficulty=True
)

# Save with v0.3.0 format
with open("data_v3.enc", 'wb') as f:
    f.write(encrypted_new)
with open("data_v3.enc.meta", 'wb') as f:
    pickle.dump(metadata_new, f)

# Clean up old files (AFTER VERIFICATION)
os.remove("data.enc")
os.remove("data.enc.meta")
```

### 4. Test Thoroughly

**Test Cases**:

```python
# Test 1: Basic encryption/decryption
encrypted, metadata = ctx.encrypt(b"test data", password="test")
decrypted = ctx.decrypt(encrypted, metadata, password="test")
assert decrypted == b"test data"

# Test 2: Context data
context = {'user': 'alice', 'timestamp': 12345}
encrypted, metadata = ctx.encrypt(b"test", password="pw", context_data=context)
decrypted = ctx.decrypt(encrypted, metadata, password="pw", context_data=context)
assert decrypted == b"test"

# Test 3: Decoys
encrypted, metadata = ctx.encrypt(b"test", password="pw", num_decoys=5)
assert 'decoy_snapshots' in metadata
assert len(metadata['decoy_snapshots']) >= 3  # 5±2 = 3-7
decrypted = ctx.decrypt(encrypted, metadata, password="pw")
assert decrypted == b"test"

# Test 4: Streaming
import tempfile
import os

with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(b"large data" * 1000000)
    input_file = f.name

output_file = input_file + ".enc"
decrypted_file = input_file + ".dec"

# Encrypt
metadata = ctx.encrypt_stream(input_file, output_file, password="pw")

# Decrypt
try:
    ctx.decrypt_stream(output_file, metadata, decrypted_file, password="pw")
except Exception:
    # Fallback
    with open(output_file, 'rb') as f:
        encrypted = f.read()
    decrypted = ctx.decrypt(encrypted, metadata, password="pw")
    with open(decrypted_file, 'wb') as f:
        f.write(decrypted)

# Verify
with open(input_file, 'rb') as f:
    original = f.read()
with open(decrypted_file, 'rb') as f:
    decrypted = f.read()
assert original == decrypted

# Cleanup
os.remove(input_file)
os.remove(output_file)
os.remove(decrypted_file)

# Test 5: Entropy health
health = ctx.get_entropy_health()
assert 'quality_score' in health
assert 'status' in health
assert 'recommendations' in health
assert 0.0 <= health['quality_score'] <= 1.0
```

### 5. Update Documentation

**Update Code Comments**:

```python
# Before (v0.2.x)
# Encrypt data using STC

# After (v0.3.0)
# Encrypt data using STC v0.3.0 with polymorphic decoys,
# adaptive morphing, and entropy health monitoring
```

**Update README/Docs**:

- Mention v0.3.0 features
- Document new parameters
- Add migration notes

---

## Compatibility

### Forward Compatibility

**v0.3.0 → v0.2.x**: ❌ **NOT COMPATIBLE**

- v0.2.x cannot decrypt v0.3.0 ciphertexts
- Reason: New metadata fields (decoy_snapshots, entropy_delta, version)
- Workaround: Keep v0.3.0 installation or re-encrypt with v0.2.x

### Backward Compatibility

**v0.2.x → v0.3.0**: ✅ **FULLY COMPATIBLE**

- v0.3.0 can decrypt v0.2.x ciphertexts
- Automatic metadata format detection
- Transparent decompression

**Test**:

```python
# Encrypt with v0.2.x
# (requires v0.2.x installation)
from stc import STCContext as STCContext_v2
ctx_v2 = STCContext_v2("seed")
encrypted_v2, metadata_v2 = ctx_v2.encrypt(b"data", password="pw")

# Decrypt with v0.3.0
from stc import STCContext as STCContext_v3
ctx_v3 = STCContext_v3("seed")
decrypted_v3 = ctx_v3.decrypt(encrypted_v2, metadata_v2, password="pw")
assert decrypted_v3 == b"data"  # Works!
```

### Metadata Compatibility

**v0.2.x Metadata** (uncompressed):

```python
{
    'cel_snapshot': [...],  # ~950 KB uncompressed
    'phe_hash': b'...',
    'state_snapshot': {...}
}
```

**v0.3.0 Metadata** (compressed + decoys):

```python
{
    'cel_snapshot': [...],  # ~465 KB compressed (RLE + varint)
    'decoy_snapshots': [...],  # ~1,050 KB (3 decoys × ~350 KB each)
    'phe_hash': b'...',
    'state_snapshot': {...},  # Compressed
    'entropy_delta': 0.123,
    'version': '0.3.0'
}
```

**Compatibility**:

- v0.3.0 reads both formats (automatic detection)
- v0.2.x cannot read v0.3.0 format

---

## Migration Examples

### Example 1: Simple Encryption

**Before (v0.2.x)**:

```python
from stc import STCContext

ctx = STCContext("app-seed")
encrypted, metadata = ctx.encrypt(b"secret data", password="my_password")
```

**After (v0.3.0)** - No changes needed!

```python
from stc import STCContext

ctx = STCContext("app-seed")
encrypted, metadata = ctx.encrypt(b"secret data", password="my_password")
# Now includes: decoys, adaptive morphing, adaptive difficulty
# Metadata size: ~1,500 KB (vs ~950 KB in v0.2.x)
```

**After (v0.3.0)** - With entropy health:

```python
from stc import STCContext

ctx = STCContext("app-seed")

# Check entropy health
health = ctx.get_entropy_health()
if health['quality_score'] < 0.7:
    print("Refreshing entropy...")
    ctx.cel.update()

encrypted, metadata = ctx.encrypt(b"secret data", password="my_password")
```

### Example 2: Large File Encryption

**Before (v0.2.x)**:

```python
from stc import STCContext

ctx = STCContext("app-seed")

# Load entire file into memory (risky for large files)
with open("large_file.bin", 'rb') as f:
    data = f.read()  # May cause MemoryError

encrypted, metadata = ctx.encrypt(data, password="pw")

with open("large_file.enc", 'wb') as f:
    f.write(encrypted)
```

**After (v0.3.0)** - Using streaming:

```python
from stc import STCContext

ctx = STCContext("app-seed")

# Stream encryption (constant 8 MB memory)
metadata = ctx.encrypt_stream(
    input_path="large_file.bin",
    output_path="large_file.enc",
    password="pw",
    progress_callback=lambda b, t: print(f"Progress: {b/t*100:.1f}%")
)

# Save metadata
import pickle
with open("large_file.enc.meta", 'wb') as f:
    pickle.dump(metadata, f)
```

### Example 3: Password Manager

**Before (v0.2.x)**:

```python
import json
from stc import STCContext

class PasswordManager:
    def __init__(self, master_password):
        self.ctx = STCContext(f"pwmgr-{master_password}")
        self.master_password = master_password
    
    def store(self, service, password):
        encrypted, metadata = self.ctx.encrypt(
            password.encode(),
            password=self.master_password
        )
        # Save encrypted + metadata
```

**After (v0.3.0)** - With entropy health + decoys:

```python
import json
from stc import STCContext

class PasswordManager:
    def __init__(self, master_password):
        self.ctx = STCContext(f"pwmgr-{master_password}")
        self.master_password = master_password
        self.operations = 0
    
    def store(self, service, password):
        # Periodic entropy health check
        self.operations += 1
        if self.operations % 10 == 0:
            health = self.ctx.get_entropy_health()
            if health['quality_score'] < 0.85:
                self.ctx.cel.update()
        
        # Encrypt with full security
        encrypted, metadata = self.ctx.encrypt(
            password.encode(),
            password=self.master_password,
            num_decoys=5,  # High security
            context_data={'service': service}  # Service-specific context
        )
        # Save encrypted + metadata
```

### Example 4: Context-Aware Encryption

**Before (v0.2.x)**:

```python
from stc import STCContext
import time

ctx = STCContext("app-seed")

context = {
    'user_id': 'alice',
    'timestamp': int(time.time())
}

encrypted, metadata = ctx.encrypt(
    b"data",
    password="pw",
    context_data=context
)
```

**After (v0.3.0)** - Same code, more security:

```python
from stc import STCContext
import time

ctx = STCContext("app-seed")

context = {
    'user_id': 'alice',
    'timestamp': int(time.time())
}

encrypted, metadata = ctx.encrypt(
    b"data",
    password="pw",
    context_data=context
    # Automatic: decoys, adaptive morphing, adaptive difficulty
)
# No code changes needed!
```

---

## Troubleshooting

### Issue 1: "ValueError: Cannot decompress metadata"

**Cause**: Trying to decrypt v0.3.0 ciphertext with v0.2.x

**Solution**:

```bash
# Upgrade to v0.3.0
pip install --upgrade seigr-toolset-crypto

# Verify version
python -c "import stc; print(stc.__version__)"
```

### Issue 2: Metadata File Size Increased

**Cause**: Decoys enabled by default in v0.3.0

**Expected**:

- v0.2.x: ~950 KB
- v0.3.0 (no decoys): ~465 KB (compressed)
- v0.3.0 (3 decoys): ~1,500 KB
- v0.3.0 (5 decoys): ~2,000 KB

**Solution**:

- Accept increased size (worth security benefit)
- Adjust storage allocation
- Disable decoys only if absolutely necessary (NOT recommended):

```python
encrypted, metadata = ctx.encrypt(data, password=pw, use_decoys=False)
```

### Issue 3: decrypt_stream() Fails for Large Files

**Cause**: Known limitation in v0.3.0 (>100 MB files)

**Solution**:

```python
# Implement fallback
try:
    ctx.decrypt_stream(input_path, metadata, output_path, password=pw)
except Exception as e:
    print(f"Streaming failed, using standard decrypt: {e}")
    with open(input_path, 'rb') as f:
        encrypted = f.read()
    decrypted = ctx.decrypt(encrypted, metadata, password=pw)
    with open(output_path, 'wb') as f:
        f.write(decrypted)
```

**Fixed in**: v0.3.1 (planned)

### Issue 4: Hash Operations Slower Under Load

**Cause**: Adaptive difficulty scaling on oracle attack detection

**Expected**:

- Normal: 7 paths (~50ms)
- Attack detected: 15 paths (~100ms)

**Solution**:

- Implement request rate limiting
- Monitor PHE request patterns
- Disable adaptive difficulty only if false positives (NOT recommended):

```python
encrypted, metadata = ctx.encrypt(data, password=pw, adaptive_difficulty=False)
```

### Issue 5: "Low entropy quality" Warning

**Cause**: CEL degraded after many operations

**Solution**:

```python
# Check health
health = ctx.get_entropy_health()
print(f"Quality: {health['quality_score']:.2f}")
print(f"Recommendations: {health['recommendations']}")

# Refresh entropy
if health['quality_score'] < 0.7:
    ctx.cel.update()
    print("Entropy refreshed")
```

### Issue 6: Import Errors After Upgrade

**Cause**: Multiple STC versions installed

**Solution**:

```bash
# Uninstall all versions
pip uninstall seigr-toolset-crypto -y

# Reinstall v0.3.0
pip install seigr-toolset-crypto

# Verify
python -c "import stc; print(stc.__version__)"
```

---

## Rollback to v0.2.x

**If you need to rollback**:

```bash
# Uninstall v0.3.0
pip uninstall seigr-toolset-crypto -y

# Install v0.2.x
pip install seigr-toolset-crypto==0.2.0

# Verify
python -c "import stc; print(stc.__version__)"
```

**Limitations**:

- Cannot decrypt v0.3.0 ciphertexts
- No access to new features
- Consider re-encrypting data with v0.2.x if needed

---

## Support

For migration issues:

- **GitHub Issues**: [Seigr-lab/SeigrToolsetCrypto/issues](https://github.com/Seigr-lab/SeigrToolsetCrypto/issues)
- **Documentation**: [docs/](https://github.com/Seigr-lab/SeigrToolsetCrypto/tree/main/docs)
- **API Reference**: [docs/api-reference.md](api-reference.md)

---

## See Also

- **[API Reference](api-reference.md)** - Complete v0.3.0 API documentation
- **[Usage Guide](usage-guide.md)** - Practical examples for new features
- **[Security Guide](security-guide.md)** - Security best practices
- **[Architecture](architecture.md)** - v0.3.0 system design
- **[User Manual](user_manual/)** - Beginner-friendly guide
