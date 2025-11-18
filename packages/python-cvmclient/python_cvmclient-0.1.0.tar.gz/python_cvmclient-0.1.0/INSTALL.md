# ConnectVM CLI Installation Guide

## Quick Start

### Install from Source

```bash
# Clone the repository
cd connectvm-cli

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Verify Installation

```bash
# Check the cvm command is available
cvm --version

# Get help
cvm --help

# List available commands
cvm help
```

## Configuration

### Method 1: Environment Variables

Create a file (e.g., `connectvm-openrc.sh`) with your credentials:

```bash
export OS_AUTH_URL=https://cloud.connectvm.com:5000/v3
export OS_PROJECT_NAME=your-project-name
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USERNAME=your-username
export OS_USER_DOMAIN_NAME=Default
export OS_PASSWORD=your-password
export OS_REGION_NAME=RegionOne
export OS_IDENTITY_API_VERSION=3
```

Source the file before using the CLI:
```bash
source connectvm-openrc.sh
cvm server list
```

### Method 2: clouds.yaml Configuration

Create `~/.config/openstack/clouds.yaml`:

```yaml
clouds:
  connectvm:
    auth:
      auth_url: https://cloud.connectvm.com:5000/v3
      project_name: your-project-name
      project_domain_name: Default
      username: your-username
      user_domain_name: Default
      password: your-password
    region_name: RegionOne
    identity_api_version: 3
```

Use with `--os-cloud` option:
```bash
cvm --os-cloud connectvm server list
```

### Method 3: Command-Line Options

Pass credentials directly:
```bash
cvm --os-auth-url https://cloud.connectvm.com:5000/v3 \
    --os-project-name your-project \
    --os-username your-username \
    --os-password your-password \
    server list
```

## Common Commands

### Servers (Virtual Machines)

```bash
# List servers
cvm server list

# Create a server
cvm server create --flavor m1.small --image ubuntu-20.04 --network private my-server

# Show server details
cvm server show my-server

# Delete server
cvm server delete my-server

# Reboot server
cvm server reboot my-server

# Stop/Start server
cvm server stop my-server
cvm server start my-server
```

### Images

```bash
# List images
cvm image list

# Show image details
cvm image show ubuntu-20.04

# Create image from server
cvm image create --server my-server my-snapshot
```

### Flavors

```bash
# List flavors
cvm flavor list

# Show flavor details
cvm flavor show m1.small
```

### Networks

```bash
# List networks
cvm network list

# Create network
cvm network create my-network

# List subnets
cvm subnet list

# Create subnet
cvm subnet create --network my-network --subnet-range 192.168.1.0/24 my-subnet
```

### Volumes

```bash
# List volumes
cvm volume list

# Create volume
cvm volume create --size 10 my-volume

# Attach volume to server
cvm server add volume my-server my-volume

# Detach volume
cvm server remove volume my-server my-volume
```

### Security Groups

```bash
# List security groups
cvm security group list

# Create security group
cvm security group create my-secgroup

# Add rule (allow SSH)
cvm security group rule create --protocol tcp --dst-port 22 my-secgroup
```

### Keypairs

```bash
# List keypairs
cvm keypair list

# Create keypair
cvm keypair create my-key > my-key.pem
chmod 600 my-key.pem

# Import existing public key
cvm keypair create --public-key ~/.ssh/id_rsa.pub my-key
```

### Identity (Users, Projects, Roles)

```bash
# List users
cvm user list

# List projects
cvm project list

# List roles
cvm role list

# Assign role to user
cvm role add --user alice --project myproject member
```

## Troubleshooting

### Enable Debug Mode

```bash
cvm --debug server list
```

### Check Endpoints

```bash
cvm catalog list
```

### Verify Authentication

```bash
cvm token issue
```

### Common Issues

**Issue**: `Missing value auth-url required for auth plugin password`

**Solution**: Ensure you've set `OS_AUTH_URL` or provided `--os-auth-url`

**Issue**: `Authentication failed`

**Solution**: Verify your credentials and ensure the auth URL is correct

**Issue**: `Command not found: cvm`

**Solution**: Ensure the package is installed and your PATH includes the pip bin directory

## Development Setup

For development work:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -r test-requirements.txt

# Run tests
tox

# Run linting
pre-commit run --all-files
```

## Getting Help

- Command help: `cvm help <command>`
- Subcommand help: `cvm <command> <subcommand> --help`
- Documentation: https://console.connectvm.com/
- Support: support@connectvm.com
