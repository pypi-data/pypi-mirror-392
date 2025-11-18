# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **ConnectVM CLI** (cvm), a command-line interface client for ConnectVM Cloud. It is based on OpenStack's python-openstackclient and provides a unified command-line interface for managing cloud resources including Compute, Identity, Image, Network, Block Storage, and Object Storage services.

The CLI is branded as `cvm` (ConnectVM) and communicates with OpenStack-compatible APIs running at connectvm.com.

## Build and Development Commands

### Installation

Install from source in development mode:
```bash
pip install -e .
```

Install dependencies:
```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
```

### Testing

Run all tests:
```bash
tox
```

Run specific test environment:
```bash
tox -e py311  # Run tests with Python 3.11
tox -e pep8   # Run linting checks
```

Run tests with stestr directly:
```bash
stestr run
```

Run a single test file:
```bash
python -m stestr run openstackclient.tests.unit.compute.v2.test_server
```

Run a specific test:
```bash
python -m stestr run openstackclient.tests.unit.compute.v2.test_server.TestServerCreate.test_server_create
```

### Linting and Formatting

Run pre-commit hooks:
```bash
pre-commit run --all-files
```

Run ruff linting:
```bash
ruff check .
```

Format code with ruff:
```bash
ruff format .
```

Type checking with mypy:
```bash
mypy openstackclient
```

### Building Documentation

Build documentation locally:
```bash
tox -e docs
```

View built docs:
```bash
open doc/build/html/index.html
```

## Architecture Overview

### Command Entry Point

- **Main Entry Point**: `openstackclient/shell.py` - Contains `OpenStackShell` class and `main()` function
- **Command Registration**: Uses stevedore plugin system via entry points in `pyproject.toml`
- **CLI Command**: `cvm` (registered in `[project.scripts]` section)

### Plugin Architecture

The CLI uses a plugin-based architecture powered by stevedore and cliff:

1. **Command Manager**: `commandmanager.CommandManager('openstack.cli')` loads commands dynamically
2. **Entry Points**: Commands are registered via setuptools entry points in `pyproject.toml`
3. **API Versioning**: Each service (compute, network, identity, etc.) supports multiple API versions

Entry point groups:
- `openstack.cli.base` - Base service client registration
- `openstack.common` - Cross-service commands (quota, limits, etc.)
- `openstack.compute.v2` - Compute/Nova commands
- `openstack.identity.v3` - Identity/Keystone v3 commands
- `openstack.network.v2` - Network/Neutron commands
- `openstack.image.v2` - Image/Glance commands
- `openstack.volume.v3` - Block Storage/Cinder commands
- `openstack.object_store.v1` - Object Storage/Swift commands

### Module Structure

```
openstackclient/
├── shell.py              # Main CLI shell and entry point
├── common/               # Common utilities and cross-service commands
│   ├── clientmanager.py  # Manages API clients for different services
│   ├── module.py         # Command/module listing
│   ├── quota.py          # Quota management commands
│   └── ...
├── compute/              # Compute service (Nova) commands
│   └── v2/               # API version 2
│       ├── server.py     # Server (VM instance) commands
│       ├── flavor.py     # Flavor (instance type) commands
│       ├── keypair.py    # SSH keypair commands
│       └── ...
├── identity/             # Identity service (Keystone) commands
│   ├── v2_0/             # API version 2
│   └── v3/               # API version 3
│       ├── user.py       # User management
│       ├── project.py    # Project/tenant management
│       ├── token.py      # Token operations
│       └── ...
├── network/              # Network service (Neutron) commands
│   └── v2/
│       ├── network.py    # Network management
│       ├── subnet.py     # Subnet management
│       ├── router.py     # Router management
│       ├── port.py       # Port management
│       ├── security_group.py
│       └── ...
├── image/                # Image service (Glance) commands
│   └── v2/
│       └── image.py      # Image management
├── volume/               # Block storage (Cinder) commands
│   └── v3/
│       ├── volume.py     # Volume management
│       ├── volume_snapshot.py
│       └── ...
└── object/               # Object storage (Swift) commands
    └── v1/
        ├── container.py  # Container management
        └── object.py     # Object management
```

### Command Implementation Pattern

All commands follow cliff's command pattern:

1. Commands inherit from `command.Command` (for actions) or `command.Lister`/`command.ShowOne` (for data display)
2. Each command class implements:
   - `get_parser(self, prog_name)` - Define command arguments using argparse
   - `take_action(self, parsed_args)` - Execute the command logic

Example command structure:
```python
class CreateServer(command.ShowOne):
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('name', help='Server name')
        # ... more arguments
        return parser
    
    def take_action(self, parsed_args):
        # Implementation
        # Returns tuple of (columns, data) for ShowOne
        # Returns list for Lister
```

### Client Manager

`openstackclient/common/clientmanager.py` manages all service API clients:

- Lazy loads clients on first access
- Handles API versioning automatically
- Manages authentication across all services
- Uses openstacksdk as the primary client library

Service clients are accessed via:
```python
self.app.client_manager.compute  # Nova client
self.app.client_manager.identity  # Keystone client
self.app.client_manager.network   # Neutron client
# etc.
```

### Authentication Flow

1. Configuration loaded from (in order of precedence):
   - Command-line options (`--os-username`, `--os-password`, etc.)
   - Environment variables (`OS_USERNAME`, `OS_PASSWORD`, etc.)
   - `clouds.yaml` file
2. `clientmanager.py` initializes openstacksdk connection
3. Authentication happens on first API call (lazy auth)
4. Token cached for subsequent requests

## Key Design Patterns

### Command Registration

Commands are NOT imported directly. They're discovered via entry points:
- Adding new commands requires updating `pyproject.toml` entry points
- Command module must be in the correct service/version directory
- Entry point format: `command_name = "module.path:ClassName"`

### API Version Handling

- Each service has a `DEFAULT_API_VERSION` in its client module
- Version can be overridden via `--os-<service>-api-version` or `OS_<SERVICE>_API_VERSION`
- Command groups are loaded based on requested API version
- Commands should handle version-specific features gracefully

### Error Handling

- Use `osc_lib.exceptions` for user-facing errors
- Wrap SDK exceptions with meaningful messages
- Return appropriate exit codes (non-zero on error)

### Output Formatting

- Use cliff's formatting for table/list/show output
- Support `-f {json,yaml,table,value,shell}` for all list/show commands
- Use `format_columns` from `osc_lib.cli` for special column formatting

## Important Files to Know

- `pyproject.toml` - Project metadata, dependencies, entry points, tool configuration
- `setup.cfg` - Additional setuptools metadata
- `requirements.txt` - Runtime dependencies
- `test-requirements.txt` - Testing dependencies
- `tox.ini` - Tox test environment configuration
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `openstackclient/shell.py` - Main CLI shell
- `openstackclient/common/clientmanager.py` - Service client manager

## Testing Conventions

- Tests use `unittest` framework
- Test files mirror source structure: `openstackclient/tests/unit/<service>/v<version>/test_<module>.py`
- Use `openstackclient.tests.unit.fakes` for test data
- Mock external API calls using `unittest.mock`
- Functional tests require a working cloud environment

## ConnectVM-Specific Notes

- The command is `cvm` NOT `openstack`
- Package name is `python-cvmclient`
- Internal module structure remains `openstackclient` for compatibility
- Points to ConnectVM Cloud endpoints (default: cloud.connectvm.com)
- All OpenStack functionality is available under the `cvm` command

## Common Development Workflows

### Adding a New Command

1. Create command class in appropriate service/version module (e.g., `openstackclient/compute/v2/mycommand.py`)
2. Inherit from `command.Command`, `command.ShowOne`, or `command.Lister`
3. Implement `get_parser()` and `take_action()` methods
4. Add entry point to `pyproject.toml` under appropriate section
5. Write unit tests in `openstackclient/tests/unit/`
6. Run tests: `tox -e py311`

### Debugging

- Use `--debug` flag for verbose output
- Check `~/.config/openstack/` for cached data
- Use `--os-cloud <cloud-name>` to specify cloud config from clouds.yaml
- Set `OS_DEBUG=1` for SDK-level debugging

### Modifying Existing Commands

1. Locate command in appropriate service module
2. Modify `get_parser()` for argument changes
3. Update `take_action()` for logic changes
4. Update corresponding tests
5. Run specific test: `stestr run test_module.TestClass.test_method`
