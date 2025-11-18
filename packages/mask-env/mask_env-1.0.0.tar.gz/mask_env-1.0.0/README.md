# mask-env

[![PyPI version](https://img.shields.io/pypi/v/mask-env.svg)](https://pypi.org/project/mask-env/)
[![Python versions](https://img.shields.io/pypi/pyversions/mask-env.svg)](https://pypi.org/project/mask-env/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Note: PyPI and Python version badges will appear after the first release is published to PyPI.

Create safe example files from secret files in multiple formats by replacing all secret-looking values with human-readable placeholders.

**Supports:** `.env`, `.JSON`, `.YAML`, `.INI/CFG/CONF`, `.properties`, `.TOML`, and `.key/certificate` files.

## Features

- 🔒 **Automatic secret detection** using heuristics (API keys, tokens, passwords, etc.)
- 📝 **Preserves formatting** (comments, blank lines, inline comments, export statements)
- 🚀 **Fast and efficient** - handles thousands of environment variables
- 🛡️ **Never logs secrets** - safe for production use
- 📦 **Zero dependencies** - uses only Python standard library
- 🎯 **Simple CLI** - one command to generate safe examples

## Installation

```bash
pip install mask-env
```

Optional extras (enable parsers for additional formats):

```bash
# YAML support
pip install "mask-env[yaml]"

# TOML support (Python < 3.11 uses tomli)
pip install "mask-env[toml]"

# Everything
pip install "mask-env[yaml,toml]"
```

## Usage

### Basic Usage

```bash
# Reads .env and creates .env.example
mask-env

# Works with any supported format (auto-detected)
mask-env config.json          # Creates config.json.example
mask-env secrets.yaml         # Creates secrets.yaml.example
mask-env config.ini           # Creates config.ini.example
mask-env application.properties  # Creates application.properties.example

# Specify custom output file
mask-env .env -o .env.example
mask-env config.json -o config.safe.json
```

### CLI Options

```text
usage: mask-env [-h] [-o OUTPUT] [input]

Create safe .env.example files from .env files

positional arguments:
  input                 Input .env file path (default: .env)

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output file path (default: input_path + ".example")
```

### Supported Formats

- **.env files** - `.env`, `.env.*` (fully supported)
- **JSON** - `config.json`, `credentials.json`, etc. (requires stdlib only)
- **YAML** - `config.yaml`, `secrets.yaml`, `docker-compose.yml` (requires `pyyaml` package)
- **INI/CFG/CONF** - `config.ini`, `settings.cfg`, `app.conf` (fully supported)
- **.properties** - `application.properties`, `gradle.properties` (fully supported)
- **TOML** - `pyproject.toml`, `config.toml` (requires `tomli` or `toml` package)
- **Key/Certificate files** - `.pem`, `.key`, `.crt`, `.p12`, `.pfx` (fully supported)

### What Gets Replaced?

The tool detects secrets using multiple heuristics:

1. **Key name patterns**: Keys containing `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PASS`, `API_KEY`, `PRIVATE`, `CREDENTIAL`, `AUTH`, `ACCESS_KEY`, `SECRET_KEY`

2. **Value characteristics**:
   - Long random strings (12+ characters, high entropy)
   - Connection strings with embedded passwords
   - Private key blocks (`BEGIN PRIVATE KEY`)

3. **Safe values preserved**:
   - URLs, file paths, email addresses
   - Short values, obvious non-secrets

## Python API

```python
from mask_env import process_file

# Works with any supported format (auto-detected)
secrets_replaced = process_file('config.json')
secrets_replaced = process_file('secrets.yaml')
secrets_replaced = process_file('.env')

# Custom input and output
secrets_replaced = process_file('input.json', 'output.safe.json')

# For .env files specifically, you can also use:
from mask_env import create_safe_example
secrets_replaced = create_safe_example('.env')
```

## Requirements

- Python 3.7+
- **Optional dependencies** (for extended format support):
  - `pyyaml` - for YAML file support: `pip install pyyaml`
  - `tomli` or `toml` - for TOML file support: `pip install tomli`

**Note:** Core functionality (`.env`, JSON, INI, `.properties`, key files) works with zero dependencies using only Python standard library.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- PyPI: `https://pypi.org/project/mask-env/`
- Source: `https://github.com/VishApp/mask-env`
- Issues: `https://github.com/VishApp/mask-env/issues`

