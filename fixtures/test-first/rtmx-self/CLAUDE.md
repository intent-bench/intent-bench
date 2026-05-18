# Test-First Development

Pre-written tests are provided in `tests/release_gate_test.go`. Your task is to
make all tests pass by implementing the `release gate` subcommand.

## Contract

The tests call `executeReleaseGate(projectDir, version, jsonOutput, stdout, stderr)`
which must be wired to the actual command implementation. The function should:
- Return nil when all requirements for the version are COMPLETE (exit 0)
- Return an error when any requirements are incomplete (exit 1)
- Return an error when no requirements are assigned (exit 1)
- Output JSON when jsonOutput is true

## Approach

1. Read all tests to understand the release gate contract
2. Study the existing CLI command patterns (Cobra, table output)
3. Wire the `executeReleaseGate` function to the actual implementation
4. Implement the command following existing patterns
5. Run `go test ./...` to verify all tests pass
6. Do not modify the test assertions, only the contract wiring
