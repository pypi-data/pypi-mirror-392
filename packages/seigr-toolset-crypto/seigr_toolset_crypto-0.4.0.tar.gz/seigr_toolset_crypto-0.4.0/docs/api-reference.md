# API Reference - STC v0.3.0# API Reference - STC v0.2.0



Complete API documentation for Seigr Toolset Crypto v0.3.0 "Adaptive Security & Transparency"Complete API documentation for Seigr Toolset Crypto v0.2.0



## interfaces.api.stc_api## interfaces.api.stc_api



### STCContext### STCContext



Main context class for STC operations with password-based encryption, MAC verification, entropy health monitoring, and streaming support.Main context class for STC operations with password-based encryption and MAC verification.



#### Constructor#### Constructor



```python```python

STCContext(STCContext(

    seed: Union[str, bytes, int],    seed: Union[str, bytes, int],

    lattice_size: int = 128,    lattice_size: int = 128,

    depth: int = 6,    depth: int = 6,

    morph_interval: int = 100    morph_interval: int = 100

))

``````



**Parameters:****Parameters:**

- `seed`: Initialization seed (determines initial CEL state)

- `seed`: Initialization seed (determines initial CEL state)- `lattice_size`: CEL lattice dimension (default: 128, range: 16-256)

- `lattice_size`: CEL lattice dimension (default: 128, range: 16-256)- `depth`: CEL lattice depth (default: 6, range: 2-8)

- `depth`: CEL lattice depth (default: 6, range: 2-8)- `morph_interval`: PCF morphing frequency (default: 100 operations)

- `morph_interval`: Base PCF morphing frequency (default: 100, adaptive in v0.3.0)

**Returns:** `STCContext` instance

**Returns:** `STCContext` instance

**Example:**

**Example:**```python

from interfaces.api.stc_api import STCContext

```python

from interfaces.api.stc_api import STCContext# Default parameters (balanced)

ctx = STCContext('my-seed')

# Default parameters (balanced security + performance)

ctx = STCContext('my-seed')# Custom parameters (faster, smaller metadata)

ctx_fast = STCContext('my-seed', lattice_size=64, depth=4)

# Custom parameters (faster, smaller metadata)

ctx_fast = STCContext('my-seed', lattice_size=64, depth=4)# Maximum security (slower, larger metadata)

ctx_secure = STCContext('my-seed', lattice_size=256, depth=8)

# Maximum security (slower, larger metadata)```

ctx_secure = STCContext('my-seed', lattice_size=256, depth=8)

```---



---#### encrypt()



#### encrypt()```python

encrypt(

```python    data: Union[str, bytes],

encrypt(    context_data: Optional[Dict[str, Any]] = None,

    data: Union[str, bytes],    password: Optional[str] = None,

    context_data: Optional[Dict[str, Any]] = None,    use_decoys: bool = False,

    password: Optional[str] = None,    num_decoys: int = 3

    use_decoys: bool = True,              # v0.3.0: Default True) -> Tuple[bytes, bytes]

    num_decoys: int = 3,```

    variable_decoy_sizes: bool = True,     # v0.3.0: NEW

    randomize_decoy_count: bool = True,    # v0.3.0: NEWEncrypt data with password-based protection and MAC.

    timing_randomization: bool = False,    # v0.3.0: NEW (opt-in)

    noise_padding: bool = False,           # v0.3.0: NEW (opt-in)**Parameters:**

    adaptive_morphing: bool = True,        # v0.3.0: NEW- `data`: Data to encrypt (string or bytes)

    adaptive_difficulty: bool = True       # v0.3.0: NEW- `context_data`: Optional additional context for key derivation

) -> Tuple[bytes, bytes]- `password`: Encryption password (if None, uses seed)

```- `use_decoys`: Enable decoy vectors (NOT YET SUPPORTED - must be False)

- `num_decoys`: Number of decoy snapshots (3-5)

Encrypt data with password-based protection, MAC, and polymorphic decoys.

**Returns:** Tuple of `(encrypted_bytes, metadata_bytes)`

**Parameters:**- `encrypted_bytes`: Encrypted data (binary)

- `metadata_bytes`: Binary TLV format metadata (~786KB)

- `data`: Data to encrypt (string or bytes)

- `context_data`: Optional additional context for key derivation**Raises:**

- `password`: Encryption password (if None, uses seed)- `TypeError`: If data is not str or bytes

- `use_decoys`: **v0.3.0: Enable decoy vectors** (default: True)- `ValueError`: If use_decoys=True (not yet implemented)

- `num_decoys`: Base number of decoy snapshots (3-7, default: 3)

- `variable_decoy_sizes`: **v0.3.0: Use variable decoy lattice sizes** (default: True)**Example:**

- `randomize_decoy_count`: **v0.3.0: Randomize actual decoy count** (default: True)```python

- `timing_randomization`: **v0.3.0: Add timing jitter** (opt-in, adds delay)ctx = STCContext('my-seed')

- `noise_padding`: **v0.3.0: Add noise to metadata** (opt-in, increases size)

- `adaptive_morphing`: **v0.3.0: CEL-delta-driven morphing** (default: True)# With password

- `adaptive_difficulty`: **v0.3.0: Oracle attack detection** (default: True)encrypted, metadata = ctx.encrypt(

    "Secret message",

**Returns:** Tuple of `(encrypted_bytes, metadata_bytes)`    password="strong_password"

)

- `encrypted_bytes`: Encrypted data (binary)

- `metadata_bytes`: Binary TLV format metadata (~486 KB compressed)# Without password (uses seed)

encrypted, metadata = ctx.encrypt("Data")

**Raises:**

# Binary data

- `TypeError`: If data is not str or bytesencrypted, metadata = ctx.encrypt(

- `ValueError`: If entropy health quality < 0.5 (unsafe to encrypt)    b'\x00\x01\x02\xFF',

    password="pw"

**Example:**)

```

```python

ctx = STCContext('my-seed')---



# v0.3.0: Full security with all features (RECOMMENDED)#### decrypt()

encrypted, metadata = ctx.encrypt(

    "Secret message",```python

    password="strong_password"decrypt(

    # use_decoys=True (default)    encrypted_data: bytes,

    # variable_decoy_sizes=True (default)    metadata: Union[Dict[str, Any], bytes],

    # randomize_decoy_count=True (default)    context_data: Optional[Dict[str, Any]] = None,

    # adaptive_morphing=True (default)    password: Optional[str] = None

    # adaptive_difficulty=True (default)) -> Union[str, bytes]

)```



# Minimal (faster, less secure - NOT recommended)Decrypt data with automatic MAC verification.

encrypted, metadata = ctx.encrypt(

    "Data",**Parameters:**

    use_decoys=False,- `encrypted_data`: Encrypted bytes from encrypt()

    adaptive_morphing=False,- `metadata`: Metadata from encrypt() (binary TLV or dict for v0.1.x compat)

    adaptive_difficulty=False- `context_data`: Optional context (must match encryption)

)- `password`: Decryption password (if None, uses seed)



# With timing obfuscation (adds 0.1-1.0ms delay per decoy)**Returns:** Decrypted data (string if was_string=True, else bytes)

encrypted, metadata = ctx.encrypt(

    "High-value data",**Raises:**

    password="pw",- `ValueError`: If MAC verification fails (wrong password or tampering)

    timing_randomization=True- `KeyError`: If required metadata fields missing

)- `Exception`: If decryption fails for other reasons



# With noise padding (adds random noise to metadata)**Example:**

encrypted, metadata = ctx.encrypt(```python

    "Extra secure data",ctx = STCContext('my-seed')

    password="pw",

    noise_padding=True# With password

)try:

    decrypted = ctx.decrypt(

# Binary data        encrypted,

encrypted, metadata = ctx.encrypt(        metadata,

    b'\x00\x01\x02\xFF',        password="strong_password"

    password="pw"    )

)except ValueError:

```    print("Wrong password or data tampered!")



**v0.3.0 Security Notes:**# Without password (uses seed)

decrypted = ctx.decrypt(encrypted, metadata)

- **Default behavior changed**: `use_decoys=True` by default (was False in v0.2.x)

- **Polymorphic decoys**: Variable sizes (32-96), randomized count (±2)# Backward compatible with v0.1.x JSON metadata

- **Adaptive morphing**: CEL-delta determines interval (50/100/200 ops)decrypted = ctx.decrypt(encrypted, old_json_metadata)

- **Adaptive difficulty**: PHE paths scale from 7→15 on oracle attack detection```



------



#### decrypt()#### hash()



```python```python

decrypt(hash(

    encrypted_data: bytes,    data: Union[str, bytes],

    metadata: Union[Dict[str, Any], bytes],    context_data: Optional[Dict[str, Any]] = None

    context_data: Optional[Dict[str, Any]] = None,) -> bytes

    password: Optional[str] = None```

) -> Union[str, bytes]

```Generate probabilistic hash (CEL-driven, changes over time).



Decrypt data with automatic MAC verification and decoy CEL selection.**Parameters:**

- `data`: Data to hash

**Parameters:**- `context_data`: Optional additional context



- `encrypted_data`: Encrypted bytes from encrypt()**Returns:** 32-byte hash value

- `metadata`: Metadata from encrypt() (binary TLV or dict for backward compat)

- `context_data`: Optional context (must match encryption)**Note:** Each call produces different hash due to CEL evolution. Not suitable for password verification unless CEL state is frozen.

- `password`: Decryption password (if None, uses seed)

**Example:**

**Returns:** Decrypted data (string if was_string=True, else bytes)```python

ctx = STCContext('hash-seed')

**Raises:**

hash1 = ctx.hash("data")

- `ValueError`: If MAC verification fails (wrong password or tampering)hash2 = ctx.hash("data")

- `KeyError`: If required metadata fields missing

- `Exception`: If decryption fails (wrong CEL, corrupted data)assert hash1 != hash2  # Different due to CEL evolution

assert len(hash1) == 32

**Example:**```



```python---

ctx = STCContext('my-seed')

#### derive_key()

# With password

try:```python

    decrypted = ctx.decrypt(derive_key(

        encrypted,    length: int = 32,

        metadata,    context_data: Optional[Dict[str, Any]] = None

        password="strong_password") -> bytes

    )```

except ValueError:

    print("Wrong password or data tampered!")Derive cryptographic key using CKE.



# Without password (uses seed)**Parameters:**

decrypted = ctx.decrypt(encrypted, metadata)- `length`: Key length in bytes (default: 32)

- `context_data`: Optional additional context

# Backward compatible with v0.1.x JSON metadata

decrypted = ctx.decrypt(encrypted, old_json_metadata)**Returns:** Derived key (bytes of specified length)



# Backward compatible with v0.2.x without decoys**Example:**

decrypted = ctx.decrypt(encrypted, v2_metadata)```python

```ctx = STCContext('my-seed')



**v0.3.0 Decoy Handling:**# Derive 32-byte key

key = ctx.derive_key()

Automatically tries all CEL snapshots (real + decoys) until successful decryption. Attacker cannot determine which CEL is real without knowing password and context_data.

# Derive 64-byte key

---key_64 = ctx.derive_key(length=64)



#### encrypt_stream()# With context

key_ctx = ctx.derive_key(context_data={'user': 'alice'})

```python```

encrypt_stream(

    input_stream: BinaryIO,---

    output_stream: BinaryIO,

    context_data: Optional[Dict[str, Any]] = None,#### save_state()

    password: Optional[str] = None,

    chunk_size: int = 1048576,  # 1 MB chunks```python

    progress_callback: Optional[Callable[[int, int], None]] = None,save_state() -> Dict[str, Any]

    **encrypt_options```

) -> bytes

```Save current context state (CEL, PHE, PCF).



**v0.3.0: NEW** - Encrypt large files incrementally without loading into memory.**Returns:** Dict containing all component states



**Parameters:****Example:**

```python

- `input_stream`: Input file-like object (opened in 'rb' mode)ctx = STCContext('my-seed')

- `output_stream`: Output file-like object (opened in 'wb' mode)

- `context_data`: Optional additional context# Perform operations

- `password`: Encryption passwordctx.hash("data1")

- `chunk_size`: Size of chunks to process (default: 1 MB)ctx.hash("data2")

- `progress_callback`: Optional callback function `(current_bytes, total_bytes) -> None`

- `**encrypt_options`: Additional options passed to encrypt() (e.g., use_decoys, num_decoys)# Save state

state = ctx.save_state()

**Returns:** Metadata bytes (must be saved separately)

# State keys

**Example:**print(state.keys())  # dict_keys(['cel_state', 'phe_state', 'pcf_state'])

```

```python

ctx = STCContext('my-seed')---



# Define progress callback#### load_state()

def progress(current, total):

    percent = (current / total) * 100```python

    print(f"Encrypting: {percent:.1f}%", end='\r')load_state(state: Dict[str, Any]) -> None

```

# Encrypt large file

with open('large_file.bin', 'rb') as input_file:Load previously saved context state.

    with open('encrypted.bin', 'wb') as output_file:

        metadata = ctx.encrypt_stream(**Parameters:**

            input_stream=input_file,- `state`: State dict from save_state()

            output_stream=output_file,

            password="strong_pw",**Example:**

            progress_callback=progress```python

        )# Save state

state = ctx.save_state()

# Save metadata separately

with open('encrypted.bin.meta', 'wb') as meta_file:# Create new context and load state

    meta_file.write(metadata)ctx2 = STCContext('my-seed')

ctx2.load_state(state)

print("\nEncryption complete!")

```# ctx2 now has same state as ctx

```

**Memory Usage:**

---

- Constant ~8 MB regardless of file size

- Processes files of any size#### get_status()

- Suitable for multi-GB files

```python

---get_status() -> str

```

#### decrypt_stream()

Get human-readable context status.

```python

decrypt_stream(**Returns:** Formatted status string

    encrypted_stream: BinaryIO,

    metadata: bytes,**Example:**

    output_stream: BinaryIO,```python

    context_data: Optional[Dict[str, Any]] = None,ctx = STCContext('my-seed')

    password: Optional[str] = None,print(ctx.get_status())

    chunk_size: int = 1048576,

    progress_callback: Optional[Callable[[int, int], None]] = None# Output:

) -> None# === STC Context Status ===

```# CEL Operation Count: 10

# CEL State Version: 5

**v0.3.0: NEW** - Decrypt large files incrementally.# CEL Lattice Size: 128x128x6

# PCF Status: Active

**Parameters:**# PCF Morph Interval: 100

# ==========================

- `encrypted_stream`: Encrypted file-like object (opened in 'rb' mode)```

- `metadata`: Metadata bytes from encrypt_stream()

- `output_stream`: Output file-like object (opened in 'wb' mode)---

- `context_data`: Optional context (must match encryption)

- `password`: Decryption password (must match encryption)### Module Functions

- `chunk_size`: Size of chunks to process (default: 1 MB)

- `progress_callback`: Optional callback function `(current_bytes, total_bytes) -> None`#### initialize()



**Returns:** None (writes to output_stream)```python

initialize(

**Raises:**    seed: Union[str, bytes, int],

    lattice_size: int = 128,

- `ValueError`: If MAC verification fails or decryption fails    depth: int = 6,

    morph_interval: int = 100

**Example:**) -> STCContext

```

```python

ctx = STCContext('my-seed')Initialize STC context (convenience function).



# Load metadata**Parameters:** Same as `STCContext.__init__`

with open('encrypted.bin.meta', 'rb') as meta_file:

    metadata = meta_file.read()**Returns:** `STCContext` instance



# Define progress callback**Example:**

def progress(current, total):```python

    percent = (current / total) * 100from interfaces.api import stc_api

    print(f"Decrypting: {percent:.1f}%", end='\r')

ctx = stc_api.initialize(seed="my-seed")

# Decrypt large file```

with open('encrypted.bin', 'rb') as encrypted_file:

    with open('decrypted.bin', 'wb') as output_file:---

        ctx.decrypt_stream(

            encrypted_stream=encrypted_file,#### quick_encrypt()

            metadata=metadata,

            output_stream=output_file,```python

            password="strong_pw",quick_encrypt(

            progress_callback=progress    data: Union[str, bytes],

        )    seed: Union[str, bytes, int],

    password: Optional[str] = None,

print("\nDecryption complete!")    lattice_size: int = 128,

```    depth: int = 6

) -> Tuple[bytes, bytes, STCContext]

**Known Issue (v0.3.0):**```



Streaming decrypt may fail on files >100 MB. Use standard decrypt() for large files as workaround. Fixed in v0.3.1.One-liner encryption (creates context, encrypts, returns all).



---**Parameters:**

- `data`: Data to encrypt

#### get_entropy_health()- `seed`: Encryption seed

- `password`: Optional password (if None, uses seed)

```python- `lattice_size`: CEL lattice size (default: 128)

get_entropy_health() -> Dict[str, Any]- `depth`: CEL depth (default: 6)

```

**Returns:** Tuple of `(encrypted, metadata, context)`

**v0.3.0: NEW** - Get current CEL entropy health metrics.

**Example:**

**Returns:** Dict containing:```python

from interfaces.api import stc_api

```python

{encrypted, metadata, ctx = stc_api.quick_encrypt(

    'quality_score': float,        # 0.0-1.0 (0.7+ recommended)    "Secret data",

    'unique_ratio': float,         # 0.0-1.0 (unique values / total)    seed="my-seed",

    'distribution_score': float,   # 0.0-1.0 (statistical uniformity)    password="strong_pw"

    'update_count': int,           # Number of CEL updates performed)

    'status': str,                 # 'excellent' | 'good' | 'fair' | 'poor'```

    'recommendations': list        # Suggested actions

}---

```

#### quick_decrypt()

**Quality Thresholds:**

```python

- `excellent` (≥0.85): Ideal for encryption, no action neededquick_decrypt(

- `good` (0.70-0.84): Acceptable, continue normal operation    encrypted_data: bytes,

- `fair` (0.50-0.69): Marginal, consider calling update_cel()    metadata: Union[Dict[str, Any], bytes],

- `poor` (<0.50): Insufficient, MUST call update_cel() before encrypting    seed: Union[str, bytes, int],

    password: Optional[str] = None

**Example:**) -> Union[str, bytes]

```

```python

ctx = STCContext('my-seed')One-liner decryption (creates context from metadata, decrypts).



# Check health**Parameters:**

health = ctx.get_entropy_health()- `encrypted_data`: Encrypted bytes

- `metadata`: Metadata from encryption

print(f"Quality: {health['quality_score']:.2f}")- `seed`: Decryption seed (must match encryption)

print(f"Status: {health['status']}")- `password`: Optional password (must match encryption)

print(f"Unique ratio: {health['unique_ratio']:.2f}")

print(f"Updates: {health['update_count']}")**Returns:** Decrypted data



if health['recommendations']:**Raises:** `ValueError` if MAC verification fails

    print("Recommendations:")

    for rec in health['recommendations']:**Example:**

        print(f"  - {rec}")```python

from interfaces.api import stc_api

# Force update if poor

if health['quality_score'] < 0.5:decrypted = stc_api.quick_decrypt(

    ctx.cel.update()    encrypted,

    print("CEL updated!")    metadata,

```    seed="my-seed",

    password="strong_pw"

**Best Practice:**)

```

Check entropy health periodically (e.g., every 100 operations) to ensure encryption quality remains high.

---

---

## core.cel

#### hash()

### ContinuousEntropyLattice

```python

hash(Self-evolving 3D entropy lattice with timing-based entropy.

    data: Union[str, bytes],

    context_data: Optional[Dict[str, Any]] = None#### Constructor

) -> bytes

``````python

ContinuousEntropyLattice(

Generate probabilistic hash (CEL-driven, changes over time).    lattice_size: int = 256,

    depth: int = 8

**Parameters:**)

```

- `data`: Data to hash

- `context_data`: Optional additional context**Parameters:**

- `lattice_size`: Lattice dimension (NxN)

**Returns:** 32-byte hash value- `depth`: Lattice depth (Z dimension)



**Note:** Each call produces different hash due to CEL evolution. Not suitable for password verification unless CEL state is frozen.**Example:**

```python

**v0.3.0: Adaptive Difficulty** - PHE path count scales from 7→15 on oracle attack detection.from core.cel import ContinuousEntropyLattice



**Example:**cel = ContinuousEntropyLattice(lattice_size=128, depth=6)

cel.init('my-seed')

```python```

ctx = STCContext('hash-seed')

---

hash1 = ctx.hash("data")

hash2 = ctx.hash("data")#### init()



assert hash1 != hash2  # Different due to CEL evolution```python

assert len(hash1) == 32init(seed: Union[str, bytes, int]) -> None

```

# With context

hash_ctx = ctx.hash("data", context_data={'user': 'alice'})Initialize lattice from seed.

```

**Parameters:**

---- `seed`: Initialization seed



#### derive_key()---



```python#### update()

derive_key(

    length: int = 32,```python

    context_data: Optional[Dict[str, Any]] = Noneupdate(context: Optional[Dict[str, Any]] = None) -> None

) -> bytes```

```

Evolve lattice state (mixes timing, memory, and context entropy).

Derive cryptographic key using CKE.

**Parameters:**

**Parameters:**- `context`: Optional context data to mix in



- `length`: Key length in bytes (default: 32)---

- `context_data`: Optional additional context

#### snapshot()

**Returns:** Derived key (bytes of specified length)

```python

**Example:**snapshot() -> Dict[str, Any]

```

```python

ctx = STCContext('my-seed')Take snapshot of current lattice state.



# Derive 32-byte key**Returns:** Dict with lattice array, operation count, etc.

key = ctx.derive_key()

---

# Derive 64-byte key

key_64 = ctx.derive_key(length=64)#### restore_snapshot()



# With context```python

key_ctx = ctx.derive_key(context_data={'session': 'abc123'})restore_snapshot(snapshot: Dict[str, Any]) -> None

``````



---Restore lattice from snapshot.



#### save_state()**Parameters:**

- `snapshot`: Snapshot dict from snapshot()

```python

save_state() -> Dict[str, Any]---

```

#### extract_entropy()

Save current context state (CEL, PHE, PCF).

```python

**Returns:** Dict containing all component statesextract_entropy(

    length: int,

**Example:**    context: Optional[str] = None

) -> np.ndarray

```python```

ctx = STCContext('my-seed')

Extract entropy from lattice.

# Perform operations

ctx.hash("data1")**Parameters:**

ctx.hash("data2")- `length`: Number of entropy values to extract

- `context`: Optional context for extraction

# Save state

state = ctx.save_state()**Returns:** NumPy array of entropy values



# State keys---

print(state.keys())  # dict_keys(['cel_state', 'phe_state', 'pcf_state'])

```## core.phe



---### ProbabilisticHashingEngine



#### load_state()Multi-path probabilistic hashing with CEL integration.



```python#### Constructor

load_state(state: Dict[str, Any]) -> None

``````python

ProbabilisticHashingEngine()

Load previously saved context state.```



**Parameters:****Example:**

```python

- `state`: State dict from save_state()from core.phe import ProbabilisticHashingEngine



**Example:**phe = ProbabilisticHashingEngine()

```

```python

# Save state---

state = ctx.save_state()

#### digest()

# Create new context and load state

ctx2 = STCContext('my-seed')```python

ctx2.load_state(state)digest(

    data: Union[str, bytes],

# ctx2 now has same state as ctx    context: Optional[Dict[str, Any]] = None

```) -> bytes

```

---

Generate multi-path probabilistic hash.

#### get_status()

**Parameters:**

```python- `data`: Data to hash

get_status() -> str- `context`: Optional context

```

**Returns:** 32-byte hash

Get human-readable context status with v0.3.0 health metrics.

**Example:**

**Returns:** Formatted status string```python

phe = ProbabilisticHashingEngine()

**Example:**hash_value = phe.digest(b"data to hash")

```

```python

ctx = STCContext('my-seed')---

print(ctx.get_status())

#### map_entropy()

# Output:

# === STC Context Status ===```python

# CEL Operation Count: 10map_entropy(cel_snapshot: Dict[str, Any]) -> None

# CEL State Version: 5```

# CEL Lattice Size: 128x128x6

# Entropy Health: good (0.78)Bind PHE to CEL snapshot.

# PCF Status: Active

# PCF Morph Interval: 100 (adaptive)**Parameters:**

# ==========================- `cel_snapshot`: CEL snapshot from ContinuousEntropyLattice.snapshot()

```

---

---

#### trace()

### Module Functions

```python

#### initialize()trace() -> Dict[str, Any]

```

```python

initialize(Get PHE execution trace.

    seed: Union[str, bytes, int],

    lattice_size: int = 128,**Returns:** Dict with operation count, path history, etc.

    depth: int = 6,

    morph_interval: int = 100---

) -> STCContext

```## core.cke



Initialize STC context (convenience function).### ContextualKeyEmergence



**Parameters:** Same as `STCContext.__init__`Ephemeral key generation from context intersections.



**Returns:** `STCContext` instance#### Constructor



**Example:**```python

ContextualKeyEmergence()

```python```

from interfaces.api import stc_api

---

ctx = stc_api.initialize(seed="my-seed")

```#### derive()



---```python

derive(

#### quick_encrypt()    length: int = 32,

    context: Optional[Dict[str, Any]] = None,

```python    cel_snapshot: Optional[Dict[str, Any]] = None,

quick_encrypt(    phe_hash: Optional[bytes] = None

    data: Union[str, bytes],) -> bytes

    seed: Union[str, bytes, int],```

    password: Optional[str] = None,

    lattice_size: int = 128,Derive ephemeral key.

    depth: int = 6,

    **encrypt_options**Parameters:**

) -> Tuple[bytes, bytes, STCContext]- `length`: Key length in bytes

```- `context`: Optional context data

- `cel_snapshot`: Optional CEL snapshot

One-liner encryption (creates context, encrypts, returns all).- `phe_hash`: Optional PHE hash



**Parameters:****Returns:** Derived key (bytes)



- `data`: Data to encrypt---

- `seed`: Encryption seed

- `password`: Optional password (if None, uses seed)## utils.tlv_format

- `lattice_size`: CEL lattice size (default: 128)

- `depth`: CEL depth (default: 6)### serialize_metadata_tlv()

- `**encrypt_options`: **v0.3.0: Additional options** (e.g., use_decoys, num_decoys, variable_decoy_sizes)

```python

**Returns:** Tuple of `(encrypted, metadata, context)`serialize_metadata_tlv(metadata: Dict[str, Any]) -> bytes

```

**Example:**

Serialize metadata to binary TLV format.

```python

from interfaces.api import stc_api**Parameters:**

- `metadata`: Metadata dict

# v0.3.0: Full security (default)

encrypted, metadata, ctx = stc_api.quick_encrypt(**Returns:** Binary TLV bytes

    "Secret data",

    seed="my-seed",---

    password="strong_pw"

)### deserialize_metadata_tlv()



# Custom decoy configuration```python

encrypted, metadata, ctx = stc_api.quick_encrypt(deserialize_metadata_tlv(tlv_bytes: bytes) -> Dict[str, Any]

    "Data",```

    seed="seed",

    password="pw",Deserialize TLV bytes to metadata dict.

    num_decoys=5,

    variable_decoy_sizes=True,**Parameters:**

    randomize_decoy_count=True- `tlv_bytes`: Binary TLV data

)

```**Returns:** Metadata dict



---**Raises:**

- `ValueError`: If TLV format invalid

#### quick_decrypt()- `Exception`: If version unsupported



```python---

quick_decrypt(

    encrypted_data: bytes,## Performance Metrics (v0.2.0)

    metadata: Union[Dict[str, Any], bytes],

    seed: Union[str, bytes, int],Default parameters (`lattice_size=128, depth=6`):

    password: Optional[str] = None- **Encryption**: ~1.3s for small messages

) -> Union[str, bytes]- **Decryption**: ~0.9s for small messages

```- **Metadata Size**: ~786 KB (constant)

- **Hash Generation**: ~0.05s per hash

One-liner decryption (creates context from metadata, decrypts).

See [PERFORMANCE_OPTIMIZATIONS.md](../PERFORMANCE_OPTIMIZATIONS.md) for detailed benchmarks.

**Parameters:**

---

- `encrypted_data`: Encrypted bytes

- `metadata`: Metadata from encryption## Version Compatibility

- `seed`: Decryption seed (must match encryption)

- `password`: Optional password (must match encryption)### v0.2.0 Features



**Returns:** Decrypted data- Password-based encryption with MAC verification

- Binary TLV metadata format (~786 KB vs 4 MB)

**Raises:** `ValueError` if MAC verification fails- Metadata encryption with ephemeral keys

- Automatic version detection (v0.1.x JSON vs v0.2.0 TLV)

**Example:**- 76x performance improvement over v0.2.0-alpha



```python### Backward Compatibility

from interfaces.api import stc_api

```python

decrypted = stc_api.quick_decrypt(# v0.1.x JSON metadata still supported

    encrypted,ctx = STCContext('seed')

    metadata,decrypted = ctx.decrypt(encrypted, old_json_metadata)

    seed="my-seed",

    password="strong_pw"# v0.2.0 TLV metadata

)decrypted = ctx.decrypt(encrypted, new_tlv_metadata)

```

# Auto-detection handles both

---```



## core.cel---



### ContinuousEntropyLattice## Error Codes



Self-evolving 3D entropy lattice with timing-based entropy and health monitoring.| Error | Cause | Solution |

|-------|-------|----------|

#### Constructor| `ValueError: MAC verification failed` | Wrong password or data tampered | Check password, verify data integrity |

| `KeyError: 'vectors'` | Trying to use decoy vectors | Set `use_decoys=False` |

```python| `ValueError: Invalid lattice size` | lattice_size out of range (16-256) | Use valid range |

ContinuousEntropyLattice(| `TypeError: data must be str or bytes` | Invalid data type | Convert to str or bytes |

    lattice_size: int = 256,

    depth: int = 8---

)

```## See Also



**Parameters:**- [Usage Guide](usage-guide.md) - Practical examples and patterns

- [Architecture](architecture.md) - System design and components

- `lattice_size`: Lattice dimension (NxN)- [CHANGELOG](../CHANGELOG.md) - Version history

- `depth`: Lattice depth (Z dimension)- [PERFORMANCE_OPTIMIZATIONS](../PERFORMANCE_OPTIMIZATIONS.md) - Optimization details


**Example:**

```python
from core.cel import ContinuousEntropyLattice

cel = ContinuousEntropyLattice(lattice_size=128, depth=6)
cel.init('my-seed')
```

---

#### init()

```python
init(seed: Union[str, bytes, int]) -> None
```

Initialize lattice from seed.

**Parameters:**

- `seed`: Initialization seed

---

#### update()

```python
update(context: Optional[Dict[str, Any]] = None) -> None
```

Evolve lattice state (mixes timing, memory, and context entropy).

**Parameters:**

- `context`: Optional context data to mix in

**v0.3.0:** Also updates entropy health metrics.

---

#### get_entropy_health()

```python
get_entropy_health() -> Dict[str, Any]
```

**v0.3.0: NEW** - Calculate comprehensive entropy health metrics.

**Returns:** Dict with quality_score, unique_ratio, distribution_score, status, recommendations

See `STCContext.get_entropy_health()` for detailed format.

---

#### snapshot()

```python
snapshot() -> Dict[str, Any]
```

Take snapshot of current lattice state.

**Returns:** Dict with lattice array, operation count, seed, update_count

**v0.3.0:** Snapshot can be compressed for metadata storage (see StateManager).

---

#### restore_snapshot()

```python
restore_snapshot(snapshot: Dict[str, Any]) -> None
```

Restore lattice from snapshot.

**Parameters:**

- `snapshot`: Snapshot dict from snapshot()

---

#### extract_entropy()

```python
extract_entropy(
    length: int,
    context: Optional[str] = None
) -> np.ndarray
```

Extract entropy from lattice.

**Parameters:**

- `length`: Number of entropy values to extract
- `context`: Optional context for extraction

**Returns:** NumPy array of entropy values

---

## core.phe

### ProbabilisticHashingEngine

Multi-path probabilistic hashing with CEL integration and adaptive difficulty.

#### Constructor

```python
ProbabilisticHashingEngine()
```

**Example:**

```python
from core.phe import ProbabilisticHashingEngine

phe = ProbabilisticHashingEngine()
```

---

#### digest()

```python
digest(
    data: Union[str, bytes],
    context: Optional[Dict[str, Any]] = None,
    num_paths: int = 7  # v0.3.0: Adaptive (7-15)
) -> bytes
```

Generate multi-path probabilistic hash with adaptive difficulty.

**Parameters:**

- `data`: Data to hash
- `context`: Optional context
- `num_paths`: **v0.3.0: Number of hash paths** (7-15, scales on oracle attack)

**Returns:** 32-byte hash

**Example:**

```python
phe = ProbabilisticHashingEngine()

# Standard hash (7 paths)
hash_value = phe.digest(b"data to hash")

# Increased difficulty (15 paths)
hash_secure = phe.digest(b"data", num_paths=15)
```

**v0.3.0: Oracle Attack Detection:**

Automatically increases num_paths from 7→15 on detection of:

- Rapid sequential hash requests (>10 in <1 second)
- Identical context_data with different inputs
- High request frequency

---

#### map_entropy()

```python
map_entropy(cel_snapshot: Dict[str, Any]) -> None
```

Bind PHE to CEL snapshot.

**Parameters:**

- `cel_snapshot`: CEL snapshot from ContinuousEntropyLattice.snapshot()

---

#### trace()

```python
trace() -> Dict[str, Any]
```

Get PHE execution trace.

**Returns:** Dict with operation count, path history, adaptive difficulty state

**v0.3.0:** Includes oracle attack detection metrics.

---

## core.cke

### ContextualKeyEmergence

Ephemeral key generation from context intersections with streaming support.

#### Constructor

```python
ContextualKeyEmergence()
```

---

#### derive()

```python
derive(
    length: int = 32,
    context: Optional[Dict[str, Any]] = None,
    cel_snapshot: Optional[Dict[str, Any]] = None,
    phe_hash: Optional[bytes] = None
) -> bytes
```

Derive ephemeral key.

**Parameters:**

- `length`: Key length in bytes
- `context`: Optional context data
- `cel_snapshot`: Optional CEL snapshot
- `phe_hash`: Optional PHE hash

**Returns:** Derived key (bytes)

**v0.3.0:** Supports streaming key derivation for encrypt_stream() / decrypt_stream().

---

## core.state

### StateManager

CEL state serialization with compression.

#### compress_lattice()

```python
compress_lattice(lattice: np.ndarray) -> bytes
```

**v0.3.0: NEW** - Compress lattice using RLE + varint encoding.

**Parameters:**

- `lattice`: NumPy array to compress

**Returns:** Compressed bytes

**Compression Ratio:**

- Typical: 51% reduction (~950 KB → ~465 KB)
- Decompression overhead: <10ms

---

#### decompress_lattice()

```python
decompress_lattice(compressed: bytes, shape: Tuple[int, ...]) -> np.ndarray
```

**v0.3.0: NEW** - Decompress lattice from RLE + varint.

**Parameters:**

- `compressed`: Compressed bytes from compress_lattice()
- `shape`: Original lattice shape (e.g., (128, 128, 6))

**Returns:** Decompressed NumPy array

---

## utils.tlv_format

### serialize_metadata_tlv()

```python
serialize_metadata_tlv(metadata: Dict[str, Any]) -> bytes
```

Serialize metadata to binary TLV format.

**Parameters:**

- `metadata`: Metadata dict (may include compressed lattices in v0.3.0)

**Returns:** Binary TLV bytes

**v0.3.0:** Supports compressed lattices, decoy configurations, entropy health.

---

### deserialize_metadata_tlv()

```python
deserialize_metadata_tlv(tlv_bytes: bytes) -> Dict[str, Any]
```

Deserialize TLV bytes to metadata dict.

**Parameters:**

- `tlv_bytes`: Binary TLV data

**Returns:** Metadata dict

**Raises:**

- `ValueError`: If TLV format invalid
- `Exception`: If version unsupported

**v0.3.0:** Auto-detects v0.1.x JSON, v0.2.x TLV, v0.3.0 TLV with compression.

---

## Performance Metrics (v0.3.0)

Default parameters (`lattice_size=128, depth=6, use_decoys=True, num_decoys=3`):

**Encryption:**

- Small messages (<10 KB): ~1.8 seconds
- Real CEL generation: ~0.81s
- Decoy generation (3x 64×64×4): ~0.42s
- DSF folding: ~0.3s
- Metadata compression: ~0.05s

**Decryption:**

- Small messages: ~0.9s
- Metadata decompression: ~0.01s
- Trial decryption (3 decoys): ~0.5s
- DSF unfolding: ~0.3s

**Streaming:**

- 100 MB file: ~180 seconds
- Memory usage: ~8 MB (constant)

**Metadata:**

- Uncompressed: ~950 KB
- Compressed (v0.3.0): ~486 KB (51% reduction)
- With 7 decoys: ~680 KB compressed

**Entropy Health:**

- Health check: ~60ms
- Negligible overhead

See [docs/PERFORMANCE.md](PERFORMANCE.md) for detailed benchmarks and optimization guide.

---

## Version Compatibility

### v0.3.0 Changes

**New Features:**

- Entropy Health API (`get_entropy_health()`)
- Polymorphic decoy system with variable sizes
- Streaming encryption/decryption
- Metadata compression (RLE + varint)
- Adaptive morphing (CEL-delta-driven)
- Adaptive difficulty (oracle attack detection)

**Breaking Changes:**

- `use_decoys=True` by default (was False)
- Metadata format changed (includes compression info)
- Streaming API added (new methods)

**Backward Compatibility:**

```python
# v0.1.x JSON metadata still supported
ctx = STCContext('seed')
decrypted = ctx.decrypt(encrypted, old_json_metadata)

# v0.2.x TLV metadata still supported
decrypted = ctx.decrypt(encrypted, v2_metadata)

# v0.3.0 compressed metadata
decrypted = ctx.decrypt(encrypted, v3_metadata)

# Auto-detection handles all versions
```

**Migration from v0.2.x:**

See [migration-guide.md](migration-guide.md) for detailed upgrade instructions.

---

## Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: MAC verification failed` | Wrong password or data tampered | Check password, verify data integrity |
| `ValueError: Entropy quality too low (<0.5)` | Insufficient entropy health | Call `cel.update()` before encrypting |
| `ValueError: Invalid lattice size` | lattice_size out of range (16-256) | Use valid range |
| `TypeError: data must be str or bytes` | Invalid data type | Convert to str or bytes |
| `Exception: Streaming decrypt failed` | Known v0.3.0 issue with large files | Use standard decrypt() as workaround |

---

## See Also

- **[Usage Guide](usage-guide.md)** - Practical examples and patterns
- **[Architecture](architecture.md)** - System design and components
- **[Security Guide](security-guide.md)** - Best practices and threat model
- **[User Manual](user_manual/)** - Beginner-friendly guides
- **[CHANGELOG](../CHANGELOG.md)** - Version history
- **[PERFORMANCE](PERFORMANCE.md)** - Optimization strategies
