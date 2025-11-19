# NetBox FreeIPA Plugin

NetBox plugin for integration with FreeIPA identity management system. View and manage FreeIPA enrolled hosts directly from NetBox.

## Features

- View enrolled hosts from FreeIPA
- Detailed host information (IP, MAC, certificates, SSH keys)
- Automatic background synchronization
- Manual sync option
- REST API support
- Filtering and search

## Compatibility

NetBox v4.0 or later

## Installation

```bash
pip install netbox-freeipa
```

## Configuration

Edit `/opt/netbox/netbox/netbox/configuration.py`:

```python
PLUGINS = ['netbox_freeipa']

PLUGINS_CONFIG = {
    'netbox_freeipa': {
        'freeipa_host': 'ipa.example.com',
        'freeipa_username': 'admin',
        'freeipa_password': 'your-password',
        # Optional settings:
        'freeipa_verify_ssl': True,
        'sync_interval': 300,  # seconds
        'auto_sync_enabled': True,
    }
}
```

Run migrations and restart:

```bash
cd /opt/netbox/netbox
python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

## Usage

Navigate to Plugins > FreeIPA Hosts in NetBox menu.

## REST API

```bash
# List hosts
curl -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/hosts/

# Trigger sync
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/hosts/sync/
```

## Build & Publish

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

## License

Apache License 2.0
