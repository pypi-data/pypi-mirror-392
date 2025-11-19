# Aitronos CLI

Unified command-line interface for managing all Aitronos services, including Streamline automations, AI assistants, and more.

## Installation

### Via pip (Recommended for Python developers)

```bash
pip install aitronos-cli
```

### Via Homebrew (Recommended for macOS/Linux)

```bash
# Add the Aitronos tap
brew tap aitronos/tap

# Install the CLI
brew install aitronos-cli
```

### Verify Installation

```bash
aitronos --version
```

## Quick Start

### 1. Authentication

Login to your Aitronos account:

```bash
aitronos auth login
```

### 2. Streamline Automations

Initialize a new Streamline project:

```bash
aitronos streamline init
```

Upload an automation:

```bash
aitronos streamline upload
```

Link a GitHub repository:

```bash
aitronos streamline link-repo
```

Execute an automation:

```bash
aitronos streamline execute <automation-id>
```

### 3. View Logs

```bash
aitronos streamline logs <automation-id>
```

## Features

- **Authentication**: Secure login with email verification
- **Streamline Automations**: Create, upload, and manage automations
- **GitHub Integration**: Link repositories for automatic syncing
- **Execution Management**: Run automations and view real-time logs
- **Template Support**: Initialize projects from templates
- **Interactive Menus**: User-friendly navigation with arrow keys

## Commands

### Authentication

- `aitronos auth login` - Login to your account
- `aitronos auth logout` - Logout from your account
- `aitronos auth status` - Check authentication status

### Streamline

- `aitronos streamline init` - Initialize a new project/repository
- `aitronos streamline upload` - Upload automation manually
- `aitronos streamline link-repo` - Link GitHub repository
- `aitronos streamline list` - List all automations
- `aitronos streamline execute <id>` - Execute an automation
- `aitronos streamline logs <id>` - View execution logs
- `aitronos streamline sync <id>` - Sync automation from GitHub
- `aitronos streamline delete <id>` - Delete an automation
- `aitronos streamline schedule <id>` - Set execution schedule
- `aitronos streamline remove-schedule <id>` - Remove schedule

## Configuration

The CLI stores configuration in `~/.aitronos/`:

- `config.yaml` - General configuration
- `auth.json` - Authentication tokens (never share this file)

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Aitronos-Development/aitronos.cli.git
cd aitronos.cli

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run compliance checks
./start-compliance.sh
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=aitronos_cli --cov-report=term

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

The project uses strict compliance checks:

```bash
# Run all compliance checks
./start-compliance.sh

# Run specific checks
uvx ruff check .              # Linting
uvx ruff format --check .     # Format check
uvx bandit -r aitronos_cli/   # Security scan
pytest tests/ --cov           # Tests with coverage
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Run tests and compliance checks
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feat/amazing-feature`)
7. Open a Pull Request

### Branch Naming Conventions

- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - How to deploy new versions
- [API Documentation](https://docs.aitronos.com/api) - Backend API reference
- [Compliance Guide](scripts/compliance/README.md) - Code quality standards

## Support

- **Documentation**: https://docs.aitronos.com
- **Issues**: https://github.com/Aitronos-Development/aitronos.cli/issues
- **Email**: support@aitronos.com

## License

MIT License - see [LICENSE](LICENSE) for details

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
