# Contributing to llama.cpp Tiger/Leopard

Thank you for helping improve the llama.cpp Tiger/Leopard PowerPC port. This
repository documents and preserves a working llama.cpp build for Mac OS X Tiger
10.4 and Leopard 10.5 on PowerPC G4/G5 hardware. Contributions should keep the
vintage Mac build path reproducible and easy for other users to verify.

## Project Scope

This repository contains:

- top-level documentation for building and running llama.cpp on Tiger/Leopard
- tested PowerPC hardware and performance notes
- attribution, license, and community information
- a vendored `llama.cpp_source/` tree for the ported source

Good contributions include:

- documentation fixes for build commands, model recommendations, or hardware
  test notes
- updates to verified Tiger or Leopard build instructions
- small PowerPC portability fixes with a clear explanation
- focused updates to vendored llama.cpp documentation when they affect this port
- test notes that distinguish G4, G5, Tiger, and Leopard behavior

Avoid broad source rewrites or unrelated vendored-tree cleanup unless they are
needed for the PowerPC port you are changing.

## Local Setup

Clone the repository and create a working branch:

```bash
git clone https://github.com/Scottcjn/llama-cpp-tigerleopard.git
cd llama-cpp-tigerleopard
git switch -c <your-branch-name>
```

For documentation-only work, review the rendered Markdown before opening a pull
request. For build or runtime changes, test on the closest available target
system and state the hardware and OS version in the pull request.

## Working With the Vendored Source

The `llama.cpp_source/` directory is large and mirrors upstream llama.cpp with
PowerPC-oriented port work. Keep changes there narrow:

- touch only files needed for the bug, docs update, or portability fix
- separate top-level guide changes from vendored source changes when possible
- preserve upstream context so future syncs remain reviewable
- call out whether a change is PowerPC-specific or generally applicable

If a change came from upstream llama.cpp, include the upstream commit or release
reference in the pull request description.

## Build and Runtime Notes

PowerPC build behavior depends heavily on hardware, compiler, and OS version.
When updating build instructions or source code, record:

- machine model and CPU type
- Tiger or Leopard version
- Xcode and GCC version
- CMake or Makefile command used
- model file and quantization tested
- observed tokens per second, if relevant

Keep examples realistic for vintage systems. Prefer small model examples and
commands that work within the RAM limits documented in `README.md`.

## Validation

Run the checks that match your change before opening a pull request.

For documentation-only changes:

```bash
git diff --check
```

Review the rendered Markdown and verify changed paths, commands, and model names.

For source or build changes, run the relevant build on the target platform when
possible:

```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_ARCHITECTURES=ppc
make -j2
```

If you cannot test on Tiger or Leopard PowerPC hardware, say so clearly and list
the checks you did run.

## Pull Request Guidelines

Use focused pull requests. Include:

- the documentation section, source file, or build path changed
- the hardware and OS version used for validation
- exact commands run
- whether `llama.cpp_source/` was changed
- whether the change is PowerPC-specific or from upstream llama.cpp

Do not mix unrelated README edits, vendored source changes, and performance
claims in one pull request.

## Review Checklist

Before requesting review, confirm:

- Tiger/Leopard users can follow the updated instructions
- PowerPC-specific flags or assumptions are explained
- attribution and license notes remain intact
- vendored source changes are minimal and justified
- limitations or missing hardware validation are documented
