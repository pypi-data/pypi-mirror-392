===============
ConnectVM CLI
===============

ConnectVM CLI (cvm) is a command-line client for ConnectVM Cloud that brings
the command set for Compute, Identity, Image, Network, Object Store and Block
Storage APIs together in a single shell with a uniform command structure.

The primary goal is to provide a unified shell command structure and a common
language to describe operations in ConnectVM Cloud.

Getting Started
===============

ConnectVM CLI can be installed from PyPI using pip:

.. code-block:: shell

    python3 -m pip install python-cvmclient

You can use ``--help`` or the ``help`` command to get a list of global options
and supported commands:

.. code-block:: shell

    cvm --help
    cvm help

You can also get help for a specific command:

.. code-block:: shell

    cvm server create --help
    cvm help server create

Configuration
=============

ConnectVM CLI must be configured with authentication information in order to
communicate with your ConnectVM Cloud. This configuration can be achieved
via a ``clouds.yaml`` file, a set of environment variables (often shared via an
``openrc`` file), a set of command-line options, or a combination of all three.

Your ConnectVM Cloud dashboard will typically provide either a
``clouds.yaml`` file or ``openrc`` file for you. If using a ``clouds.yaml``
file, ConnectVM CLI expects to find it in one of the following locations:

* If set, the path indicated by the ``OS_CLIENT_CONFIG_FILE`` environment variable
* ``.`` (the current directory)
* ``$HOME/.config/openstack``
* ``/etc/openstack``

The options you should set will depend on the configuration of your cloud and
the authentication mechanism(s) supported. For example, consider a cloud that
supports username/password authentication. Configuration for this cloud using a
``clouds.yaml`` file would look like so:

.. code-block:: yaml

    clouds:
      connectvm:
        auth:
          auth_url: 'https://cloud.connectvm.com:5000/v3'
          project_name: '<project-name>'
          project_domain_name: '<project-domain-name>'
          username: '<username>'
          user_domain_name: '<user-domain-name>'
          password: '<password>'  # (optional)
        region_name: '<region>'

The corresponding environment variables would look very similar:

.. code-block:: shell

    export OS_AUTH_URL=https://cloud.connectvm.com:5000/v3
    export OS_REGION_NAME=<region>
    export OS_PROJECT_NAME=<project-name>
    export OS_PROJECT_DOMAIN_NAME=<project-domain-name>
    export OS_USERNAME=<username>
    export OS_USER_DOMAIN_NAME=<user-domain-name>
    export OS_PASSWORD=<password>  # (optional)

Likewise, the corresponding command-line options would look very similar::

    cvm \
    --os-auth-url https://cloud.connectvm.com:5000/v3 \
    --os-region <region> \
    --os-project-name <project-name> \
    --os-project-domain-name <project-domain-name> \
    --os-username <username> \
    --os-user-domain-name <user-domain-name> \
    [--os-password <password>]

.. note::

    If a password is not provided above (in plaintext), you will be
    interactively prompted to provide one securely.

Contributing
============

For information on contributing to ConnectVM CLI, please contact
support@connectvm.com
