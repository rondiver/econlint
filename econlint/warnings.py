"""Warning dataclass and explanation templates for econlint."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Warning:
    """Represents a single linter warning."""

    code: str
    message: str
    file: Path
    line: int
    pattern: str
    explanation: str


EXPLANATIONS = {
    "ECON001": """Economic risk: Each loop iteration incurs API/network cost.
At 1000 iterations, this becomes 1000 billable calls.
Under partial failure, retries multiply this further.

Even if the collection is small today, data growth or
upstream changes can make this unbounded.

Consider: Batch the calls, or add explicit bounds.""",
    "ECON002": """Economic risk: Without a retry limit, transient failures
cause infinite retry loops. Each retry costs money and
keeps connections/resources open.

A downstream outage becomes a self-inflicted denial of
service with unbounded costs.

Consider: Set stop_after_attempt(n) or a max retry count.""",
    "ECON003": """Economic risk: This is an N+1 pattern. For N items in the
collection, you make N separate calls instead of 1 batch.

At N=1000, you pay for 1000 round trips instead of 1.
Latency also multiplies: 1000 × 50ms = 50 seconds.

Consider: Use a batch API, or prefetch all data at once.""",
    "ECON004": """Economic risk: Unbounded concurrency can spawn thousands
of simultaneous requests. APIs rate-limit or charge per
call, and you may exhaust connection pools.

A burst of 10,000 concurrent requests can trigger
rate limiting, increased costs, or cascading failures.

Consider: Use a Semaphore or set max_workers explicitly.""",
}
