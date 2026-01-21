# CLAUDE.md

## Commands

```bash
python -m econlint /path/to/codebase      # Run analysis
python -m econlint /path/to/codebase --json   # JSON output
python -m pytest tests/                   # Run tests
```

## Architecture

```
CLI → File Discovery → AST Parser → Rule Engine → Suppression Filter → Formatter
```

Standard library only. No external dependencies.

## File structure

```
econlint/
├── __init__.py
├── __main__.py          # Entry point
├── cli.py               # argparse, orchestration
├── discovery.py         # Find .py files
├── parser.py            # AST parsing, error handling
├── rules/
│   ├── __init__.py
│   ├── base.py          # BaseRule visitor class
│   ├── econ001.py       # External calls in loops
│   ├── econ002.py       # Unbounded retries
│   ├── econ003.py       # N+1 patterns
│   └── econ004.py       # Unbounded fan-out
├── suppression.py       # # econlint: ignore handling
├── formatters/
│   ├── __init__.py
│   ├── text.py
│   └── json_fmt.py
└── warnings.py          # Warning dataclass, explanation templates
tests/
├── fixtures/{rule}/     # positive_*.py, negative_*.py, suppressed_*.py
└── test_{rule}.py
```

## Build order

1. `warnings.py` — Warning dataclass
2. `cli.py` — Minimal argparse, accept path
3. `discovery.py` — Find .py files
4. `parser.py` — Parse to AST
5. `rules/base.py` — Base visitor
6. `rules/econ001.py` — First rule
7. `formatters/text.py` — Print warnings
8. `__main__.py` — Wire together, test end-to-end
9. Remaining rules: econ002, econ003, econ004
10. `suppression.py` — Inline ignores
11. `formatters/json_fmt.py`
12. Tests

## Detection heuristics

### ECON001 — External calls in loops

Detect calls inside `for`, `while`, list comprehensions:
- HTTP: `requests.*`, `httpx.*`, `aiohttp.*`, `urllib.request.*`
- AWS: `boto3` client methods
- Database: `cursor.execute`, `session.execute`
- Generic: calls on `*client*`, `*api*`, `*service*`, `*connection*`

### ECON002 — Unbounded retries

- `tenacity` without `stop=stop_after_attempt(n)`
- `retrying` without `stop_max_attempt_number`
- `while True` + `try/except` + `sleep`
- `while` loops with exception handlers lacking counter

### ECON003 — N+1 patterns

- `for item in collection:` with external call using `item`
- `[api.get(x) for x in items]`
- Methods named `get`, `fetch`, `load`, `query`, `find` inside loops

### ECON004 — Unbounded fan-out

- `asyncio.gather(*[...])` without `Semaphore`
- `ThreadPoolExecutor` without bounded `max_workers`
- `multiprocessing.Pool.map` with external calls

## Warning format

```
ECON001: External call inside loop at app/sync.py:45

  Pattern: requests.get() called inside for loop
  
  Economic risk: Each loop iteration incurs API/network cost.
  At 1000 iterations, this becomes 1000 billable calls.
  Under partial failure, retries multiply this further.
  
  Even if the collection is small today, data growth or
  upstream changes can make this unbounded.
  
  Consider: Batch the calls, or add explicit bounds.
```

**Quality bar:** If it doesn't make someone say "yes, that would get expensive," rewrite it.

## Suppression syntax

```python
requests.get(url)  # econlint: ignore
requests.get(url)  # econlint: ignore=ECON001
requests.get(url)  # econlint: ignore=ECON001,ECON003
```

## Exit codes

- `0` — No warnings
- `1` — Warnings found
- `2` — Error

## Code style

- Type hints on all signatures
- `pathlib.Path` over `os.path`
- f-strings
- No classes where functions suffice

## Testing

Each rule needs in `tests/fixtures/{rule}/`:
- `positive_*.py` — Should trigger
- `negative_*.py` — Should not trigger
- `suppressed_*.py` — Has ignore comment

No mocking frameworks. Simple assertions.

## Don't

- Add config files or severity levels
- Use external dependencies
- Write vague "might be inefficient" warnings
- Detect every possible variant

## Tuning

Track heuristic adjustments in `TUNING.md`:

```markdown
## ECON001
### False positives
- logger.info() — not external, ignore logging

### False negatives
- self.api.call() — need *api* in attribute chain
```

## Done when

1. Four rules detect target patterns
2. Explanations feel expensive
3. Suppression works
4. Text and JSON output work
5. Tests pass
6. Zero external dependencies
