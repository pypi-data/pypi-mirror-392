# Using STC in Your Project

## Installation

```bash
pip install seigr-toolset-crypto
```

## Quick Start - Simple API (Recommended)

```python
import stc

# Encrypt data
encrypted, metadata = stc.encrypt(b"secret data", password="my_password")

# Decrypt data
data = stc.decrypt(encrypted, metadata, password="my_password")
```

That's it! You now have post-classical encryption.

## File Encryption

```python
import stc

# Encrypt a file
info = stc.encrypt_file(
    "document.pdf",
    "document.enc",
    password="my_password"
)
print(f"Encrypted {info['original_size']} bytes to {info['encrypted_size']} bytes")

# Decrypt a file
info = stc.decrypt_file(
    "document.enc",
    "document_decrypted.pdf",
    password="my_password"
)
```

**Important**: File encryption creates TWO files:

- `document.enc` - the encrypted data
- `document.enc.meta` - the metadata

You need BOTH to decrypt. Don't lose either one!

## Automatic Security Profiles

STC automatically detects file types and applies appropriate security:

```python
# Financial data gets maximum security
encrypted, meta = stc.encrypt_file("taxes_2024.pdf", "taxes.enc", password="pass")

# Media files get optimized speed
encrypted, meta = stc.encrypt_file("video.mp4", "video.enc", password="pass")
```

Or specify explicitly:

```python
encrypted, meta = stc.encrypt(
    data,
    password="pass",
    profile="FINANCIAL_DATA"  # Maximum security
)
```

Available profiles:

- `FINANCIAL_DATA` - Tax docs, invoices, financial records
- `MEDICAL_RECORDS` - Health data, insurance, medical files
- `CREDENTIALS` - Passwords, API keys, certificates
- `LEGAL_DOCUMENTS` - Contracts, agreements, legal files
- `SOURCE_CODE` - Programming files, repositories
- `DOCUMENT` - General documents (default)
- `MEDIA` - Photos, videos, audio
- `BACKUP` - Archive files, backups

## For P2P / Streaming Applications

```python
import stc

# Create streaming context (both peers use same seed)
stream = stc.StreamingContext("session-shared-seed")

# Encrypt frame (sender)
header, encrypted_frame = stream.encrypt_chunk(video_frame_data)

# Send both header (16 bytes) and encrypted frame
network_send(header.to_bytes() + encrypted_frame)

# Decrypt frame (receiver)
received_data = network_receive()
header = stc.ChunkHeader.from_bytes(received_data[:16])
encrypted = received_data[16:]
frame = stream.decrypt_chunk(header, encrypted)
```

Performance: **132 FPS at 7.5ms latency** for 5KB frames.

## Advanced: Multiple Operations with Same Seed

```python
import stc

# Create context once, use many times
ctx = stc.Context(seed="my-app-seed")

# Encrypt multiple pieces of data
user_data, meta1 = ctx.encrypt(user_info)
settings_data, meta2 = ctx.encrypt(settings)
logs_data, meta3 = ctx.encrypt(logs)

# All use same cryptographic state
# More efficient than creating new context each time
```

## Security Best Practices

### DO

- ✅ Use strong passwords (12+ characters, mixed case, numbers, symbols)
- ✅ Store passwords securely (environment variables, key vault, NOT in code)
- ✅ Keep backups of encrypted files AND metadata
- ✅ Set proper file permissions (`chmod 600` on Unix)
- ✅ Let STC auto-detect profiles for appropriate security

### DON'T

- ❌ Lose your password (data is unrecoverable)
- ❌ Lose metadata files (needed for decryption)
- ❌ Store passwords in code or version control
- ❌ Use weak/simple passwords
- ❌ Upload encrypted data and metadata together to untrusted storage

## What Makes STC Different?

Unlike traditional encryption (AES, RSA):

1. **Post-Classical**: No XOR, no block ciphers, no classical crypto fallbacks
2. **Lattice-Based**: Uses multi-dimensional entropy lattices (resistant to quantum attacks)
3. **Self-Sovereign**: No cloud, no keys sent anywhere, complete data sovereignty
4. **Adaptive**: Security adjusts based on content type and threats
5. **Entropy-Regenerative**: Cryptographic state evolves, preventing pattern analysis

## Backwards Compatibility

Existing code using the old API still works:

```python
from SeigrToolsetCrypto import STCContext

# Old way (still supported)
ctx = STCContext(seed="my-seed")
encrypted, metadata = ctx.encrypt(data)
decrypted = ctx.decrypt(encrypted, metadata)
```

But the new `stc` module is simpler and recommended.

## Need Help?

- **Documentation**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/tree/main/docs>
- **Examples**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/tree/main/examples>
- **Issues**: <https://github.com/Seigr-lab/SeigrToolsetCrypto/issues>

## License

ANTI-CAPITALIST SOFTWARE LICENSE (v1.4)
