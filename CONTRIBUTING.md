# Contributing to db_connect

Thank you for your interest in contributing! Here's how you can help.

## Filing Issues

If you find a bug or have a feature request:

1. Check the [existing issues](https://github.com/markariosd3/db_connect/issues) to avoid duplicates
2. Click **New issue** and choose a template
3. Provide a clear title and description
4. Include:
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Python version and OS
   - Error messages or logs (if applicable)

## Submitting Pull Requests

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:
   ```powershell
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with clear, descriptive commits
4. **Test your changes**:
   ```powershell
   python -m pip install -r requirements.txt
   python -m db_connection --help
   ```
5. **Push to your fork**:
   ```powershell
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** on GitHub with:
   - A clear title and description
   - Reference to any related issues (e.g., "Closes #123")
   - Explanation of what changed and why

## Development Guidelines

- Keep changes focused and well-tested
- Follow PEP 8 style guidelines
- Add tests for new features when possible
- Update documentation if needed
- Commit messages should be clear and descriptive

## Questions?

Feel free to open an issue with the `question` label or reach out in existing discussions.

Thanks for contributing!
