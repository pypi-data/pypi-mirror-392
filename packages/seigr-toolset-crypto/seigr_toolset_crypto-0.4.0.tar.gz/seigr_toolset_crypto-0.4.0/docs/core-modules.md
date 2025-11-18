# Core Modules - STC v0.3.0# Core Modules



Detailed technical specifications for STC v0.3.0 "Adaptive Security & Transparency" core modules with entropy health monitoring, polymorphic decoys, adaptive features, and streaming support.Detailed specifications for STC core modules.



## Module Overview## Continuous Entropy Lattice (CEL)



```text**File**: `core/cel/cel.py`

CEL (Continuous Entropy Lattice) - Base entropy source with health monitoring

 ├─► PHE (Probabilistic Hashing Engine) - Adaptive difficulty hashing### Purpose

 │    └─► CKE (Contextual Key Emergence) - Context-aware key derivation

 │         └─► DSF (Data-State Folding) - Multi-stage encryptionProvides self-evolving entropy source without external randomness.

 ├─► CKE (Direct key derivation from CEL)

 │    └─► DSF (Encryption/decryption)### Implementation Details

 └─► DSF (Direct entropy access for folding)

#### Lattice Structure

PCF (Polymorphic Cryptographic Flow) - Adaptive morphing (CEL-delta-driven)- **Type**: 3D NumPy array (`np.ndarray`)

STATE (State Management) - Serialization with RLE + varint compression- **Shape**: `(size, size, depth)` - default `(256, 256, 8)`

UTILS (Mathematical Primitives) - Pure integer arithmetic functions- **Data Type**: `uint64`

DecoyManager (v0.3.0) - Polymorphic decoy generation and management- **Total Cells**: 524,288 for default configuration

```- **Memory**: ~4 MB for default lattice



---#### Initialization



## Continuous Entropy Lattice (CEL)1. Seed conversion to integer:

   - String → UTF-8 bytes → integer via `int.from_bytes()`

**File**: `core/cel/cel.py`     - Bytes → integer directly

**Class**: `ContinuousEntropyLattice`     - Integer → used as-is

**Version**: v0.3.0 with entropy health monitoring

2. Lattice generation:

### Purpose   ```python

   # For each cell (i, j, k):

Self-evolving 3D entropy source without external randomness, featuring comprehensive health metrics and quality monitoring.   base = (seed + i * size + j) % PRIME

   exponent = (k + 1) % PRIME

### Lattice Configurations   lattice[i, j, k] = pow(base, exponent, PRIME)

   ```

#### Primary (Encryption) Lattice   where `PRIME = 65521` (largest prime < 2^16)



```python3. Initial diffusion:

size: 128              # Dimension (NxN)   - 3 rounds of non-linear diffusion

depth: 6               # Z-axis layers   - Prevents zero-valued cells

shape: (128, 128, 6)   - Spreads seed influence across lattice

total_cells: 98,304

memory: ~7.5 MB#### State Evolution

data_type: uint64

```Triggered by `update()` call:



#### Decoy Lattices (v0.3.0)1. Calculate time delta:

   ```python

```python   current_time = time.perf_counter()

# Optimization: Smaller lattices for decoys   delta_t = current_time - last_update_time

size: 64               # Dimension (NxN)   time_factor = int((delta_t * 1e9) % PRIME)

depth: 4               # Z-axis layers   ```

shape: (64, 64, 4)

total_cells: 16,3842. Apply non-linear diffusion:

memory: ~1 MB each   - Each cell influenced by 6 neighbors (±x, ±y, ±z)

count: 3-7 (configurable + randomization)   - Weighted combination: `(sum_neighbors * time_factor) % PRIME`

   - 1 round per update

# Performance: 5.8x faster generation

# Primary CEL: ~0.81s3. Increment update counter

# Decoy CEL: ~0.14s each

```#### Entropy Extraction



### Implementation Details`get_entropy(length)` method:



#### Initialization1. Flatten lattice to 1D array

2. Take first `length` values

**Seed Processing**:3. Return as uint64 NumPy array

4. Call `update()` after extraction

```python

def _seed_to_int(seed: Union[str, bytes, int]) -> int:### Constants

    if isinstance(seed, str):

        return int.from_bytes(seed.encode('utf-8'), 'big') % PRIME```python

    elif isinstance(seed, bytes):PRIME = 65521           # Modulus for all operations

        return int.from_bytes(seed, 'big') % PRIMEDEFAULT_SIZE = 256      # Lattice dimension

    else:DEFAULT_DEPTH = 8       # Lattice depth layers

        return seed % PRIMEDIFFUSION_ROUNDS = 3    # Initial diffusion rounds

``````



**Lattice Generation**:### Thread Safety



```python**Not thread-safe**. Concurrent `update()` calls cause race conditions on:

# Using np.random.RandomState for deterministic generation- `lattice` array

rng = np.random.RandomState(seed_int)- `last_update_time`

lattice = rng.randint(0, PRIME, size=(size, size, depth), dtype=np.uint64)- `update_count`



# Initial diffusion (3 rounds)---

for _ in range(3):

    lattice = non_linear_diffusion(lattice)## Probabilistic Hashing Engine (PHE)

```

**File**: `core/phe/phe.py`

**Constants**:

### Purpose

```python

PRIME = 65521          # Largest prime < 2^16Generates hashes influenced by CEL state, producing different outputs over time for same input.

DEFAULT_SIZE = 128     # v0.3.0: Changed from 256

DEFAULT_DEPTH = 6      # v0.3.0: Changed from 8### Implementation Details

DIFFUSION_ROUNDS = 3   # Initial mixing rounds

```#### Hash Generation Process



#### State Evolution1. Update CEL state:

   ```python

**Update Process** (triggered by `update()` call):   self.cel.update()

   ```

```python

def update(self, context: Optional[Dict[str, Any]] = None) -> None:2. Convert input to bytes:

    # 1. Calculate timing delta   - String → UTF-8 bytes

    current_time = time.perf_counter()   - Bytes → as-is

    delta_t = current_time - self.last_update_time

    time_factor = int((delta_t * 1e9) % PRIME)3. Get CEL entropy:

       ```python

    # 2. Apply non-linear diffusion   entropy = self.cel.get_entropy(32)  # 32 uint64 values

    self.lattice = non_linear_diffusion(self.lattice, rounds=1)   ```

    

    # 3. Mix in timing entropy4. Combine data with entropy:

    for i in range(self.size):   ```python

        for j in range(self.size):   for i, byte in enumerate(data_bytes):

            for k in range(self.depth):       combined = (byte + entropy[i % 32]) % 256

                self.lattice[i, j, k] = (       hash_value.append(combined)

                    self.lattice[i, j, k] + time_factor   ```

                ) % PRIME

    5. Apply context if provided:

    # 4. Context mixing (if provided)   ```python

    if context:   if context:

        context_hash = hash(str(context))       context_bytes = str(context).encode()

        context_factor = context_hash % PRIME       for i, ctx_byte in enumerate(context_bytes):

        self.lattice = (self.lattice + context_factor) % PRIME           hash_value[i % 32] ^= ctx_byte

       ```

    # 5. Update counters

    self.update_count += 16. Return first 32 bytes

    self.last_update_time = current_time

    ### Properties

    # 6. Update health metrics (v0.3.0)

    self._update_health_metrics()- **Output Size**: Always 32 bytes

```- **Determinism**: Same input + same CEL state = same hash

- **Time Variance**: Different CEL state → different hash

**Timing Entropy**:- **Collision Resistance**: Depends on CEL entropy quality



- Uses `time.perf_counter()` for microsecond precision### Use Cases

- Delta converted to nanoseconds: `delta_t * 1e9`

- Modulo PRIME prevents overflow- Password verification (with static CEL state)

- Different timing = different evolution- Data fingerprinting

- Context-aware hashing

#### Entropy Extraction- Not suitable for: blockchain, Merkle trees, or applications requiring deterministic hashing



```python---

def get_entropy(self, length: int) -> np.ndarray:

    """## Contextual Key Emergence (CKE)

    Extract entropy from lattice

    **File**: `core/cke/cke.py`

    Args:

        length: Number of uint64 values to extract### Purpose

    

    Returns:Derives encryption keys from CEL state and optional context data.

        NumPy array of entropy values

    """### Implementation Details

    # Flatten lattice to 1D

    flat = self.lattice.flatten()#### Key Derivation Process

    

    # Take first 'length' values1. Hash context data (if provided):

    entropy = flat[:length].copy()   ```python

       if context_data:

    # Update state after extraction       context_hash = self.phe.hash(str(context_data))

    self.update()   ```

    

    return entropy2. Get CEL entropy:

```   ```python

   base_entropy = self.cel.get_entropy(key_length)

**Properties**:   ```



- Extraction triggers automatic state update3. Combine entropy with context:

- Returns copy (prevents external modification)   ```python

- Values in range [0, PRIME-1]   for i in range(key_length):

       if context_data:

#### Entropy Health API (v0.3.0)           key_vector[i] = (base_entropy[i] + context_hash[i]) % PRIME

       else:

**Comprehensive Health Metrics**:           key_vector[i] = base_entropy[i] % PRIME

   ```

```python

def get_entropy_health(self) -> Dict[str, Any]:4. Return key as NumPy array copy

    """

    Calculate comprehensive entropy quality metrics### Key Properties

    

    Returns:- **Length**: Configurable (default 32 bytes)

        {- **Type**: `np.ndarray` of `uint64`

            'quality_score': float,        # 0.0-1.0 overall quality- **Range**: Values in [0, 65520] (mod PRIME)

            'unique_ratio': float,         # Unique values / total- **Ephemeral**: Not stored, regenerated on demand

            'distribution_score': float,   # Statistical uniformity

            'update_count': int,           # Number of updates### Important Notes

            'status': str,                 # Classification

            'recommendations': list        # Suggested actions**Fixed in v0.1.0**: `derive()` now returns `key_vector.copy()` instead of reference. This prevents external modification of internal state.

        }

    """---

    flat = self.lattice.flatten()

    total_values = len(flat)## Data-State Folding (DSF)

    

    # 1. Unique ratio (diversity metric)**File**: `core/dsf/dsf.py`

    unique_values = len(np.unique(flat))

    unique_ratio = unique_values / total_values### Purpose

    

    # 2. Distribution score (uniformity metric)Encrypts data via multidimensional tensor transformations.

    histogram, _ = np.histogram(flat, bins=100, range=(0, PRIME))

    expected_count = total_values / 100### Implementation Details

    deviations = np.abs(histogram - expected_count)

    distribution_score = 1.0 - (np.mean(deviations) / expected_count)#### Encryption: fold()

    

    # 3. Overall quality score (weighted combination)1. **Tensor Preparation**:

    quality_score = (unique_ratio * 0.6) + (distribution_score * 0.4)   ```python

       # Calculate tensor dimensions

    # 4. Status classification   total_size = len(data)

    if quality_score >= 0.85:   height = int(np.ceil(np.sqrt(total_size)))

        status = 'excellent'   width = height

    elif quality_score >= 0.70:   

        status = 'good'   # Pad data to fit tensor

    elif quality_score >= 0.50:   padded_size = height * width

        status = 'fair'   padded_data = data + b'\x00' * (padded_size - total_size)

    else:   

        status = 'poor'   # Reshape to 2D tensor

       tensor = np.frombuffer(padded_data, dtype=np.uint8).reshape(height, width)

    # 5. Recommendations   ```

    recommendations = []

    if quality_score < 0.5:2. **Apply 5 Folding Strategies**:

        recommendations.append("CRITICAL: Force update before encryption")

    elif quality_score < 0.7:   **a. Rotation** (circular shift):

        recommendations.append("Consider calling update() to refresh entropy")   ```python

    if unique_ratio < 0.4:   shift = int(key[0] % height)

        recommendations.append("Low diversity - increase update frequency")   tensor = np.roll(tensor, shift, axis=0)

    if distribution_score < 0.6:   tensor = np.roll(tensor, shift, axis=1)

        recommendations.append("Non-uniform distribution - check update patterns")   ```

       

    return {   **b. Permutation** (row/column shuffle):

        'quality_score': quality_score,   ```python

        'unique_ratio': unique_ratio,   seed = int(key[1])

        'distribution_score': distribution_score,   rng = np.random.RandomState(seed)

        'update_count': self.update_count,   row_order = rng.permutation(height)

        'status': status,   col_order = rng.permutation(width)

        'recommendations': recommendations   tensor = tensor[row_order, :]

    }   tensor = tensor[:, col_order]

```   ```

   

**Quality Interpretation**:   **c. Compression** (modular mixing):

   ```python

| Score | Status | Meaning | Action |   for i in range(height):

|-------|--------|---------|--------|       for j in range(width):

| ≥0.85 | Excellent | Ideal entropy quality | No action needed |           tensor[i, j] = (tensor[i, j] + key[(i+j) % len(key)]) % 256

| 0.70-0.84 | Good | Acceptable for encryption | Continue normal operation |   ```

| 0.50-0.69 | Fair | Marginal quality | Consider update() |   

| <0.50 | Poor | Insufficient entropy | **MUST update() before encrypt** |   **d. Diffusion** (non-linear mixing):

   ```python

**Typical Values** (after 10+ updates):   tensor = math_primitives.non_linear_diffusion(tensor, rounds=3)

   ```

- Unique ratio: 0.45-0.55 (51% unique in v0.3.0 benchmarks)   

- Distribution score: 0.75-0.85   **e. Entropy Weighting** (CEL integration):

- Quality score: 0.70-0.80   ```python

   cel_entropy = self.cel.get_entropy(height * width)

#### Snapshot and Restore   entropy_weights = (cel_entropy % 256).reshape(height, width)

   tensor = ((tensor.astype(np.uint16) * entropy_weights) % 256).astype(np.uint8)

```python   ```

def snapshot(self) -> Dict[str, Any]:

    """Take complete CEL state snapshot"""3. **Flatten and Return**:

    return {   ```python

        'lattice': self.lattice.copy(),  # Full lattice copy   return tensor.flatten().tobytes()

        'size': self.size,   ```

        'depth': self.depth,

        'seed': self.seed,#### Decryption: unfold()

        'update_count': self.update_count,

        'last_update_time': self.last_update_timeReverses operations in exact opposite order:

    }

1. Reshape to tensor

def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:2. Reverse entropy weighting (modular inverse)

    """Restore CEL from snapshot"""3. Reverse diffusion

    self.lattice = snapshot['lattice'].copy()4. Reverse compression

    self.size = snapshot['size']5. Reverse permutation (inverse order)

    self.depth = snapshot['depth']6. Reverse rotation (negative shift)

    self.seed = snapshot['seed']7. Trim to original length

    self.update_count = snapshot['update_count']

    self.last_update_time = snapshot['last_update_time']### Critical Requirements

```

- **Integer-Only Operations**: All arithmetic uses modulo 256 or PRIME

**v0.3.0 Enhancement**: Snapshots can be compressed via StateManager for 51% size reduction.- **No Rounding**: Eliminated in v0.1.0 to ensure perfect reversibility

- **CEL State Match**: Decryption requires exact CEL state from encryption

### Thread Safety- **Key Match**: Same key must be used for fold/unfold



**Status**: Not thread-safe### Performance



**Unsafe Operations**:- **Fold Time**: ~50-200 ms for <10 KB data

- **Memory**: ~2x input size during processing

- `self.lattice` mutations during concurrent `update()`- **Overhead**: Metadata ~10-20 KB (CEL snapshot)

- `self.last_update_time` race conditions

- `self.update_count` race conditions---



**Recommendations**:## Polymorphic Cryptographic Flow (PCF)



- Use separate CEL instances per thread**File**: `core/pcf/pcf.py`

- Implement read-write locks for shared instances (planned v0.3.1)

- Use thread-local storage for contexts### Purpose



---Tracks operation count and provides morphing state for algorithm adaptation.



## Probabilistic Hashing Engine (PHE)### Implementation Details



**File**: `core/phe/phe.py`  #### State Tracking

**Class**: `ProbabilisticHashingEngine`  

**Version**: v0.3.0 with adaptive difficulty scaling```python

class PolymorphicCryptographicFlow:

### Purpose    def __init__(self, morph_interval: int = 100):

        self.operation_count = 0

Generates non-deterministic hashes influenced by CEL state, with oracle attack detection and adaptive computational difficulty.        self.morph_interval = morph_interval

        self.current_morph = 0

### Implementation Details```



#### Hash Generation Process#### Methods



```python**update()**:

def digest(```python

    self,def update(self):

    data: Union[str, bytes],    self.operation_count += 1

    context: Optional[Dict[str, Any]] = None,    if self.operation_count % self.morph_interval == 0:

    num_paths: int = 7  # v0.3.0: Adaptive 7-15        self.current_morph += 1

) -> bytes:```

    """

    Generate multi-path probabilistic hash**get_morph_state()**:

    ```python

    Args:def get_morph_state() -> int:

        data: Data to hash    return self.current_morph

        context: Optional context for key derivation```

        num_paths: Number of hash paths (adaptive in v0.3.0)

    ### Current Usage

    Returns:

        32-byte hash valueIn v0.1.0, PCF is **initialized but not actively used** in encryption/decryption logic. It's present for future algorithm morphing implementations.

    """

    # 1. Update CEL state### Future Use Cases

    self.cel.update(context)

    - Algorithm selection based on morph state

    # 2. Convert data to bytes- Dynamic folding strategy changes

    if isinstance(data, str):- Adaptive security parameter adjustment

        data_bytes = data.encode('utf-8')

    else:---

        data_bytes = data

    ## State Management

    # 3. Multi-path hashing (v0.3.0: adaptive num_paths)

    paths = []**File**: `core/state/state.py`

    for path_idx in range(num_paths):

        # Get path-specific CEL entropy### Purpose

        entropy = self.cel.get_entropy(32)

        Serializes and deserializes CEL state for metadata storage.

        # Combine data with entropy

        path_hash = bytearray(32)### Implementation Details

        for i, byte in enumerate(data_bytes):

            path_hash[i % 32] ^= byte#### Serialization

            path_hash[i % 32] = (path_hash[i % 32] + entropy[i % 32]) % 256

        ```python

        paths.append(bytes(path_hash))@staticmethod

    def serialize_state(cel: ContinuousEntropyLattice) -> Dict[str, Any]:

    # 4. Combine all paths (XOR reduction)    snapshot = cel.get_snapshot()

    final_hash = bytearray(32)    return {

    for path in paths:        'lattice': snapshot['lattice'].tolist(),  # NumPy array → Python list

        for i in range(32):        'size': snapshot['size'],

            final_hash[i] ^= path[i]        'depth': snapshot['depth'],

            'seed': snapshot['seed'],

    # 5. Context mixing (if provided)        'update_count': snapshot['update_count']

    if context:    }

        context_bytes = str(context).encode()```

        for i, ctx_byte in enumerate(context_bytes):

            final_hash[i % 32] ^= ctx_byte#### Deserialization

    

    return bytes(final_hash)```python

```@staticmethod

def deserialize_state(state_dict: Dict[str, Any]) -> ContinuousEntropyLattice:

#### Adaptive Difficulty Scaling (v0.3.0)    # Create new CEL with same parameters

    cel = ContinuousEntropyLattice(

**Oracle Attack Detection**:        seed=state_dict['seed'],

        size=state_dict['size'],

```python        depth=state_dict['depth']

class OracleDetector:    )

    def __init__(self):    

        self.request_times = []    # Restore lattice from list

        self.context_patterns = {}    lattice_array = np.array(state_dict['lattice'], dtype=np.uint64)

        self.attack_threshold = 10  # Requests per second    

        # Restore snapshot

    def detect_attack(    cel.restore_from_snapshot({

        self,        'lattice': lattice_array,

        context_data: Optional[Dict[str, Any]]        'size': state_dict['size'],

    ) -> bool:        'depth': state_dict['depth'],

        """Detect potential oracle attack patterns"""        'seed': state_dict['seed'],

        current_time = time.time()        'update_count': state_dict['update_count']

            })

        # 1. Clean old requests (>1 second old)    

        self.request_times = [    return cel

            t for t in self.request_times ```

            if current_time - t < 1.0

        ]### JSON Compatibility

        

        # 2. Record current request- Converts NumPy arrays to nested Python lists

        self.request_times.append(current_time)- All numeric types remain JSON-compatible

        - Enables metadata storage in JSON files

        # 3. Check request frequency

        if len(self.request_times) > self.attack_threshold:### Size Considerations

            return True  # High frequency attack

        Default lattice (256×256×8):

        # 4. Check context pattern repetition- Raw size: 524,288 uint64 values

        if context_data:- JSON size: ~10-15 KB (compressed with integer serialization)

            ctx_key = str(context_data)- Dominates metadata size

            self.context_patterns[ctx_key] = (

                self.context_patterns.get(ctx_key, 0) + 1---

            )

            if self.context_patterns[ctx_key] > 5:## Mathematical Primitives

                return True  # Repeated context attack

        **File**: `utils/math_primitives.py`

        return False

```### Functions



**Adaptive Response**:#### modular_exponentiation

```python

```pythondef modular_exponentiation(base: int, exponent: int, modulus: int) -> int

def adaptive_digest(```

    self,

    data: Union[str, bytes],Fast modular exponentiation using binary method.

    context: Optional[Dict[str, Any]] = None

) -> bytes:**Usage**: CEL lattice initialization

    """Hash with adaptive difficulty"""

    # Detect attack**Example**:

    is_attack = self.oracle_detector.detect_attack(context)```python

    result = modular_exponentiation(5, 100, 65521)  # 5^100 mod 65521

    if is_attack:```

        # Increase difficulty

        num_paths = min(15, 7 + self.attack_count)#### modular_inverse

        self.attack_count += 1```python

        def modular_inverse(a: int, m: int) -> int

        # Add timing jitter```

        time.sleep(random.uniform(0.0001, 0.001))

    else:Computes modular multiplicative inverse using Extended Euclidean Algorithm.

        # Normal operation

        num_paths = 7**Usage**: DSF entropy weight reversal

        self.attack_count = max(0, self.attack_count - 1)

    **Example**:

    return self.digest(data, context, num_paths)```python

```inv = modular_inverse(7, 65521)  # 7^-1 mod 65521

```

**Difficulty Levels**:

#### non_linear_diffusion

| Level | Paths | Time | Security |```python

|-------|-------|------|----------|def non_linear_diffusion(matrix: np.ndarray, rounds: int = 1) -> np.ndarray

| Normal | 7 | ~50ms | Standard |```

| Elevated | 10 | ~70ms | Increased |

| Maximum | 15 | ~100ms | Maximum |Applies cellular automaton-like diffusion to 2D matrix.



**Attack Mitigation**:**Process**:

1. For each cell, compute weighted sum of neighbors

- **Computational cost**: Doubles from 7→15 paths2. Apply modular arithmetic

- **Timing randomization**: 0.1-1.0ms random delay3. Repeat for specified rounds

- **Cooldown**: Decreases difficulty after attack stops

- **Reset**: Returns to normal after 10 seconds no attack**Fixed in v0.1.0**: Now uses separate result matrix per iteration to avoid in-place modification bugs.



### Properties#### tensor_permutation

```python

- **Output Size**: Always 32 bytesdef tensor_permutation(tensor: np.ndarray, seed: int) -> Tuple[np.ndarray, np.ndarray]

- **Determinism**: Same input + CEL state + paths = same hash```

- **Time Variance**: CEL evolution → different hashes

- **Collision Resistance**: Depends on CEL entropy quality and path countDeterministic tensor shuffling.



### Use Cases**Returns**: (permuted_tensor, inverse_permutation_indices)



✅ **Suitable for**:**Usage**: DSF permutation strategy



- Message authentication codes (with fixed CEL)#### safe_index

- Data fingerprinting (with CEL evolution)```python

- Challenge-response protocolsdef safe_index(tensor: np.ndarray, indices: Tuple[int, ...]) -> Any

- Context-aware authentication```



❌ **Not suitable for**:Bounds-checked array indexing.



- Password hashing (use specialized PBKDF2/Argon2)**Returns**: Value at index or 0 if out of bounds

- Blockchain/Merkle trees (requires determinism)

- Digital signatures (requires determinism)---

- Cryptographic commitments

## Dependencies Between Modules

---

```

## Contextual Key Emergence (CKE)CEL (base entropy source)

 ├─► PHE (hashing)

**File**: `core/cke/cke.py`   │    └─► CKE (key derivation)

**Class**: `ContextualKeyEmergence`   │         └─► DSF (encryption/decryption)

**Version**: v0.3.0 with streaming support ├─► CKE (key derivation)

 │    └─► DSF

### Purpose └─► DSF (direct entropy access)



Derives ephemeral encryption keys from CEL state and optional context data with streaming key generation support.PCF (independent)

STATE (operates on CEL)

### Implementation DetailsUTILS (pure functions, no dependencies)

```

#### Key Derivation Process

## Version History

```python

def derive(### v0.1.0 Changes

    self,

    length: int = 32,1. **CEL**: Fixed initialization (use PRIME=65521 instead of 2^16)

    context: Optional[Dict[str, Any]] = None,2. **CKE**: Fixed derive() to return copy instead of reference

    cel_snapshot: Optional[Dict[str, Any]] = None,3. **DSF**: Replaced floating-point rotations with np.roll()

    phe_hash: Optional[bytes] = None4. **DSF**: Removed all rounding operations

) -> bytes:5. **Utils**: Fixed non_linear_diffusion in-place modification bug

    """

    Derive ephemeral key from CEL + contextAll modules now use pure integer arithmetic for perfect reversibility.

    
    Args:
        length: Key length in bytes
        context: Optional context data
        cel_snapshot: Optional CEL snapshot for deterministic key
        phe_hash: Optional pre-computed PHE hash
    
    Returns:
        Derived key (bytes)
    """
    # 1. Get CEL entropy
    if cel_snapshot:
        # Use snapshot (for decryption)
        cel_temp = ContinuousEntropyLattice(128, 6)
        cel_temp.restore_snapshot(cel_snapshot)
        base_entropy = cel_temp.get_entropy(length)
    else:
        # Use current CEL state (for encryption)
        base_entropy = self.cel.get_entropy(length)
    
    # 2. Hash context data (if provided)
    if context and not phe_hash:
        context_hash = self.phe.digest(str(context).encode())
    elif phe_hash:
        context_hash = phe_hash
    else:
        context_hash = bytes(32)
    
    # 3. Combine entropy + context
    key_vector = bytearray(length)
    for i in range(length):
        # Mix base entropy with context hash
        key_vector[i] = (
            (base_entropy[i % len(base_entropy)] + context_hash[i % 32])
            % 256
        )
    
    # 4. Additional mixing (prevent simple reversibility)
    for i in range(length):
        prev = key_vector[(i - 1) % length]
        next_val = key_vector[(i + 1) % length]
        key_vector[i] = (key_vector[i] + prev + next_val) % 256
    
    return bytes(key_vector)
```

#### Streaming Key Derivation (v0.3.0)

```python
def derive_stream_key(
    self,
    chunk_index: int,
    base_key: bytes,
    chunk_size: int
) -> bytes:
    """
    Derive per-chunk key for streaming encryption
    
    Args:
        chunk_index: Index of current chunk
        base_key: Base encryption key
        chunk_size: Size of chunks
    
    Returns:
        Chunk-specific key
    """
    # Derive chunk-specific key from base key + index
    chunk_context = {
        'chunk_index': chunk_index,
        'chunk_size': chunk_size
    }
    
    # Mix base key with chunk context
    chunk_key_data = base_key + str(chunk_context).encode()
    
    # Hash to get chunk key
    chunk_key = self.phe.digest(chunk_key_data)
    
    return chunk_key
```

### Key Properties

- **Length**: Configurable (default 32 bytes)
- **Type**: `bytes`
- **Range**: Values in [0, 255]
- **Ephemeral**: Not stored, regenerated on demand
- **Context-dependent**: Different context → different key
- **CEL-dependent**: Different CEL state → different key

### Important Notes

**Fixed in v0.1.0**: Returns copy of key vector, not reference (prevents external modification).

**v0.3.0**: Added streaming support for per-chunk key derivation.

---

## Data-State Folding (DSF)

**File**: `core/dsf/dsf.py`  
**Class**: `DataStateFolding`  
**Version**: v0.3.0 (no changes from v0.2.0)

### Purpose

Encrypts data via multidimensional tensor transformations using 5 folding strategies.

### Implementation Details

#### Encryption: fold()

**1. Tensor Preparation**:

```python
def fold(self, data: bytes, key: bytes) -> bytes:
    # Calculate square tensor dimensions
    total_size = len(data)
    height = int(np.ceil(np.sqrt(total_size)))
    width = height
    
    # Pad data to fit tensor
    padded_size = height * width
    padded_data = data + b'\x00' * (padded_size - total_size)
    
    # Convert to 2D tensor
    tensor = np.frombuffer(
        padded_data,
        dtype=np.uint8
    ).reshape(height, width).copy()
```

**2. Five Folding Strategies**:

**Strategy 1: Rotation** (circular shift):

```python
shift = int(key[0] % height)
tensor = np.roll(tensor, shift, axis=0)  # Rows
tensor = np.roll(tensor, shift, axis=1)  # Columns
```

**Strategy 2: Permutation** (row/column shuffle):

```python
seed = int.from_bytes(key[1:5], 'big')
rng = np.random.RandomState(seed)

# Generate permutation orders
row_order = rng.permutation(height)
col_order = rng.permutation(width)

# Apply permutations
tensor = tensor[row_order, :]  # Rows
tensor = tensor[:, col_order]  # Columns

# Store orders for decryption
self._row_order = row_order
self._col_order = col_order
```

**Strategy 3: Compression** (modular mixing):

```python
for i in range(height):
    for j in range(width):
        key_idx = (i + j) % len(key)
        tensor[i, j] = (tensor[i, j] + key[key_idx]) % 256
```

**Strategy 4: Diffusion** (non-linear mixing):

```python
# Apply cellular automaton-like diffusion
tensor = non_linear_diffusion(tensor, rounds=3)
```

**Strategy 5: Entropy Weighting** (CEL integration):

```python
# Get CEL entropy matching tensor size
cel_entropy = self.cel.get_entropy(height * width)

# Reshape entropy to match tensor
entropy_weights = (cel_entropy % 256).reshape(height, width)

# Apply multiplicative weighting
tensor = (
    (tensor.astype(np.uint16) * entropy_weights) % 256
).astype(np.uint8)

# Store weights for decryption
self._entropy_weights = entropy_weights
```

**3. Return Encrypted Data**:

```python
return tensor.flatten().tobytes()
```

#### Decryption: unfold()

**Reverse Operations** (exact opposite order):

```python
def unfold(
    self,
    encrypted_data: bytes,
    key: bytes,
    original_length: int
) -> bytes:
    # 1. Reshape to tensor
    tensor_size = int(np.sqrt(len(encrypted_data)))
    tensor = np.frombuffer(
        encrypted_data,
        dtype=np.uint8
    ).reshape(tensor_size, tensor_size).copy()
    
    # 2. Reverse entropy weighting (modular inverse)
    for i in range(tensor_size):
        for j in range(tensor_size):
            weight = self._entropy_weights[i, j]
            # Find modular inverse of weight
            inv_weight = modular_inverse(weight, 256)
            tensor[i, j] = (tensor[i, j] * inv_weight) % 256
    
    # 3. Reverse diffusion
    tensor = reverse_non_linear_diffusion(tensor, rounds=3)
    
    # 4. Reverse compression
    for i in range(tensor_size):
        for j in range(tensor_size):
            key_idx = (i + j) % len(key)
            tensor[i, j] = (tensor[i, j] - key[key_idx]) % 256
    
    # 5. Reverse permutation (inverse order)
    inv_col_order = np.argsort(self._col_order)
    inv_row_order = np.argsort(self._row_order)
    tensor = tensor[:, inv_col_order]  # Columns first
    tensor = tensor[inv_row_order, :]  # Then rows
    
    # 6. Reverse rotation (negative shift)
    shift = int(key[0] % tensor_size)
    tensor = np.roll(tensor, -shift, axis=1)  # Columns
    tensor = np.roll(tensor, -shift, axis=0)  # Rows
    
    # 7. Flatten and trim to original length
    return tensor.flatten().tobytes()[:original_length]
```

### Critical Requirements

✅ **Must have**:

- **Integer-only operations**: All arithmetic mod 256 or PRIME
- **No rounding**: Perfect reversibility required
- **Exact CEL state**: Must restore same entropy weights
- **Same key**: fold() and unfold() must use identical key
- **Correct order**: Reverse operations in exact opposite order

❌ **Must avoid**:

- Floating-point operations
- In-place modifications without copy
- Different CEL state for encryption/decryption
- Skipping any folding strategy

### Performance

| Operation | Time (10 KB) | Memory Overhead |
|-----------|--------------|-----------------|
| fold() | ~300ms | ~2x input size |
| unfold() | ~250ms | ~2x input size |
| Total round-trip | ~550ms | ~2x input size |

---

## Polymorphic Cryptographic Flow (PCF)

**File**: `core/pcf/pcf.py`  
**Class**: `PolymorphicCryptographicFlow`  
**Version**: v0.3.0 with CEL-delta adaptive morphing

### Purpose

Tracks operation count and provides adaptive morphing intervals based on CEL entropy changes.

### Implementation Details

#### State Tracking

```python
class PolymorphicCryptographicFlow:
    def __init__(self, base_interval: int = 100):
        self.operation_count = 0
        self.base_interval = base_interval  # Base morph interval
        self.current_morph = 0
        self.cel_delta_history = []  # v0.3.0
        self.last_cel_mean = None  # v0.3.0
```

#### CEL-Delta Calculation (v0.3.0)

```python
def calculate_cel_delta(self, cel: ContinuousEntropyLattice) -> float:
    """
    Calculate normalized change in CEL entropy
    
    Args:
        cel: CEL instance to measure
    
    Returns:
        Normalized delta (0.0-1.0)
    """
    # Get current CEL mean
    current_mean = np.mean(cel.lattice)
    
    if self.last_cel_mean is None:
        self.last_cel_mean = current_mean
        return 0.5  # Neutral delta
    
    # Calculate absolute change
    delta = abs(current_mean - self.last_cel_mean)
    
    # Normalize (max possible delta = PRIME)
    normalized_delta = delta / PRIME
    
    # Update history
    self.cel_delta_history.append(normalized_delta)
    if len(self.cel_delta_history) > 10:
        self.cel_delta_history.pop(0)
    
    # Update last mean
    self.last_cel_mean = current_mean
    
    return normalized_delta
```

#### Adaptive Morphing (v0.3.0)

```python
def get_adaptive_interval(
    self,
    cel: ContinuousEntropyLattice
) -> int:
    """
    Calculate adaptive morph interval based on CEL delta
    
    Returns:
        Adaptive interval (50, 100, or 200 operations)
    """
    cel_delta = self.calculate_cel_delta(cel)
    
    if cel_delta < 0.3:
        # High entropy change → frequent morphing
        return 50
    elif cel_delta < 0.7:
        # Medium entropy change → normal morphing
        return 100
    else:
        # Low entropy change → infrequent morphing
        return 200
```

#### Methods

```python
def update(self, cel: Optional[ContinuousEntropyLattice] = None):
    """Update operation count and check for morph"""
    self.operation_count += 1
    
    if cel and adaptive_morphing_enabled:
        # v0.3.0: Adaptive interval
        interval = self.get_adaptive_interval(cel)
    else:
        # Fixed interval
        interval = self.base_interval
    
    if self.operation_count % interval == 0:
        self.current_morph += 1

def get_morph_state(self) -> int:
    """Get current morph state"""
    return self.current_morph

def reset(self):
    """Reset PCF state"""
    self.operation_count = 0
    self.current_morph = 0
    self.cel_delta_history = []
    self.last_cel_mean = None
```

### Usage in v0.3.0

PCF is **actively used** for adaptive algorithm behavior:

- **Encryption**: Morph interval adapts based on CEL entropy changes
- **Context-aware**: High CEL change → more frequent algorithm adaptation
- **Performance**: Optimizes security vs speed based on actual entropy evolution

### Morph Interval Examples

| CEL Delta | Interval | Behavior |
|-----------|----------|----------|
| 0.15 (high change) | 50 ops | Frequent adaptation |
| 0.50 (medium change) | 100 ops | Normal adaptation |
| 0.85 (low change) | 200 ops | Infrequent adaptation |

---

## State Management

**File**: `core/state/state.py`  
**Class**: `StateManager`  
**Version**: v0.3.0 with RLE + varint compression

### Purpose

Serializes and deserializes CEL state with compression for efficient metadata storage.

### Implementation Details

#### Compression (v0.3.0)

**Run-Length Encoding (RLE)**:

```python
def rle_encode(data: List[int]) -> List[Tuple[int, int]]:
    """
    Encode data using run-length encoding
    
    Args:
        data: List of integers
    
    Returns:
        List of (value, count) tuples
    """
    if not data:
        return []
    
    encoded = []
    current_value = data[0]
    count = 1
    
    for value in data[1:]:
        if value == current_value:
            count += 1
        else:
            encoded.append((current_value, count))
            current_value = value
            count = 1
    
    # Append last run
    encoded.append((current_value, count))
    
    return encoded
```

**Variable-Length Integer Encoding (varint)**:

```python
def encode_varint(value: int) -> bytes:
    """
    Encode integer as variable-length bytes
    
    Value range → Bytes used:
    0-127       → 1 byte
    128-16383   → 2 bytes
    16384+      → 3+ bytes
    """
    result = bytearray()
    
    while value >= 128:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    
    result.append(value & 0x7F)
    
    return bytes(result)

def decode_varint(data: bytes, offset: int) -> Tuple[int, int]:
    """
    Decode varint from bytes
    
    Returns:
        (value, bytes_consumed)
    """
    result = 0
    shift = 0
    bytes_read = 0
    
    while True:
        byte = data[offset + bytes_read]
        bytes_read += 1
        
        result |= (byte & 0x7F) << shift
        
        if (byte & 0x80) == 0:
            break
        
        shift += 7
    
    return result, bytes_read
```

**Combined RLE + Varint Compression**:

```python
def compress_lattice(lattice: np.ndarray) -> bytes:
    """
    Compress lattice using RLE + varint
    
    Args:
        lattice: NumPy array to compress
    
    Returns:
        Compressed bytes
    """
    # Flatten to 1D list
    flat = lattice.flatten().tolist()
    
    # Apply RLE
    rle_data = rle_encode(flat)
    
    # Encode as varints
    compressed = bytearray()
    for value, count in rle_data:
        compressed.extend(encode_varint(value))
        compressed.extend(encode_varint(count))
    
    return bytes(compressed)

def decompress_lattice(
    compressed: bytes,
    shape: Tuple[int, ...]
) -> np.ndarray:
    """
    Decompress lattice from RLE + varint
    
    Args:
        compressed: Compressed bytes
        shape: Original lattice shape
    
    Returns:
        Decompressed NumPy array
    """
    # Decode varints
    offset = 0
    rle_data = []
    
    while offset < len(compressed):
        value, bytes_read = decode_varint(compressed, offset)
        offset += bytes_read
        
        count, bytes_read = decode_varint(compressed, offset)
        offset += bytes_read
        
        rle_data.append((value, count))
    
    # Decode RLE
    flat = []
    for value, count in rle_data:
        flat.extend([value] * count)
    
    # Reshape to original shape
    return np.array(flat, dtype=np.uint64).reshape(shape)
```

#### Serialization

```python
@staticmethod
def serialize_state(cel: ContinuousEntropyLattice) -> Dict[str, Any]:
    """Serialize CEL state with compression"""
    snapshot = cel.snapshot()
    
    # Compress lattice
    compressed_lattice = compress_lattice(snapshot['lattice'])
    
    return {
        'lattice': compressed_lattice,  # Compressed bytes
        'size': snapshot['size'],
        'depth': snapshot['depth'],
        'seed': snapshot['seed'],
        'update_count': snapshot['update_count'],
        'compression': {
            'method': 'rle_varint',
            'original_size': snapshot['lattice'].nbytes,
            'compressed_size': len(compressed_lattice)
        }
    }
```

#### Deserialization

```python
@staticmethod
def deserialize_state(state_dict: Dict[str, Any]) -> ContinuousEntropyLattice:
    """Deserialize CEL state with decompression"""
    # Create new CEL
    cel = ContinuousEntropyLattice(
        size=state_dict['size'],
        depth=state_dict['depth']
    )
    cel.init(state_dict['seed'])
    
    # Decompress lattice
    shape = (state_dict['size'], state_dict['size'], state_dict['depth'])
    lattice = decompress_lattice(state_dict['lattice'], shape)
    
    # Restore snapshot
    cel.restore_snapshot({
        'lattice': lattice,
        'size': state_dict['size'],
        'depth': state_dict['depth'],
        'seed': state_dict['seed'],
        'update_count': state_dict['update_count']
    })
    
    return cel
```

### Compression Performance (v0.3.0)

| Metric | Value |
|--------|-------|
| Original lattice size | ~950 KB |
| Compressed size | ~465 KB |
| Compression ratio | 51% |
| Compression time | ~50ms |
| Decompression time | ~10ms |

**Typical Lattice Statistics**:

- Unique values: 51% of total cells
- Repeated values: 49% of total cells
- RLE efficiency: High for repeated values
- Varint efficiency: Most values <16384 (2 bytes)

---

## Polymorphic Decoy System (v0.3.0)

**File**: `interfaces/api/stc_api.py`  
**Class**: `DecoyManager`  
**Version**: v0.3.0 NEW

### Purpose

Generate and manage cryptographically indistinguishable decoy CEL lattices to prevent real CEL identification.

### Implementation Details

#### Decoy Generation

```python
class DecoyManager:
    def __init__(self, seed: Union[str, bytes, int]):
        self.base_seed = seed
        self.decoy_sizes = [
            (32, 3),   # 32×32×3
            (48, 3),   # 48×48×3
            (64, 4),   # 64×64×4 (default)
            (80, 4),   # 80×80×4
            (96, 5),   # 96×96×5
        ]
    
    def generate_decoys(
        self,
        num_decoys: int,
        variable_sizes: bool = True,
        randomize_count: bool = True
    ) -> List[ContinuousEntropyLattice]:
        """
        Generate polymorphic decoy lattices
        
        Args:
            num_decoys: Base number of decoys
            variable_sizes: Use random sizes
            randomize_count: Randomize actual count
        
        Returns:
            List of decoy CEL instances
        """
        # Randomize count (±2)
        if randomize_count:
            actual_count = num_decoys + random.randint(-2, 2)
            actual_count = max(1, min(actual_count, 7))
        else:
            actual_count = num_decoys
        
        decoys = []
        for i in range(actual_count):
            # Select size
            if variable_sizes:
                size, depth = random.choice(self.decoy_sizes)
            else:
                size, depth = 64, 4  # Default decoy size
            
            # Derive decoy-specific seed
            decoy_seed = self._derive_decoy_seed(i)
            
            # Create decoy CEL
            decoy = ContinuousEntropyLattice(size, depth)
            decoy.init(decoy_seed)
            
            # Update to diversify (random 1-5 updates)
            for _ in range(random.randint(1, 5)):
                decoy.update()
            
            decoys.append(decoy)
        
        return decoys
    
    def _derive_decoy_seed(self, index: int) -> int:
        """Derive cryptographically distinct seed for decoy"""
        # Combine base seed with index
        seed_data = f"{self.base_seed}:decoy:{index}".encode()
        
        # Hash to get decoy seed
        seed_hash = hashlib.sha256(seed_data).digest()
        
        # Convert to integer
        return int.from_bytes(seed_hash[:8], 'big')
```

#### Timing Randomization (Optional)

```python
def apply_timing_jitter(self):
    """Add random delay to obscure timing patterns"""
    delay = random.uniform(0.0001, 0.001)  # 0.1-1.0ms
    time.sleep(delay)
```

### Security Properties

✅ **Cryptographic Indistinguishability**:

- Decoys generated using same algorithm as real CEL
- Same seed derivation mechanism
- Same serialization format
- Same metadata structure
- Attacker cannot determine which is real without password

✅ **Performance Optimization**:

- Decoys use smaller lattices (64×64×4)
- 5.8x faster than full-size (128×128×6)
- Real CEL: 0.81s generation
- Decoy CEL: 0.14s generation each
- Total with 3 decoys: 0.42s vs 2.43s

✅ **Adaptive Count**:

- Base count: User-specified (default 3)
- Randomization: ±2 variation
- Range: 1-7 decoys total
- Prevents pattern recognition

### Decoy Selection During Decryption

```python
def decrypt_with_decoys(
    self,
    encrypted_data: bytes,
    metadata: Dict[str, Any],
    password: str
) -> bytes:
    """
    Try all CEL snapshots until successful decryption
    
    Returns:
        Decrypted data
    
    Raises:
        ValueError: If no CEL snapshot works
    """
    cel_snapshots = metadata['cel_snapshots']
    
    for idx, snapshot in enumerate(cel_snapshots):
        try:
            # Restore CEL from snapshot
            cel = StateManager.deserialize_state(snapshot)
            
            # Attempt decryption
            decrypted = self._decrypt_with_cel(
                encrypted_data,
                metadata,
                cel,
                password
            )
            
            # Success!
            return decrypted
            
        except Exception:
            # This wasn't the right CEL, try next
            continue
    
    # No CEL worked
    raise ValueError("Decryption failed - wrong password or corrupted data")
```

**Decoy Trial Overhead**:

- Average trials: (num_decoys + 1) / 2
- 3 decoys: ~2 trials average
- Each failed trial: ~50ms
- Total overhead: ~100ms average

---

## Mathematical Primitives

**File**: `utils/math_primitives.py`  
**Version**: v0.3.0 (unchanged from v0.2.0)

### Core Functions

#### modular_exponentiation

```python
def modular_exponentiation(base: int, exp: int, mod: int) -> int:
    """
    Fast modular exponentiation using binary method
    
    Computes: (base^exp) mod mod
    
    Time complexity: O(log exp)
    """
    result = 1
    base = base % mod
    
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    
    return result
```

#### modular_inverse

```python
def modular_inverse(a: int, m: int) -> int:
    """
    Compute modular multiplicative inverse
    
    Finds x such that: (a * x) mod m = 1
    
    Uses Extended Euclidean Algorithm
    """
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse does not exist for {a} mod {m}")
    
    return (x % m + m) % m
```

#### non_linear_diffusion

```python
def non_linear_diffusion(
    matrix: np.ndarray,
    rounds: int = 1
) -> np.ndarray:
    """
    Apply cellular automaton-like diffusion
    
    Args:
        matrix: 2D NumPy array
        rounds: Number of diffusion rounds
    
    Returns:
        Diffused matrix
    """
    height, width = matrix.shape
    result = matrix.copy()
    
    for _ in range(rounds):
        temp = np.zeros_like(result)
        
        for i in range(height):
            for j in range(width):
                # Get neighbors (with wrapping)
                up = result[(i-1) % height, j]
                down = result[(i+1) % height, j]
                left = result[i, (j-1) % width]
                right = result[i, (j+1) % width]
                center = result[i, j]
                
                # Weighted combination
                temp[i, j] = (
                    (center * 2 + up + down + left + right) // 6
                ) % 256
        
        result = temp
    
    return result
```

### Constants

```python
PRIME = 65521  # Largest prime < 2^16, used throughout STC
```

---

## Module Dependencies (v0.3.0)

```text
┌─────────────────────────────────────────────────────────────┐
│                         Application                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      STCContext (API)                       │
│  - DecoyManager (manages decoy generation)                  │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │  CEL   │─────────►│  PHE   │─────────►│  CKE   │
    │(+health│          │(adaptive│          │(stream)│
    └────────┘          └────────┘          └────────┘
         │                    │                    │
         │                    │                    ▼
         │                    │               ┌────────┐
         │                    │               │  DSF   │
         │                    │               │(5 fold)│
         │                    │               └────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │  PCF   │          │ STATE  │          │ UTILS  │
    │(adapt) │          │(RLE+var│          │ (math) │
    └────────┘          └────────┘          └────────┘
```

**Dependency Flow**:

1. **CEL** → Base entropy (used by PHE, CKE, DSF)
2. **PHE** → Hashing (used by CKE for context hashing)
3. **CKE** → Key derivation (uses CEL + PHE)
4. **DSF** → Encryption (uses CEL + CKE)
5. **PCF** → Morphing (monitors CEL delta)
6. **STATE** → Serialization (operates on CEL)
7. **DecoyManager** → Decoy generation (creates CEL instances)
8. **UTILS** → Pure functions (no dependencies)

---

## Version History

### v0.3.0 Changes

1. **CEL**:
   - Added `get_entropy_health()` comprehensive metrics
   - Changed default size: 256→128, depth: 8→6
   - Added health-based encryption prevention

2. **PHE**:
   - Added adaptive difficulty scaling (7-15 paths)
   - Added oracle attack detection
   - Added timing randomization

3. **CKE**:
   - Added streaming key derivation
   - Enhanced context mixing

4. **PCF**:
   - Added CEL-delta-driven adaptive morphing
   - Changed from fixed to adaptive intervals (50/100/200)

5. **STATE**:
   - Added RLE + varint compression
   - 51% metadata size reduction
   - <10ms decompression overhead

6. **DecoyManager** (NEW):
   - Polymorphic decoy generation
   - Variable sizes (32-96)
   - Randomized counts (±2)
   - Timing jitter (optional)

### v0.2.0 Changes

- Password-based encryption
- MAC verification
- Binary TLV metadata format

### v0.1.0 Changes

- Fixed CEL initialization (PRIME=65521)
- Fixed CKE derive() to return copy
- Eliminated floating-point operations
- Fixed non_linear_diffusion in-place bug

---

## Performance Characteristics (v0.3.0)

| Component | Operation | Time | Memory |
|-----------|-----------|------|--------|
| CEL (128×128×6) | Initialization | ~0.81s | ~7.5 MB |
| CEL (64×64×4) | Initialization | ~0.14s | ~1 MB |
| CEL | update() | ~50ms | - |
| CEL | get_entropy_health() | ~60ms | - |
| PHE | digest() (7 paths) | ~50ms | - |
| PHE | digest() (15 paths) | ~100ms | - |
| CKE | derive() | ~10ms | - |
| DSF | fold() | ~300ms | 2x input |
| DSF | unfold() | ~250ms | 2x input |
| PCF | update() | <1ms | - |
| STATE | compress_lattice() | ~50ms | - |
| STATE | decompress_lattice() | ~10ms | - |
| DecoyManager | generate_decoys(3) | ~0.42s | ~3 MB |

**Total Encryption (10 KB, 3 decoys)**:

- Real CEL: 0.81s
- Decoys: 0.42s
- DSF fold: 0.30s
- Compression: 0.05s
- **Total**: ~1.8s

---

## See Also

- **[Architecture](architecture.md)** - System design overview
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Usage Guide](usage-guide.md)** - Practical examples
- **[Security Guide](security-guide.md)** - Best practices and threat model
- **[Performance Guide](PERFORMANCE.md)** - Optimization strategies
