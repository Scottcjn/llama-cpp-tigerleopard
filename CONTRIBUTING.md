# Contributing to llama.cpp Tiger/Leopard

Thank you for your interest in contributing to the llama.cpp Tiger/Leopard port! This project brings modern large language model inference to vintage PowerPC Macs running Mac OS X Tiger (10.4) and Leopard (10.5). Your contributions help keep classic Mac hardware relevant in the AI era.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Project Overview](#project-overview)
- [Development Environment](#development-environment)
- [How to Contribute](#how-to-contribute)
- [PowerPC-Specific Guidelines](#powerpc-specific-guidelines)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)
- [Optimization Guidelines](#optimization-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project welcomes contributors of all experience levels. We expect:
- Respectful communication
- Patience with vintage hardware limitations
- Documentation of workarounds and quirks
- Celebration of creative solutions to old-hardware challenges

## Project Overview

### What This Is

A backport of llama.cpp (LLM inference in C/C++) to PowerPC Macs:
- **Target OS**: Mac OS X 10.4 Tiger, 10.5 Leopard
- **Target CPUs**: PowerPC G4, G5 (both 32-bit and 64-bit)
- **Goal**: Run modern LLMs (Llama, Mistral, etc.) on vintage hardware

### Key Challenges

- **No AltiVec in upstream**: Must add PowerPC SIMD manually
- **Limited RAM**: G4/G5 max out at 2-8GB
- **Old compilers**: GCC 4.0/4.2, no modern C++ features
- **No Metal**: CPU-only inference
- **Endianness**: PowerPC is big-endian (x86 is little-endian)

### Architecture Support Matrix

| CPU | Bits | AltiVec | Notes |
|-----|------|---------|-------|
| PowerPC G3 | 32 | No | Minimum supported CPU |
| PowerPC G4 | 32 | Yes | 7450+ recommended |
| PowerPC G5 | 32/64 | Yes | Dual-core models best |

## Development Environment

### Option 1: Native PowerPC Mac (Recommended)

If you have a PowerPC Mac:

1. **Install Xcode 2.5** (Tiger) or **Xcode 3.1** (Leopard)
2. **Install Git** (via MacPorts or build from source)
3. **Clone the repository**:
   ```bash
   git clone https://github.com/Scottcjn/llama-cpp-tigerleopard.git
   cd llama-cpp-tigerleopard
   ```

### Option 2: Cross-Compilation (Faster)

Build on modern macOS/Linux for PowerPC target:

```bash
# Install PowerPC cross-compiler
# macOS with MacPorts:
sudo port install powerpc-apple-darwin10-gcc

# Or use osxcross for Linux:
git clone https://github.com/tpoechtrager/osxcross
cd osxcross
./build.sh
```

### Option 3: QEMU Emulation

Test without physical hardware:

```bash
# Install QEMU
brew install qemu  # macOS
sudo apt-get install qemu-system-ppc  # Linux

# Run Tiger in QEMU
qemu-system-ppc -M mac99 -boot d -cdrom tiger.iso \
  -hda tiger.img -m 1024 -cpu G4
```

## How to Contribute

### Reporting Issues

When reporting bugs, always include:
- **Mac model** (e.g., Power Mac G5 Dual 2.0GHz)
- **OS version** (e.g., Mac OS X 10.4.11)
- **RAM amount**
- **Compiler version** (`gcc --version`)
- **Model being used** (e.g., llama-7b-q4_0.gguf)
- **Full error output** or crash log

### Areas Needing Help

1. **AltiVec Optimizations**: SIMD acceleration for G4/G5
2. **Memory Optimization**: Reduce RAM usage for limited systems
3. **Quantization Support**: Better GGUF format compatibility
4. **Build System**: Improve Makefile for vintage toolchains
5. **Documentation**: Better setup guides for different Mac models

### Building from Source

```bash
# Basic build (unoptimized)
make

# Optimized for G5 (64-bit)
make ARCH_FLAGS="-mcpu=970 -mtune=970 -mpowerpc64"

# Optimized for G4 with AltiVec
make ARCH_FLAGS="-mcpu=7450 -mtune=7450 -faltivec"

# Debug build
make DEBUG=1
```

## PowerPC-Specific Guidelines

### AltiVec SIMD

When adding AltiVec optimizations:

```c
#include <altivec.h>

// Check for AltiVec support at runtime
#include <sys/sysctl.h>

bool has_altivec() {
    int selectors[2] = { CTL_HW, HW_VECTORUNIT };
    int hasVectorUnit = 0;
    size_t length = sizeof(hasVectorUnit);
    sysctl(selectors, 2, &hasVectorUnit, &length, NULL, 0);
    return hasVectorUnit != 0;
}

// Example: Vectorized dot product
float dot_product_altivec(const float* a, const float* b, int n) {
    vector float sum = vec_splat_f32(0.0f);
    
    for (int i = 0; i < n; i += 4) {
        vector float va = vec_ld(0, &a[i]);
        vector float vb = vec_ld(0, &b[i]);
        sum = vec_madd(va, vb, sum);
    }
    
    // Horizontal sum
    vector float temp = vec_add(sum, vec_sld(sum, sum, 8));
    temp = vec_add(temp, vec_sld(temp, temp, 4));
    return vec_extract(temp, 0);
}
```

### Endianness Handling

PowerPC is big-endian. Handle GGUF format carefully:

```c
// Always use endian-aware reads
#include <endian.h>

static inline uint32_t gguf_read_u32(const uint8_t* ptr) {
    // GGUF is little-endian, convert if on big-endian
    #if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
        return __builtin_bswap32(*(uint32_t*)ptr);
    #else
        return *(uint32_t*)ptr;
    #endif
}

static inline float gguf_read_f32(const uint8_t* ptr) {
    union { uint32_t i; float f; } u;
    u.i = gguf_read_u32(ptr);
    return u.f;
}
```

### Memory Constraints

Optimize for limited RAM:

```c
// Use mmap for model files instead of loading into RAM
void* mmap_model(const char* path, size_t* size) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return NULL;
    
    struct stat st;
    fstat(fd, &st);
    *size = st.st_size;
    
    void* mapped = mmap(NULL, *size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    
    return mapped;
}

// Implement aggressive memory pooling
#define MEMORY_POOL_SIZE (256 * 1024 * 1024)  // 256MB chunks

static void* memory_pool = NULL;
static size_t pool_used = 0;

void* pool_alloc(size_t size) {
    size = (size + 15) & ~15;  // 16-byte align
    if (pool_used + size > MEMORY_POOL_SIZE) {
        // Allocate new pool
        memory_pool = valloc(MEMORY_POOL_SIZE);
        pool_used = 0;
    }
    void* ptr = (char*)memory_pool + pool_used;
    pool_used += size;
    return ptr;
}
```

## Style Guidelines

### C/C++ Code Style

Follow the existing llama.cpp style:

```c
// Use 4-space indentation
// Braces on same line
void ggml_vec_dot_f32(int n, float* s, const float* x, const float* y) {
    float sumf = 0.0f;
    for (int i = 0; i < n; i++) {
        sumf += x[i] * y[i];
    }
    *s = sumf;
}

// Prefix with ggml_ or llama_ for public functions
// Use static for file-local functions
static inline float ggml_silu(float x) {
    return x / (1.0f + expf(-x));
}

// Comments explain WHY, not WHAT
// Bad: increment i
// Good: Process next 4 elements for AltiVec alignment
```

### Compiler Compatibility

Write code that compiles with GCC 4.0/4.2:

```c
// Avoid C11 features
// Use traditional struct initialization
struct ggml_tensor tensor = {
    .type = GGML_TYPE_F32,
    .ne = {0},
    .nb = {0},
    .op = GGML_OP_NONE
};

// Avoid auto, range-based for, lambda
// Use explicit types and traditional loops
for (int i = 0; i < n; i++) {
    // ...
}

// Avoid std::thread (not available on Tiger)
// Use pthreads instead
#include <pthread.h>

void* worker_thread(void* arg) {
    // Thread work
    return NULL;
}

pthread_t thread;
pthread_create(&thread, NULL, worker_thread, NULL);
```

## Testing

### On Real Hardware

```bash
# Run basic tests
make test

# Test with a small model
./main -m models/tinyllama-1b-q4_0.gguf -p "Hello"

# Benchmark
./perplexity -m models/llama-7b-q4_0.gguf -f test.txt
```

### Performance Benchmarking

Report performance with:
- Tokens per second (tok/s)
- Memory usage (RSS)
- Model load time
- CPU utilization

```bash
# Standard benchmark command
./main -m models/llama-7b-q4_0.gguf \
       -p "The quick brown fox" \
       -n 128 \
       --threads 2 \
       2>&1 | tee benchmark.log
```

### Expected Performance (Reference)

| Model | CPU | RAM | Quant | Speed |
|-------|-----|-----|-------|-------|
| TinyLlama-1B | G4 1.42GHz | 1GB | Q4_0 | ~2 tok/s |
| Llama-7B | G5 Dual 2.0GHz | 4GB | Q4_0 | ~1 tok/s |
| Mistral-7B | G5 Quad 2.5GHz | 8GB | Q4_0 | ~1.5 tok/s |

## Optimization Guidelines

### Profiling

Use Shark (Leopard) or gprof:

```bash
# Build with profiling
make PROFILE=1

# Run to generate gmon.out
./main -m model.gguf -p "test"

# Analyze
gprof ./main gmon.out > profile.txt
```

### Optimization Priority

1. **Memory access patterns** (biggest impact)
2. **AltiVec vectorization** (4x speedup potential)
3. **Cache optimization** (L1/L2 on G5 is small)
4. **Thread scaling** (limited on Tiger)

### AltiVec Patterns

Common patterns for G4/G5:

```c
// Vectorized softmax
void softmax_altivec(float* x, int n) {
    // Find max (for numerical stability)
    vector float vmax = vec_splat_f32(-INFINITY);
    for (int i = 0; i < n; i += 4) {
        vector float v = vec_ld(0, &x[i]);
        vmax = vec_max(vmax, v);
    }
    
    // Exp and sum
    vector float vsum = vec_splat_f32(0.0f);
    for (int i = 0; i < n; i += 4) {
        vector float v = vec_ld(0, &x[i]);
        v = vec_expte(v - vmax);  // AltiVec exp approximation
        vec_st(v, 0, &x[i]);
        vsum = vec_add(vsum, v);
    }
    
    // Normalize
    float sum = vec_extract(vsum, 0) + vec_extract(vsum, 1) +
                vec_extract(vsum, 2) + vec_extract(vsum, 3);
    vector float vscale = vec_splat_f32(1.0f / sum);
    for (int i = 0; i < n; i += 4) {
        vector float v = vec_ld(0, &x[i]);
        v = vec_madd(v, vscale, vec_splat_f32(0.0f));
        vec_st(v, 0, &x[i]);
    }
}
```

## Pull Request Process

1. **Test on real PowerPC hardware** if possible
2. **Verify no regressions** on x86 builds
3. **Document AltiVec usage** with comments
4. **Include benchmark results** for optimizations
5. **Update BUILD.md** if build process changes

### PR Checklist

- [ ] Compiles on Tiger (GCC 4.0) or Leopard (GCC 4.2)
- [ ] Compiles on modern macOS (no regressions)
- [ ] Tested on PowerPC hardware or QEMU
- [ ] AltiVec code has runtime detection
- [ ] Endianness handled correctly
- [ ] Memory usage documented
- [ ] Benchmarks included (for optimizations)

## Resources

- [AltiVec Tutorial](https://developer.apple.com/hardwaredrivers/ve/tutorial.html)
- [PowerPC Compiler Options](https://gcc.gnu.org/onlinedocs/gcc/RS_002f6000-and-PowerPC-Options.html)
- [GGUF Format Spec](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [Original llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Mac OS X ABI](https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/LowLevelABI/000-Introduction/introduction.html)

## Vintage Mac Community

- [MacRumors PowerPC Forum](https://forums.macrumors.com/forums/powerpc-macs.221/)
- [Macintosh Garden](https://macintoshgarden.org/)
- [System 7 Today](http://system7today.com/)

Thank you for keeping PowerPC alive in the AI age!
