"""Navigation menu items for NetBox FreeIPA plugin."""

from netbox.plugins import PluginMenuItem, PluginMenuButton


menu_items = (
    PluginMenuItem(
        link='plugins:netbox_freeipa:freeipahost_list',
        link_text='FreeIPA Hosts',
        permissions=['netbox_freeipa.view_freeipahost'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_freeipa:freeipahost_sync',
                title='Sync with FreeIPA',
                icon_class='mdi mdi-sync',
                permissions=['netbox_freeipa.view_freeipahost']
            ),
        )
    ),
)
