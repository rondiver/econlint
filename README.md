# econlint

A Python linter that finds code patterns that get expensive at scale.

Most linters catch bugs. This one catches bills. It looks for patterns that work fine in development but become costly in production—API calls in loops, unbounded retries, N+1 queries, unlimited concurrency.

## What it catches

**ECON001: External calls in loops**
```python
for user in users:
    response = requests.get(f"/api/users/{user.id}")  # 1000 users = 1000 API calls
```

**ECON002: Unbounded retries**
```python
@retry()  # No stop condition = infinite retries = infinite cost
def fetch_data():
    return api.get("/data")
```

**ECON003: N+1 query patterns**
```python
for order in orders:
    customer = db.get_customer(order.customer_id)  # N orders = N+1 queries
```

**ECON004: Unbounded fan-out**
```python
await asyncio.gather(*[fetch(url) for url in urls])  # 10,000 URLs = 10,000 concurrent requests
```

## Honest disclaimer

This started as a weekend project to scratch an itch. The detection is heuristic-based—it looks for naming patterns like `*_client`, `*_api`, and known library calls rather than doing actual type inference. It will miss things. It might flag things incorrectly. But when it does catch something, the warnings explain *why* the pattern is expensive, not just that it's "bad."

Tested against scrapy (412 Python files) with a 95% reduction in false positives after tuning. Your mileage may vary.

## Setup

**Requirements:** Python 3.10+ (standard library only, no dependencies)

That's it. Clone and run.

## Running

**Analyze a file or directory:**
```bash
python -m econlint /path/to/your/code
```

**JSON output for tooling:**
```bash
python -m econlint /path/to/your/code --json
```

**Skip specific rules:**
```bash
python -m econlint /path/to/your/code --disable=ECON003
```

**Exclude paths:**
```bash
python -m econlint /path/to/your/code --exclude=tests --exclude=venv
```

## Output

When econlint finds something, it explains the economic risk:

```
ECON001: External call inside loop at app/sync.py:45

  Pattern: requests.get() called inside loop

  Economic risk: Each loop iteration incurs API/network cost.
  At 1000 iterations, this becomes 1000 billable calls.
  Under partial failure, retries multiply this further.

  Even if the collection is small today, data growth or
  upstream changes can make this unbounded.

  Consider: Batch the calls, or add explicit bounds.
```

## Suppressing warnings

If you've thought about it and the pattern is intentional:

```python
requests.get(url)  # econlint: ignore
requests.get(url)  # econlint: ignore=ECON001
requests.get(url)  # econlint: ignore=ECON001,ECON003
```

## Running tests

```bash
python -m pytest tests/
```

## What this doesn't do

- No type inference (can't tell if `client` is an HTTP client or a data structure)
- No cross-file analysis (can't track where a variable came from)
- No autofix (you have to think about the right solution)
- No config file yet (CLI flags only)

These are real limitations. A proper solution would integrate with a type checker. This is the duct-tape version that still catches real problems.

## Tech stack

- Python 3.10+
- AST module for parsing
- Zero external dependencies
