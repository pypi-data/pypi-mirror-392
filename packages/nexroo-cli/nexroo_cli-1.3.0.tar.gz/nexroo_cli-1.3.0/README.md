# Nexroo CLI

> **📚 Full Documentation:** https://docs.nexroo.ai

CLI wrapper for Nexroo workflow engine with authentication and package management.

## Prerequisites

**Python 3.11+** is required for addon packages to work. The engine itself is a standalone binary, but addons are installed to your system Python.

- **Windows:** [Download Python](https://www.python.org/downloads/)
- **Linux:** `apt install python3` or `yum install python3`
- **macOS:** `brew install python3`

## Installation

### Quick Install (Recommended)

```bash
# install CLI
pip install nexroo-cli
# use CLI to install engine
nexroo install
```

or

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/nexroo-ai/nexroo-cli/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/nexroo-ai/nexroo-cli/main/install.ps1 | iex
```


## Quick Start

After installation, authenticate and run your first workflow:

```bash
# Authenticate with Synvex
nexroo login

# Run a workflow
nexroo run workflow.json
```

## Usage

### Authentication Commands

#### Login
```bash
nexroo login
```

Opens browser for Zitadel authentication. Credentials stored encrypted for 30 days.

#### Logout
```bash
nexroo logout
```

Clears saved credentials.

#### Status
```bash
nexroo status
```

Shows authentication status and token expiration.

### Running Workflows

**With authentication** (SaaS features enabled):
```bash
nexroo run workflow.json [entrypoint]
```

**Without authentication** (local-only mode):
```bash
nexroo run workflow.json --no-auth
```

### Additional Options

```bash
nexroo run workflow.json [entrypoint] [options]
```

Refer to [Nexroo Documentation](https://docs.nexroo.ai) for all available options.

### Update

```bash
pip install --upgrade nexroo-cli
nexroo update
```

### Uninstall

```bash
# Uninstall engine, addons, and all data
nexroo uninstall

# Remove the CLI package
pip uninstall nexroo-cli
```

## Addon Packages

### Installing Addons

Addons extend the engine with additional capabilities (AI providers, databases, storage, etc.).

```bash
# Install an addon
nexroo install redis

# List available addons
nexroo addon list --available

# List installed addons
nexroo addon list
```

### Troubleshooting Addon Issues

**If the engine can't find an addon:**

1. Verify Python 3.11+ is installed:
   ```bash
   python3 --version
   ```

2. Check addon installation:
   ```bash
   nexroo addon list
   python3 -m pip list | grep rooms-pkg
   ```

3. Reinstall addon:
   ```bash
   nexroo addon install <package> --upgrade
   ```

## Storage Locations

- Engine binary: `~/.nexroo/bin/nexroo-engine`
- Addon packages: System Python's site-packages
- Encrypted tokens: `~/.nexroo/auth_token.enc`
- Encryption key: `~/.nexroo/.key`
- Addon metadata: `~/.nexroo/installed_packages.json`

## Troubleshooting

For debug use '--verbose'

### Authentication fails
```bash
nexroo logout
nexroo login
```

### Token expired
```bash
nexroo status
nexroo login   # Re-authenticate
```

## Documentation

See [Nexroo Documentation](https://docs.nexroo.ai) to know how to use Nexroo workflow engine.

## License

PolyForm Noncommercial License 1.0.0 - see [LICENSE](./LICENSE) file for details.
Or on <https://polyformproject.org/licenses/noncommercial/1.0.0>

## Support

- GitHub Issues: https://github.com/nexroo-ai/nexroo-cli/issues