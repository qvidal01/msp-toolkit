# Contributing to MSP Toolkit

Thank you for your interest in contributing to MSP Toolkit! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/qvidal01/msp-toolkit/issues)
- If not, create a new issue with:
  - Clear title and description
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details (OS, Python version)

### Suggesting Enhancements

- Check if the enhancement has been suggested
- Create an issue with:
  - Clear use case description
  - Why this would be useful
  - Possible implementation approach

### Pull Requests

1. **Fork and clone** the repository
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**:
   ```bash
   poetry install --with dev
   pre-commit install
   ```

4. **Make your changes**:
   - Write clear, documented code
   - Add type hints
   - Follow existing code style
   - Add tests for new functionality

5. **Test your changes**:
   ```bash
   # Run tests
   pytest

   # Check coverage
   pytest --cov=src/msp_toolkit

   # Lint code
   ruff check src/ tests/
   black --check src/ tests/

   # Type check
   mypy src/
   ```

6. **Commit your changes**:
   - Use conventional commit messages:
     - `feat: add new feature`
     - `fix: correct bug`
     - `docs: update documentation`
     - `test: add tests`
     - `refactor: code improvement`

7. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```
   - Fill out the PR template
   - Link related issues
   - Ensure CI passes

## Development Guidelines

### Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use Ruff for linting
- Add type hints to all functions
- Write comprehensive docstrings

### Testing

- Write unit tests for new features
- Maintain >80% code coverage
- Use pytest fixtures for reusable test data
- Mock external dependencies

### Documentation

- Update README.md if adding user-facing features
- Add docstrings to all public APIs
- Update CHANGELOG.md
- Add examples for significant features

## Good First Issues

Looking for something to work on? Check out issues labeled [`good first issue`](https://github.com/qvidal01/msp-toolkit/labels/good%20first%20issue).

Some areas that always need help:
- Additional RMM integrations
- Backup provider adapters
- Documentation improvements
- Example scripts
- Test coverage

## Plugin Development

To create a custom integration:

1. Inherit from the appropriate base class (e.g., `RMMAdapter`)
2. Implement all abstract methods
3. Add configuration support
4. Write tests
5. Document the integration

Example:
```python
from msp_toolkit.integrations.rmm.base import RMMAdapter

class MyRMM(RMMAdapter):
    def get_devices(self, client_id):
        # Your implementation
        pass
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `src/msp_toolkit/__init__.py`
2. Update CHANGELOG.md
3. Create release commit: `chore(release): v1.0.0`
4. Tag release: `git tag v1.0.0`
5. Push: `git push && git push --tags`
6. GitHub Actions will build and publish

## Questions?

- Open a [Discussion](https://github.com/qvidal01/msp-toolkit/discussions)
- Email: support@aiqso.io

Thank you for contributing! 🎉
