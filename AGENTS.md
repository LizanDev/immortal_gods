# AGENTS.md - Python Project Guidelines

## Project Setup

### Quick Start - Initialize Project

**Option 1: Automated Script (Recommended)**

```bash
# Run the initialization script
./scripts/init.ps1

# Or with custom project name
./scripts/init.ps1 -ProjectName "my-awesome-project"
```

**Option 2: Manual Setup**

```bash
# 1. Initialize UV project
uv init

# 2. Add core dependencies
uv add pytest ruff mypy pre-commit python-dotenv

# 3. Create .env from example
cp .env.example .env

# 4. Install pre-commit hooks
uv run pre-commit install

# 5. Sync environment
uv sync
```

### Virtual Environment with UV

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project
uv init

# Add dependencies
uv add <package>

# Add dev dependencies
uv add --dev pytest ruff mypy pre-commit pip-audit bandit

# Sync environment (installs from uv.lock)
uv sync

# Run commands in venv context
uv run python -m src.main
uv run pytest
uv run ruff check .
```

### UV Workflow Rules

- Always use `uv add/remove` instead of editing `requirements.txt` manually
- `uv.lock` must be committed to the repo for reproducible builds
- Use `uv sync --frozen` in CI to ensure lockfile is respected
- Use `uv run` to execute commands inside the venv

## Project Structure

```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       ├── services/
│       └── utils/
├── tests/
│   ├── conftest.py
│       ├── test_main.py
│   └── fixtures/
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── README.md
```

## Configuration (pyproject.toml)

All tool configuration goes in `pyproject.toml`. Never use separate config files.

```toml
[project]
name = "project-name"
version = "0.1.0"
description = ""
requires-python = ">=3.11"
dependencies = []

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]

[tool.ruff.lint.isort]
known-first-party = ["src"]

[tool.mypy]
strict = true
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"
pythonpath = ["."]
```

## Code Quality Standards

### Clean Code Principles

- **Functions**: Max 20 lines. Single responsibility.
- **Files**: Max 200 lines. Split into modules if longer.
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- **No magic numbers**: Use named constants.
- **Type hints**: Required on all function signatures.
- **Docstrings**: Google style on all public functions/classes.
- **Imports**: Absolute imports only. Group: stdlib, third-party, local.

```python
# Good
def calculate_discount(price: float, percentage: float) -> float:
    """Calculate the discount amount for a given price.

    Args:
        price: Original price of the item.
        percentage: Discount percentage (0-100).

    Returns:
        The discount amount.
    """
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")
    return price * (percentage / 100)
```

### Linting & Formatting

```bash
# Format
uv run ruff format .

# Lint
uv run ruff check . --fix

# Type check
uv run mypy src/
```

Run these before committing any changes. Better yet, use pre-commit hooks.

## Git Conventions

### Commit Messages (Conventional Commits)

Format: `<type>(<scope>): <description>`

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or modifying tests |
| `docs` | Documentation changes |
| `chore` | Maintenance tasks |
| `perf` | Performance improvement |

```
feat(auth): add JWT token refresh endpoint
fix(payments): handle null amount in transaction
refactor(services): extract email logic to module
test(api): add integration tests for user CRUD
```

### Branch Naming

```
feat/user-authentication
fix/payment-rounding-error
refactor/extract-email-service
```

## Error Handling

### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(AppError):
    """Input validation failed."""


class NotFoundError(AppError):
    """Requested resource not found."""


class ExternalServiceError(AppError):
    """Third-party service failure."""
```

### Rules

- **Never** catch bare `Exception` without re-raising
- **Never** swallow exceptions silently (empty except)
- **Always** log exceptions with context before re-raising
- **Wrap** external exceptions into domain exceptions
- User-facing messages must be generic. Internal details go to logs.

```python
# Bad
try:
    result = api_call()
except Exception:
    pass  # silent failure

# Bad
except Exception as e:
    return f"Error: {e}"  # leaks internals

# Good
try:
    result = external_api.call()
except ExternalAPIError as e:
    logger.error("external_api_failed", service="payments", error=str(e))
    raise ExternalServiceError("Payment service unavailable") from e
```

## Logging

### Standard Logging Setup

```python
import logging
import sys

def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging."""
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=getattr(logging, level.upper()),
        stream=sys.stdout,
    )

logger = logging.getLogger(__name__)
```

### Rules

- **Never** log sensitive data (passwords, tokens, PII)
- **Always** use structured key-value pairs for context
- Use appropriate levels: `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`
- Use `logger.exception()` to include stack trace automatically

```python
# Bad
logger.info(f"User {email} logged in with password {password}")

# Bad
logger.info("Something happened")

# Good
logger.info("user_login", extra={"user_id": user.id, "ip": request.ip})

# Good - with exception
try:
    process_payment(order)
except PaymentError:
    logger.exception("payment_failed", extra={"order_id": order.id})
    raise
```

## Testing

### Unit Tests with pytest

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific file
uv run pytest tests/test_module.py -v

# Run by keyword
uv run pytest -k "discount" -v
```

### Test Conventions

- Test files: `tests/test_<module>.py`
- Test functions: `test_<what>_<when>_<expected>`
- Use `conftest.py` for shared fixtures
- Mock external dependencies (APIs, databases, filesystem)
- Minimum coverage: 80%
- Each test must be independent and idempotent

```python
import pytest
from src.calculator import calculate_discount


def test_calculate_discount_returns_correct_amount():
    assert calculate_discount(100.0, 10.0) == 10.0


def test_calculate_discount_raises_on_invalid_percentage():
    with pytest.raises(ValueError):
        calculate_discount(100.0, 150.0)


@pytest.fixture
def sample_data():
    return {"price": 50.0, "quantity": 3}
```

## Security - Sensitive Data Protection

### NEVER Commit or Expose

- API keys, tokens, secrets
- Passwords, credentials
- Database connection strings with credentials
- Private keys or certificates
- Personal data (PII): emails, IDs, phone numbers

### Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise EnvironmentError("API_KEY not set in environment")
```

### .gitignore (required entries)

```
.env
.env.*
*.key
*.pem
*.p12
credentials.json
secrets.yaml
__pycache__/
.venv/
*.pyc
.mypy_cache/
.pytest_cache/
.ruff_cache/
htmlcov/
dist/
*.egg-info/
```

### Data Handling Rules

- **Logs**: Never log sensitive data. Sanitize before logging.
- **Errors**: Never expose internal paths, keys, or stack traces to users.
- **Serialization**: Strip sensitive fields before sending responses.
- **Configs**: Use `.env` files locally, proper secret managers in production.

### Security Scanning

```bash
# Audit dependencies for known vulnerabilities
uv run pip-audit

# Static analysis for security issues
uv run bandit -r src/
```

Run these periodically to catch security issues in dependencies and code.

### Pre-commit Secret Scanning

```bash
# Install hooks
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

## CI/CD

### GitHub Actions (`.github/workflows/ci.yml`)

Runs on every push and PR. See `ci.yml` in repo root.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --frozen

      - name: Lint
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy src/

      - name: Test
        run: uv run pytest

      - name: Security audit
        run: uv run pip-audit

      - name: Bandit scan
        run: uv run bandit -r src/
```

## Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ src/

CMD ["uv", "run", "python", "-m", "src.main"]
```

### Docker Compose (optional)

```yaml
services:
  app:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
```

## Commands Reference

| Action | Command |
|---|---|
| Init project | `uv init` |
| Add dependency | `uv add <package>` |
| Add dev dependency | `uv add --dev <package>` |
| Sync environment | `uv sync` |
| Format | `uv run ruff format .` |
| Lint | `uv run ruff check . --fix` |
| Type check | `uv run mypy src/` |
| Test | `uv run pytest` |
| Coverage | `uv run pytest --cov=src --cov-report=term-missing` |
| Pre-commit install | `uv run pre-commit install` |
| Pre-commit run | `uv run pre-commit run --all-files` |
| Security audit | `uv run pip-audit` |
| Bandit scan | `uv run bandit -r src/` |
| Run app | `uv run python -m src.main` |

## AI Assistant Guidelines

### Teaching-First Approach

The AI assistant must **never modify code directly**. Instead:

1. **Guide, don't implement**: Explain what needs to be done and let the user write the code
2. **Show examples, not solutions**: Provide reference examples that the user adapts
3. **Explain the why**: Always explain the reasoning behind suggestions
4. **Step-by-step instructions**: Break down complex tasks into actionable steps
5. **Encourage learning**: Ask questions that prompt critical thinking

```
Bad: "I'll add that function for you"
Good: "You should add a function that does X. Here's the pattern to follow..."
```

This ensures the user learns and understands the codebase thoroughly.

---

## ⚠️ MANDATORY RULES FOR AI ASSISTANT

### CRITICAL - ALWAYS FOLLOW

1. **NEVER write or modify code files directly** - Only provide guidance, examples, and instructions
2. **ALWAYS read AGENTS.md before responding** - This file is the single source of truth
3. **ALWAYS use `uv` commands** - Never use `pip`, `poetry`, or `virtualenv` directly
4. **ALWAYS run linting and type checking** - `uv run ruff check .` and `uv run mypy src/` before any commit
5. **ALWAYS run security scans** - `uv run pip-audit` and `uv run bandit -r src/` periodically
6. **NEVER commit or push without explicit user request** - Wait for user confirmation
7. **ALWAYS test locally first** - All changes must be tested on the local dev server (`http://localhost:8000`) before commit. The user must verify the change works correctly. Only after the user says "commit" or "pushea" should you stage, commit, and push.
8. **ALWAYS follow Conventional Commits** - Format: `type(scope): description`
9. **NEVER commit sensitive data** - No `.env`, credentials, keys, tokens, or PII
10. **ALWAYS use absolute imports** - No relative imports in source code
11. **ALWAYS add type hints** - Required on all function signatures
12. **ALWAYS add docstrings** - Google style on all public functions/classes

### CODE QUALITY CHECKLIST (Before any code change)

- [ ] Type hints on all functions
- [ ] Docstrings (Google style) on public functions
- [ ] Max 20 lines per function
- [ ] Max 200 lines per file
- [ ] No magic numbers (use named constants)
- [ ] Proper error handling (custom exceptions)
- [ ] No sensitive data in logs
- [ ] Follows naming conventions (snake_case, PascalCase)

### COMMAND EXECUTION RULES

| Task | Required Command |
|------|------------------|
| Add dependency | `uv add <package>` |
| Run Python | `uv run python ...` |
| Run tests | `uv run pytest ...` |
| Format code | `uv run ruff format .` |
| Lint code | `uv run ruff check . --fix` |
| Type check | `uv run mypy src/` |

### VIOLATION RESPONSE

If the AI assistant violates any rule:
1. User should immediately point out the violation
2. AI must acknowledge and correct the behavior
3. AI must re-read the relevant section of AGENTS.md
4. AI must explain what went wrong and how to avoid it

### SKILLS USAGE

- Use `find-skills` when user asks about extending capabilities
- Use `python-performance-optimization` when debugging slow code
- Load skills before starting related tasks

---

**Reminder**: This AGENTS.md is MANDATORY. Every response must comply with these guidelines.
