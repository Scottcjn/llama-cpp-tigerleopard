# Contributing to llama-cpp-tigerleopard

Thanks for helping maintain the Tiger and Leopard PowerPC llama.cpp port. This
repository supports very old toolchains and hardware, so small, well-tested
changes with clear compatibility notes are the easiest to review.

## Useful Contributions

- Improve build instructions for Xcode 2.5, Xcode 3.1, GCC 4.0, or GCC 4.2.
- Add tested notes for G4, G5, Tiger, and Leopard systems.
- Clarify model selection, quantization, and memory requirements.
- Fix portability issues while preserving old compiler compatibility.
- Add troubleshooting notes for AltiVec, CMake, or runtime failures.

## Development Workflow

1. Fork the repository and create a focused branch.
2. Keep compatibility fixes and documentation updates narrowly scoped.
3. Avoid modern language features unless the PR explicitly explains why old
   compiler support is unaffected.
4. Include machine model, OS version, compiler, and test command in the PR.

## Validation

- Documentation-only changes: run `git diff --check`.
- Build changes: run the documented build command on the oldest target system
  available and include compiler output.
- Runtime changes: include model name, quantization, RAM size, and approximate
  tokens per second.

## Pull Request Checklist

- The affected OS and CPU family are named.
- Build or runtime validation is included.
- Old compiler compatibility is considered.
- Performance claims include model, hardware, and settings.
- Generated binaries and model files are not committed.

## Reporting Issues

Include Mac model, CPU, RAM, OS version, Xcode or GCC version, build command,
model file details, and the full compiler or runtime output.
