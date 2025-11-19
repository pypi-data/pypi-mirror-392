# NetBox FreeIPA Plugin

NetBox plugin for integration with FreeIPA identity management system. View and manage FreeIPA enrolled hosts, DNS zones, and records directly from NetBox.

## Features

- View enrolled hosts from FreeIPA
- DNS zones and records management
- Detailed host information (FQDN, SSH keys, descriptions)
- **Automatic background synchronization** (hosts, DNS zones, and DNS records)
- Manual sync option via Web UI and API
- REST API support
- Filtering and search
- **High-performance bulk operations** for large installations

## Compatibility

NetBox v4.0 or later (v4.2+ recommended for automatic background synchronization)

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

**Important:** For automatic background synchronization to work, ensure the `netbox-rq` worker is running:

```bash
# Check status
sudo systemctl status netbox-rq

# View worker logs
sudo journalctl -u netbox-rq -f
```

## Usage

Navigate to Plugins > FreeIPA in NetBox menu to access:
- **Hosts** - View and manage FreeIPA enrolled hosts
- **DNS Zones** - View DNS zones from FreeIPA
- **DNS Records** - View DNS records associated with zones

### Automatic Synchronization

The plugin automatically synchronizes all data (hosts, DNS zones, and records) every 5 minutes by default (configurable via `sync_interval`). Check the Jobs section in NetBox admin to monitor synchronization status.

## REST API

```bash
# List hosts
curl -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/hosts/

# List DNS zones
curl -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/dns-zones/

# List DNS records
curl -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/dns-records/

# Trigger manual sync for hosts
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/hosts/sync/

# Trigger manual sync for DNS zones
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/dns-zones/sync/

# Trigger manual sync for DNS records
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/dns-records/sync/

# Trigger full sync (all data types)
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
     https://netbox.example.com/api/plugins/freeipa/sync/all/
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
