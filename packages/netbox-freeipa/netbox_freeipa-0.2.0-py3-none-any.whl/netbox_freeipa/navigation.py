"""Navigation menu items for NetBox FreeIPA plugin."""

from netbox.plugins import PluginMenuItem, PluginMenuButton


menu_items = (
    PluginMenuItem(
        link='plugins:netbox_freeipa:freeipahost_list',
        link_text='Hosts',
        permissions=['netbox_freeipa.view_freeipahost'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_freeipa:freeipahost_sync',
                title='Sync All',
                icon_class='mdi mdi-sync',
                permissions=['netbox_freeipa.view_freeipahost']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:netbox_freeipa:freeipadnszone_list',
        link_text='DNS Zones',
        permissions=['netbox_freeipa.view_freeipadnszone'],
    ),
    PluginMenuItem(
        link='plugins:netbox_freeipa:freeipadnsrecord_list',
        link_text='DNS Records',
        permissions=['netbox_freeipa.view_freeipadnsrecord'],
    ),
)
