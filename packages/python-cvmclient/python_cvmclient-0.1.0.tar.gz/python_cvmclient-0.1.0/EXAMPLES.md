# ConnectVM CLI Examples

This guide provides practical examples of using the `cvm` command-line interface.

## Authentication

### Using Environment Variables

```bash
# Set credentials
export OS_AUTH_URL=https://cloud.connectvm.com:5000/v3
export OS_USERNAME=myuser
export OS_PASSWORD=mypassword
export OS_PROJECT_NAME=myproject
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_REGION_NAME=RegionOne

# Use cvm commands
cvm server list
```

### Using clouds.yaml

```bash
# Use specific cloud from clouds.yaml
cvm --os-cloud connectvm server list

# Set as default
export OS_CLOUD=connectvm
cvm server list
```

## Server Management

### Creating Servers

```bash
# Basic server creation
cvm server create \
  --flavor m1.small \
  --image ubuntu-20.04 \
  --network private \
  --key-name mykey \
  myserver

# With security groups
cvm server create \
  --flavor m1.medium \
  --image centos-8 \
  --network private \
  --security-group default \
  --security-group web \
  --key-name mykey \
  webserver

# With user data (cloud-init)
cvm server create \
  --flavor m1.small \
  --image ubuntu-20.04 \
  --network private \
  --user-data cloud-init.yaml \
  myserver

# Boot from volume
cvm server create \
  --flavor m1.medium \
  --volume my-volume \
  --network private \
  myserver
```

### Listing and Filtering Servers

```bash
# List all servers
cvm server list

# List with detailed output
cvm server list --long

# Filter by status
cvm server list --status ACTIVE
cvm server list --status ERROR

# Filter by name
cvm server list --name web*

# Output as JSON
cvm server list -f json

# Show specific columns
cvm server list -c ID -c Name -c Status
```

### Server Operations

```bash
# Show server details
cvm server show myserver

# Reboot server (soft)
cvm server reboot myserver

# Reboot server (hard)
cvm server reboot --hard myserver

# Stop server
cvm server stop myserver

# Start server
cvm server start myserver

# Pause server
cvm server pause myserver

# Unpause server
cvm server unpause myserver

# Suspend server
cvm server suspend myserver

# Resume server
cvm server resume myserver

# Resize server
cvm server resize --flavor m1.large myserver
cvm server resize confirm myserver

# Rebuild server
cvm server rebuild --image ubuntu-22.04 myserver

# Delete server
cvm server delete myserver

# Delete multiple servers
cvm server delete server1 server2 server3
```

### Server Snapshots

```bash
# Create image from server
cvm server image create --name myserver-backup myserver

# Show server action history
cvm server event list myserver
```

### Console Access

```bash
# Get console URL
cvm console url show myserver

# Get console log
cvm console log show myserver

# Get console log (last 50 lines)
cvm console log show --lines 50 myserver
```

## Network Management

### Networks and Subnets

```bash
# Create network
cvm network create private-net

# Create subnet
cvm subnet create \
  --network private-net \
  --subnet-range 192.168.1.0/24 \
  --gateway 192.168.1.1 \
  --dns-nameserver 8.8.8.8 \
  private-subnet

# List networks
cvm network list

# List subnets
cvm subnet list

# Show network details
cvm network show private-net

# Delete network
cvm network delete private-net
```

### Routers

```bash
# Create router
cvm router create myrouter

# Set external gateway
cvm router set --external-gateway public myrouter

# Add subnet to router
cvm router add subnet myrouter private-subnet

# List routers
cvm router list

# Show router details
cvm router show myrouter

# Remove subnet from router
cvm router remove subnet myrouter private-subnet

# Delete router
cvm router delete myrouter
```

### Floating IPs

```bash
# Create floating IP
cvm floating ip create public

# List floating IPs
cvm floating ip list

# Associate floating IP with server
cvm server add floating ip myserver 203.0.113.10

# Disassociate floating IP
cvm server remove floating ip myserver 203.0.113.10

# Delete floating IP
cvm floating ip delete 203.0.113.10
```

### Ports

```bash
# List ports
cvm port list

# Create port
cvm port create --network private-net myport

# Show port details
cvm port show myport

# Delete port
cvm port delete myport
```

### Security Groups

```bash
# List security groups
cvm security group list

# Create security group
cvm security group create \
  --description "Web server security group" \
  web-sg

# Add SSH rule
cvm security group rule create \
  --protocol tcp \
  --dst-port 22 \
  --remote-ip 0.0.0.0/0 \
  web-sg

# Add HTTP rule
cvm security group rule create \
  --protocol tcp \
  --dst-port 80 \
  --remote-ip 0.0.0.0/0 \
  web-sg

# Add HTTPS rule
cvm security group rule create \
  --protocol tcp \
  --dst-port 443 \
  --remote-ip 0.0.0.0/0 \
  web-sg

# Allow ICMP (ping)
cvm security group rule create \
  --protocol icmp \
  web-sg

# Allow all traffic from specific security group
cvm security group rule create \
  --remote-group web-sg \
  web-sg

# List security group rules
cvm security group rule list web-sg

# Add security group to server
cvm server add security group myserver web-sg

# Remove security group from server
cvm server remove security group myserver web-sg

# Delete security group
cvm security group delete web-sg
```

## Volume Management

### Creating and Managing Volumes

```bash
# Create volume
cvm volume create --size 10 myvolume

# Create volume from image
cvm volume create \
  --size 20 \
  --image ubuntu-20.04 \
  bootable-volume

# List volumes
cvm volume list

# Show volume details
cvm volume show myvolume

# Extend volume
cvm volume set --size 20 myvolume

# Rename volume
cvm volume set --name newname myvolume

# Delete volume
cvm volume delete myvolume
```

### Attaching Volumes

```bash
# Attach volume to server
cvm server add volume myserver myvolume

# List server volumes
cvm server volume list myserver

# Detach volume
cvm server remove volume myserver myvolume
```

### Volume Snapshots

```bash
# Create snapshot
cvm volume snapshot create \
  --volume myvolume \
  --description "Daily backup" \
  myvolume-snap

# List snapshots
cvm volume snapshot list

# Create volume from snapshot
cvm volume create \
  --snapshot myvolume-snap \
  --size 10 \
  restored-volume

# Delete snapshot
cvm volume snapshot delete myvolume-snap
```

### Volume Backups

```bash
# Create backup
cvm volume backup create \
  --name myvolume-backup \
  myvolume

# List backups
cvm volume backup list

# Restore backup
cvm volume backup restore myvolume-backup

# Delete backup
cvm volume backup delete myvolume-backup
```

## Image Management

```bash
# List images
cvm image list

# List public images
cvm image list --public

# List private images
cvm image list --private

# Show image details
cvm image show ubuntu-20.04

# Create image from file
cvm image create \
  --file ubuntu.qcow2 \
  --disk-format qcow2 \
  --container-format bare \
  --public \
  my-ubuntu

# Download image
cvm image save --file downloaded.qcow2 ubuntu-20.04

# Set image properties
cvm image set \
  --property os_type=linux \
  --property os_distro=ubuntu \
  ubuntu-20.04

# Delete image
cvm image delete my-image
```

## Keypair Management

```bash
# Create keypair
cvm keypair create mykey > mykey.pem
chmod 600 mykey.pem

# Import existing public key
cvm keypair create \
  --public-key ~/.ssh/id_rsa.pub \
  imported-key

# List keypairs
cvm keypair list

# Show keypair details
cvm keypair show mykey

# Delete keypair
cvm keypair delete mykey
```

## Flavor Management

```bash
# List flavors
cvm flavor list

# Show flavor details
cvm flavor show m1.small

# Create flavor (admin only)
cvm flavor create \
  --ram 2048 \
  --disk 20 \
  --vcpus 1 \
  custom.small

# Delete flavor (admin only)
cvm flavor delete custom.small
```

## Identity Management

### Users

```bash
# List users
cvm user list

# Create user
cvm user create \
  --password secret123 \
  --email alice@example.com \
  --project myproject \
  alice

# Show user details
cvm user show alice

# Set user password
cvm user password set alice

# Disable user
cvm user set --disable alice

# Enable user
cvm user set --enable alice

# Delete user
cvm user delete alice
```

### Projects

```bash
# List projects
cvm project list

# Create project
cvm project create \
  --description "Development project" \
  dev-project

# Show project details
cvm project show dev-project

# Delete project
cvm project delete dev-project
```

### Roles

```bash
# List roles
cvm role list

# Assign role to user
cvm role add --user alice --project dev-project member

# Remove role from user
cvm role remove --user alice --project dev-project member

# List role assignments
cvm role assignment list --user alice
```

## Object Storage

### Containers

```bash
# List containers
cvm container list

# Create container
cvm container create mycontainer

# Show container details
cvm container show mycontainer

# Delete container
cvm container delete mycontainer
```

### Objects

```bash
# Upload object
cvm object create mycontainer myfile.txt

# List objects
cvm object list mycontainer

# Download object
cvm object save --file downloaded.txt mycontainer myfile.txt

# Delete object
cvm object delete mycontainer myfile.txt
```

## Quota Management

```bash
# Show project quotas
cvm quota show

# Show quota for specific project (admin)
cvm quota show myproject

# Set quotas (admin)
cvm quota set \
  --instances 20 \
  --cores 40 \
  --ram 81920 \
  myproject
```

## Miscellaneous

### Authentication

```bash
# Get authentication token
cvm token issue

# Show service catalog
cvm catalog list

# Show specific service
cvm catalog show compute
```

### Versions

```bash
# Show API versions
cvm versions show
```

### Limits

```bash
# Show current usage and limits
cvm limits show
```

### Output Formatting

```bash
# Table format (default)
cvm server list -f table

# JSON format
cvm server list -f json

# YAML format
cvm server list -f yaml

# CSV format
cvm server list -f csv

# Value format (for scripting)
cvm server list -f value -c ID -c Name

# Shell format (for eval)
cvm server show myserver -f shell
```

### Debugging

```bash
# Enable debug output
cvm --debug server list

# Show timing information
cvm --timing server list

# Verbose output
cvm --verbose server list
```

## Scripting Examples

### Create Multiple Servers

```bash
#!/bin/bash
for i in {1..5}; do
  cvm server create \
    --flavor m1.small \
    --image ubuntu-20.04 \
    --network private \
    --key-name mykey \
    "web-server-$i"
done
```

### Get All Server IPs

```bash
#!/bin/bash
cvm server list -f value -c Name -c Networks | while read name networks; do
  echo "$name: $networks"
done
```

### Delete All Stopped Servers

```bash
#!/bin/bash
cvm server list --status SHUTOFF -f value -c ID | while read id; do
  cvm server delete "$id"
done
```

### Backup All Volumes

```bash
#!/bin/bash
cvm volume list -f value -c ID -c Name | while read id name; do
  cvm volume backup create --name "${name}-backup-$(date +%Y%m%d)" "$id"
done
```

## Complete Workflow Example

### Deploy a Web Application

```bash
# 1. Create network infrastructure
cvm network create app-network
cvm subnet create --network app-network --subnet-range 10.0.1.0/24 app-subnet
cvm router create app-router
cvm router set --external-gateway public app-router
cvm router add subnet app-router app-subnet

# 2. Create security group
cvm security group create web-sg
cvm security group rule create --protocol tcp --dst-port 22 web-sg
cvm security group rule create --protocol tcp --dst-port 80 web-sg
cvm security group rule create --protocol tcp --dst-port 443 web-sg

# 3. Create keypair
cvm keypair create webkey > webkey.pem
chmod 600 webkey.pem

# 4. Create servers
cvm server create \
  --flavor m1.medium \
  --image ubuntu-20.04 \
  --network app-network \
  --security-group web-sg \
  --key-name webkey \
  webserver1

# 5. Assign floating IP
FLOAT_IP=$(cvm floating ip create public -f value -c floating_ip_address)
cvm server add floating ip webserver1 $FLOAT_IP

# 6. Verify
echo "Web server accessible at: http://$FLOAT_IP"
```
