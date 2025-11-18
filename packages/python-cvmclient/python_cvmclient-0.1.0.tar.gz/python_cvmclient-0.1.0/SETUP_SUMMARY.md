# ConnectVM CLI Setup Summary

## What Was Done

This repository contains a ConnectVM-branded CLI tool based on the OpenStack python-openstackclient project.

### Key Changes Made

#### 1. Branding Changes

**Command Name**: Changed from `openstack` to `cvm`
- Updated `pyproject.toml` entry point: `[project.scripts]` now has `cvm = "openstackclient.shell:main"`
- Updated `setup.cfg` console script

**Package Name**: Changed from `python-openstackclient` to `python-cvmclient`
- Updated in `pyproject.toml`
- Updated in `setup.cfg`

**Project Metadata**:
- Author: ConnectVM
- Email: support@connectvm.com
- Homepage: https://connectvm.com/
- Repository: https://github.com/connectvm/connectvm-cli/
- Description: "ConnectVM Command-line Client"

#### 2. Documentation Updates

**README.rst**:
- Completely rewritten for ConnectVM branding
- Updated all command examples from `openstack` to `cvm`
- Changed auth URL examples to `cloud.connectvm.com`
- Updated cloud configuration examples

**New Files Created**:
- `CLAUDE.md` - Comprehensive developer guide for Claude Code
- `INSTALL.md` - Installation and usage guide
- `SETUP_SUMMARY.md` - This file

#### 3. Code Updates

**openstackclient/shell.py**:
- Updated docstring: "Command-line interface to the ConnectVM Cloud APIs"

### What Stays the Same

#### Internal Structure
- Module name remains `openstackclient` for compatibility with dependencies
- All internal imports and class names unchanged
- Entry point namespaces remain `openstack.*` for plugin compatibility
- Uses same dependencies (openstacksdk, osc-lib, etc.)

#### Functionality
- 100% compatible with OpenStack APIs
- All commands work identically to python-openstackclient
- Supports all OpenStack services:
  - Compute (Nova)
  - Identity (Keystone)
  - Image (Glance)
  - Network (Neutron)
  - Block Storage (Cinder)
  - Object Storage (Swift)

## Architecture Highlights

### Command Structure

The CLI uses a plugin-based architecture:

```
cvm <command> <subcommand> [options]

Examples:
cvm server list
cvm server create --flavor m1.small myserver
cvm network create mynetwork
cvm volume create --size 10 myvolume
```

### Plugin System

Commands are registered via setuptools entry points in `pyproject.toml`:

```toml
[project.entry-points."openstack.compute.v2"]
server_create = "openstackclient.compute.v2.server:CreateServer"
server_list = "openstackclient.compute.v2.server:ListServer"
# ... etc
```

### Service Support

| Service | Module | API Versions | Commands |
|---------|--------|--------------|----------|
| Compute | openstackclient.compute | v2 | server, flavor, keypair, etc. |
| Identity | openstackclient.identity | v2, v3 | user, project, role, token, etc. |
| Network | openstackclient.network | v2 | network, subnet, router, port, etc. |
| Image | openstackclient.image | v1, v2 | image, etc. |
| Block Storage | openstackclient.volume | v2, v3 | volume, snapshot, backup, etc. |
| Object Storage | openstackclient.object | v1 | container, object, etc. |

## How to Use

### Installation

```bash
cd connectvm-cli
pip install -e .
```

### Configuration

Set environment variables:
```bash
export OS_AUTH_URL=https://cloud.connectvm.com:5000/v3
export OS_USERNAME=your-username
export OS_PASSWORD=your-password
export OS_PROJECT_NAME=your-project
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

Or use clouds.yaml in `~/.config/openstack/clouds.yaml`:
```yaml
clouds:
  connectvm:
    auth:
      auth_url: https://cloud.connectvm.com:5000/v3
      username: your-username
      password: your-password
      project_name: your-project
      user_domain_name: Default
      project_domain_name: Default
```

### Usage

```bash
# List servers
cvm server list

# Create server
cvm server create --flavor m1.small --image ubuntu myserver

# Get help
cvm help
cvm server create --help
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run all tests
tox

# Run specific test environment
tox -e py311

# Run linting
tox -e pep8
```

### Adding New Commands

1. Create command class in appropriate module (e.g., `openstackclient/compute/v2/newcmd.py`)
2. Register in `pyproject.toml` under the correct entry point section
3. Write tests in `openstackclient/tests/unit/`
4. Run tests

### Code Style

- Python 3.10+ required
- Uses ruff for linting and formatting
- Pre-commit hooks available
- Type hints supported via mypy

## Technical Details

### Dependencies

Core dependencies:
- `openstacksdk` - OpenStack SDK
- `osc-lib` - OpenStack Client library
- `cliff` - Command-line framework
- `python-keystoneclient` - Keystone client
- `python-cinderclient` - Cinder client
- `pbr` - Python Build Reasonableness

### Build System

- Uses PEP 517/518 build system
- Backend: pbr (Python Build Reasonableness)
- Configuration: `pyproject.toml` and `setup.cfg`

### Entry Points

The package registers the `cvm` command as a console script that points to `openstackclient.shell:main`.

All service commands are loaded dynamically via stevedore plugin discovery using entry points.

## Next Steps

### For Users

1. Install the package: `pip install -e .`
2. Configure authentication (see INSTALL.md)
3. Start using: `cvm server list`

### For Developers

1. Read CLAUDE.md for detailed architecture
2. Set up development environment
3. Run tests: `tox`
4. Make changes and test
5. Use pre-commit hooks: `pre-commit install`

## Notes

- The CLI is fully compatible with any OpenStack-based cloud
- ConnectVM Cloud runs OpenStack APIs
- All standard OpenStack features are supported
- The internal module structure intentionally keeps `openstackclient` naming for dependency compatibility
- Only user-facing elements (command name, package name, docs) are rebranded to ConnectVM
