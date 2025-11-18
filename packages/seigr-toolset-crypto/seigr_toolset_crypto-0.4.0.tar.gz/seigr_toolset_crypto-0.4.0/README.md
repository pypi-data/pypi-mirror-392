# Seigr Toolset Crypto (STC)

[![Sponsor Seigr-lab](https://img.shields.io/badge/Sponsor-Seigr--lab-forestgreen?style=flat&logo=github)](https://github.com/sponsors/Seigr-lab)
[![Version](https://img.shields.io/badge/version-0.4.0-blue)](https://github.com/Seigr-lab/SeigrToolsetCrypto/releases)
[![License](https://img.shields.io/badge/license-ANTI--CAPITALIST-red)](LICENSE)

**Post-classical cryptographic engine with automated security profiles**

## Overview

STC is a post-classical cryptographic system implementing lattice-based entropy generation, multi-path probabilistic hashing, and tensor-based data transformation. Designed for both high-security file encryption and real-time streaming applications.

### Core Capabilities

- **Post-Classical Cryptography** - No XOR, no block ciphers, lattice-based entropy (CEL), probabilistic hashing (PHE), tensor operations (DSF)
- **Automated Security Profiles** - 19+ specialized profiles with algorithmic file type detection and pattern-based content analysis
- **High-Performance Streaming** - Optimized interface for P2P applications, real-time video/audio, low-latency requirements
- **Adaptive Security** - Dynamic parameter adjustment based on detected threats and usage patterns
- **Command-Line Interface** - Simple encryption without programming required
- **Large File Support** - Files >100GB with constant 7MB memory usage

### Core Cryptographic Components

- **Continuous Entropy Lattice (CEL)** - Lattice-based entropy generation with quality metrics
- **Probabilistic Hashing Engine (PHE)** - Multi-path hashing with configurable path count
- **Contextual Key Emergence (CKE)** - Key derivation from lattice state intersections
- **Data-State Folding (DSF)** - Data transformation using tensor operations
- **Polymorphic Cryptographic Flow (PCF)** - Parameter modification based on entropy state
- **Decoy System** - Variable-count fake data vectors for obfuscation
- **State Persistence** - Serialization of cryptographic state to binary format

## Architecture

```
core/
├── cel/       # Continuous Entropy Lattice
├── phe/       # Probabilistic Hashing Engine  
├── cke/       # Contextual Key Emergence
├── dsf/       # Data-State Folding
├── pcf/       # Polymorphic Cryptographic Flow
├── state/     # State persistence and reconstruction
└── profiles/  # Automated Security Profiles
    ├── security_profiles.py      # 5 basic profiles (Document, Media, etc.)
    ├── profile_definitions.py    # 19 specialized profiles with parameter sets
    ├── adaptive_security.py      # Parameter adjustment based on detected patterns
    └── content_optimizers.py     # File-type specific optimizations

interfaces/
├── api/       # Programmatic interface
├── cli/       # Command-line tools
└── bindings/  # Future cross-language bindings

utils/         # Mathematical primitives + TLV varint encoding
tests/         # Validation and integrity checks (100+ tests)
```

## Key Features

### Streaming Encryption

**StreamingContext** - Optimized for P2P streaming applications:

- Real-time encryption: 132.9 FPS sustained, 7.52ms average latency
- Adaptive chunking: Auto-split large frames for optimal performance
- Minimal overhead: 16-byte fixed headers (0.31% metadata overhead)
- Constant memory: 7MB RAM regardless of data size
- Use cases: Video/audio streaming, live data feeds, game state sync

### File Encryption

**Security Profiles** - Automated parameter selection:

- 19+ specialized profiles (Document, Media, Credentials, Financial, Medical, Legal, etc.)
- Automatic file type detection via extensions, signatures, and content analysis
- Content-aware optimization: Different lattice sizes and parameters per file type
- Compliance ready: HIPAA, GDPR, SOX-compliant configurations

### Large File Processing

- Files >100GB supported through chunked streaming
- Constant 7MB memory usage during processing
- Upfront decoy validation: 3-5x faster decryption
- Streaming throughput: 50-100 MB/s depending on profile

### Performance Benchmarks

**StreamingContext** (P2P use cases):

- Latency: 7.52ms per frame (5KB frames, 30 FPS scenario)
- Throughput: 0.65 MB/s sustained
- Overhead: 0.31% (16 bytes per frame)

**File Profiles** (traditional encryption):

- Document: ~0.8s encryption, ~200KB metadata
- Media: ~0.5s encryption, ~150KB metadata  
- Credential: ~2.0s encryption, ~500KB metadata

## Installation

### From PyPI (Recommended)

```bash
pip install seigr-toolset-crypto==0.4.0
```

### From GitHub Release

Download the latest release from [Releases](https://github.com/Seigr-lab/SeigrToolsetCrypto/releases):

```bash
# Install from wheel (recommended)
pip install seigr_toolset_crypto-0.4.0-py3-none-any.whl

# Or install from source tarball
pip install seigr_toolset_crypto-0.4.0.tar.gz
```

### From Source (Development)

```bash
git clone https://github.com/Seigr-lab/SeigrToolsetCrypto.git
cd SeigrToolsetCrypto
pip install -e .
```

### Requirements

- Python 3.9+
- NumPy 1.24.0+

## Quick Start

### Option 1: High-Performance Streaming (NEW in v0.4.0)

```python
# For P2P streaming, real-time video/audio, low-latency applications
from interfaces.api.streaming_context import StreamingContext

# Initialize streaming context
ctx = StreamingContext('stream_session_id')

# Encrypt frame (video, audio, real-time data)
header, encrypted = ctx.encrypt_chunk(frame_data)

# Send 16-byte header + encrypted data over network
header_bytes = header.to_bytes()  # Fixed 16 bytes

# Decrypt frame
decrypted = ctx.decrypt_chunk(header, encrypted)

# Performance: 132.9 FPS, 7.52ms latency, 0.31% overhead
```

### Option 2: Command Line Usage

```bash
# Install STC
pip install seigr-toolset-crypto==0.4.0

# Encrypt file with automatic profile selection
stc-cli encrypt --input my_file.pdf --password "my_password"

# File type detected and appropriate parameters applied automatically
```

### Profile Analysis

```bash
# Analyze file to see detected type and recommended profile
stc-cli analyze --input my_document.pdf

# Output shows detected file type and selected parameter set
```

### Option 3: I'm a Developer

```python
# Install and import
pip install seigr-toolset-crypto==0.4.0

from core.profiles import get_profile_for_file
from stc import STCContext

# Detect file type and get corresponding parameter set
profile = get_profile_for_file("my_file.pdf")  # Returns detected profile
ctx = STCContext("my-app")
encrypted, metadata = ctx.encrypt_file("my_file.pdf", "password", profile=profile)
```

## Detailed Examples

### Command Line Interface

```bash
# Encrypt file with automatic profile detection
stc-cli encrypt --input my_document.pdf --password "my_password"

# Decrypt file
stc-cli decrypt --input my_document.pdf.enc --password "my_password"

# Analyze file type and see recommended profile
stc-cli analyze --input family_photo.jpg
# Output shows detected file type and selected parameter set
```

### Profile Detection System

```python
from core.profiles import get_profile_for_file, get_optimized_parameters
from stc import STCContext

# Automatic file type detection based on extension and content
profile = get_profile_for_file("tax_return.pdf")     # Returns "document"
profile = get_profile_for_file("family_photo.jpg")   # Returns "media" 
profile = get_profile_for_file("passwords.txt")      # Returns "credentials"

# Get parameter set for detected profile
params = get_optimized_parameters(profile, file_size=2048000)

# Encrypt with profile-specific parameters
ctx = STCContext("my-app")
encrypted, metadata = ctx.encrypt_file("tax_return.pdf", "password", profile_params=params)
```

### Content Analysis

```python
from core.profiles import SecurityProfileManager

# Analyze file content using pattern matching and heuristics
with open("sensitive_document.pdf", "rb") as f:
    data = f.read()

result = SecurityProfileManager.analyze_and_recommend(
    data, filename="sensitive_document.pdf"
)

print(f"Detected type: {result['content_analysis']['file_type']}")
print(f"Recommended profile: {result['recommended_profile']}")  
print(f"Confidence: {result['confidence']:.2f}")
print(f"Analysis: {result['content_analysis']}")
```

### Traditional Programming (Full Control)

```python
from interfaces.api.stc_api import STCContext

# Manual approach for developers
ctx = STCContext('my-unique-seed')
encrypted, metadata = ctx.encrypt("Secret message", password="strong_password")
decrypted = ctx.decrypt(encrypted, metadata, password="strong_password")
print(decrypted)  # "Secret message"
```

### Usage Examples

```bash
# Encrypt folder with media profile parameters
stc-cli encrypt-folder --input "Family Photos" --profile media --password "family_2024"

# Use credential profile for sensitive documents
stc-cli encrypt --input "tax_return.pdf" --profile credentials --password "tax_secure_2024"

# Use backup profile for system files
stc-cli encrypt --input "system_backup.tar.gz" --profile backup --password "backup_2024"
```

### Advanced Usage

```python
# Content analysis with additional parameters
with open("patient_record.pdf", "rb") as f:
    data = f.read()

result = SecurityProfileManager.analyze_and_recommend(
    data, filename="patient_record.pdf"
)

# Manual parameter adjustment based on requirements
from core.profiles import AdaptiveSecurityManager
adaptive = AdaptiveSecurityManager()
# Note: Threat detection is based on pattern analysis, not active monitoring
```

### Basic API (No Password)

```python
from interfaces.api import stc_api

# Initialize STC context
context = stc_api.initialize(seed="your-seed-phrase")

# Encrypt data (uses seed as password)
encrypted, metadata = context.encrypt("sensitive information")

# Decrypt data
decrypted = context.decrypt(encrypted, metadata)
print(decrypted)  # "sensitive information"

# Generate probabilistic hash
hash_result = context.hash("data to hash")
```

### Quick API (One-liners)

```python
from interfaces.api import stc_api

# Quick encrypt - returns encrypted data, metadata, and context
encrypted, metadata, context = stc_api.quick_encrypt(
    "sensitive data", 
    seed="your-seed"
)

# Quick decrypt - reconstructs context from metadata
decrypted = stc_api.quick_decrypt(
    encrypted, 
    metadata, 
    seed="your-seed"
)
```

## Usage

### Advanced: Custom Parameters

```python
from interfaces.api.stc_api import STCContext

# Custom lattice and security parameters
context = STCContext(
    seed="your-seed",
    lattice_size=128,      # Default: 128 (optimized in v0.2.0)
    depth=6,               # Default: 6 (optimized in v0.2.0)
    morph_interval=100,    # PCF morphing interval
    adaptive_morphing=True,  # v0.3.0: CEL-delta-driven intervals
    adaptive_difficulty='balanced'  # v0.3.0: 'fast', 'balanced', 'paranoid'
)

# Encrypt with custom context and v0.3.0 features
encrypted, metadata = context.encrypt(
    "data",
    password="password123",
    use_decoys=True,           # v0.3.0: Enabled by default
    num_decoys=3,              # v0.3.0: Default count
    variable_decoy_sizes=True  # v0.3.0: Polymorphic decoys
)

# Derive keys
key = context.derive_key(length=32)

# Hash data
hash_value = context.hash("data")
```

### State Management

```python
# Save context state
state = context.save_state()

# Load state (for resuming)
context.load_state(state)

# Get context status
status = context.get_status()
print(status)
```

## Complete Feature Set

### Cryptographic Engine

**Post-Classical Architecture**:

- Continuous Entropy Lattice (CEL): Lattice-based entropy with quality metrics and health monitoring
- Probabilistic Hashing Engine (PHE): Multi-path hashing (3-15 parallel paths, adaptive)
- Contextual Key Emergence (CKE): Key derivation from lattice state intersections
- Data-State Folding (DSF): Tensor-based data transformation
- Polymorphic Cryptographic Flow (PCF): Dynamic parameter modification

**Security Features**:

- Password-based encryption with MAC verification
- Metadata encryption using ephemeral keys
- Decoy vector system with variable sizes (32×3 to 96×5) and randomized counts
- Entropy quality auditing and threshold enforcement
- Adaptive difficulty scaling with oracle attack detection
- Context-adaptive morphing (CEL-delta-driven intervals)

### Automated Security Profiles

**Algorithmic Profile Selection**:

- 19+ specialized profiles (Financial, Medical, Legal, Technical, Government, Document, Media, Credentials, etc.)
- Automatic file type detection via extensions, binary signatures, and content analysis
- Pattern matching for sensitive data (SSN, credit cards, medical terms, PII)
- Dynamic parameter adjustment based on file size and content type
- Compliance-ready configurations (HIPAA, GDPR, SOX)

**Profile Optimization**:

- Different lattice sizes per profile (96×96×5 to 256×256×8)
- Variable security parameters for speed/security trade-offs
- Content-aware CEL depth and PHE path count selection
- Decoy count optimization per use case

### High-Performance Streaming

**StreamingContext Interface**:

- Real-time encryption for P2P applications (video, audio, live data)
- Adaptive chunking: Auto-split large frames into optimal sub-chunks (default 8KB)
- Fixed 16-byte headers (sequence, nonce, data_length, flags)
- Lazy CEL initialization (depth 2→6 on demand)
- Precomputed key schedules (256 keys upfront)
- Simplified DSF (2 folds vs 5 for small chunks)
- Entropy pooling (1KB reused across chunks)

**Performance Characteristics**:

- 132.9 FPS sustained (5KB frames)
- 7.52ms average latency
- 0.31% metadata overhead
- Constant 7MB memory usage
- Use cases: SeigrToolsetTransmissions, real-time streaming, game state sync

### Large File Processing

**Streaming Engine**:

- Chunk-based encryption (configurable chunk size, default 1MB)
- Files >100GB supported
- Constant 7MB RAM usage regardless of file size
- Upfront decoy validation (3-5x faster decryption)
- Progress callbacks for UI integration
- Memory-efficient streaming API

### Command-Line Interface

**Simple Operations**:

- File encryption/decryption: `stc-cli encrypt --input file.pdf --password secret`
- Batch folder operations: `stc-cli encrypt-folder --input ./documents/`
- Profile analysis: `stc-cli analyze --input file.pdf`
- Automatic mode: `stc-cli encrypt --auto` (auto-detects file type and recommends profile)
- Cross-platform support (Windows, macOS, Linux)

### Developer API

**Multiple Interfaces**:

- STCContext: Full-featured encryption with profiles, decoys, streaming
- StreamingContext: Optimized for real-time P2P applications
- Quick API: One-liner encrypt/decrypt functions
- Programmatic profile selection and customization

**Advanced Features**:

- Custom lattice parameters (size, depth, morph intervals)
- Context data for additional encryption layers
- State persistence and serialization
- Entropy health monitoring and quality thresholds
- Performance statistics and benchmarking

## Recent Changes

**v0.4.0** (November 15, 2025):

- Added StreamingContext for P2P streaming applications
- Adaptive chunking for optimal DSF performance on large frames
- 16-byte fixed headers (99.992% metadata reduction for streaming)
- Post-classical compliance (removed all XOR-based operations)

**v0.3.1** (November 2, 2025):

- 19+ automated security profiles with pattern-based content analysis
- Command-line interface with batch operations
- Upfront decoy validation (3-5x faster decryption)
- Large file streaming (>100GB, constant 7MB memory)

**v0.3.0** (October 30, 2025):

- Entropy health API with quality scoring
- Enhanced decoy polymorphism (variable sizes, randomized counts)
- Adaptive difficulty scaling and oracle attack detection
- Context-adaptive morphing

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## Design Principles

1. **Post-classical cryptography** - No XOR, no block ciphers, no legacy vulnerabilities
2. **Security by default** - All security features enabled unless explicitly disabled
3. **Automated optimization** - Optimal settings chosen automatically based on algorithmic analysis
4. **Performance through optimization** - Fast implementation, not reduced security
5. **Universal accessibility** - From command-line to enterprise API
6. **Transparency and auditability** - Open implementation, comprehensive testing

## Examples

See `examples/` directory for practical demonstrations:

- **`password_manager/`** - Secure credential storage with automated profiles
- **`config_encryption/`** - Configuration file encryption with auto-detection
- **`entropy_health/`** - Entropy monitoring and quality threshold examples
- **`validation/`** - Security profile validation and testing examples

Also see comprehensive user manual at `docs/user_manual/` with step-by-step guides for:

- **Security Profiles** - Auto-detection and algorithmic recommendations
- **Command-Line Usage** - Simple encryption without programming
- **Profile System** - Pattern-based content analysis
- **Real-World Scenarios** - Complete examples for common use cases

Run examples:

```bash
cd examples/password_manager
python password_manager.py

cd examples/config_encryption
python config_example.py

cd examples/entropy_health
python entropy_monitoring.py
```

## Testing

Run the full test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_cel.py -v
python -m pytest tests/test_phe.py -v
python -m pytest tests/test_streaming_context.py -v
python -m pytest tests/test_integration_v031.py -v
python -m pytest tests/test_security_profiles.py -v
```

**Test Coverage**: 120+ tests passing (v0.4.0)
- Core cryptographic components: 40+ tests
- Automated security profiles: 30+ tests  
- StreamingContext: 21 tests
- Integration tests: 25+ tests
- Performance benchmarks: 5+ tests

## Development Status

**v0.4.0** - Production-ready with StreamingContext for P2P applications

### Current Capabilities

- StreamingContext: Real-time P2P encryption (132.9 FPS, 7.52ms latency)
- Automated Security Profiles: 19+ profiles with pattern-based content analysis
- High-Performance Streaming: >100GB files, 50+ MB/s, 7MB constant memory
- Command-Line Interface: Simple encryption for all users
- Adaptive Security: Automatic threat response and optimization
- Comprehensive Testing: 120+ tests passing (including StreamingContext suite)

### Future Development

- v0.4.1: Hardware acceleration (SIMD/GPU), StreamingContext profile presets
- v0.5.0: Multi-threaded encryption, WebAssembly bindings
- v1.0.0: Formal security audit, quantum resistance research, stable API guarantee

## Collaboration

Seigr Toolset Crypto is developed as part of the Seigr Ecosystem, a self-sovereign decentralized network. Development follows the principles of radical transparency and community-driven innovation.

**For Seigr Ecosystem Contributors:**
- Review architecture documentation in `docs/`
- All code changes require comprehensive test coverage
- Follow post-classical cryptographic principles (no XOR, no legacy crypto)
- Maintain compatibility with SeigrToolsetTransmissions and other Seigr components

**For External Researchers:**
- Security analysis and cryptographic review welcome
- Submit findings via GitHub Issues with detailed technical analysis
- Reference implementations and academic research encouraged

**Code Quality Standards:**
- All features must have corresponding tests
- Performance benchmarks required for optimization changes
- Documentation updates mandatory for API changes
- Follow existing code structure and naming conventions

## License

ANTI-CAPITALIST SOFTWARE LICENSE (v 1.4) - See LICENSE file for details

---

## Citation

If you use STC in research, please cite:

```bibtex
@software{seigr_toolset_crypto,
  title = {Seigr Toolset Crypto: Post-Classical Cryptographic Engine with StreamingContext},
  author = {Seigr-lab},
  year = {2025},
  version = {0.4.0},
  url = {https://github.com/Seigr-lab/SeigrToolsetCrypto}
}
```
