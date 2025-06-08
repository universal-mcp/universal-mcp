# Contributing to AgentR

Thank you for your interest in contributing to AgentR! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

1. Fork the repository at git@github.com:AgentrDev/universal-mcp.git
2. Clone your fork
3. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[test]"
   ```

5. Make your changes and ensure tests pass:
   ```bash
   pytest
   ```

6. Commit your changes following conventional commits:
   ```bash
   git commit -m "feat: add new feature"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Open a Pull Request against the main repository

## 📝 Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Include docstrings for functions and classes
- Keep functions focused and single-purpose

### Testing
- Add tests for new features
- Ensure all tests pass before submitting PR
- Maintain or improve code coverage

### Pull Requests
- Keep PRs focused on a single change
- Include a clear description of changes
- Reference any related issues
- Update documentation as needed

### Commit Messages
Follow conventional commits format:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Test updates
- chore: Maintenance tasks

## 🐛 Reporting Issues

- Search existing issues before creating new ones
- Include clear steps to reproduce
- Provide system information
- Add relevant logs or screenshots

## 📚 Documentation

- Keep README.md updated
- Document new features
- Include docstrings
- Update CHANGELOG.md for significant changes

