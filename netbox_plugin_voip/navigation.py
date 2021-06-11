"""
from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_newplugin:mylink',
        link_text='MyLink',
        buttons=(
            PluginMenuButton('home', 'Button A', 'mdi mdi-plus-thick-info', ButtonColorChoices.BLUE),
        )
    ),
)
"""
from extras.plugins import PluginMenuItem


menu_items = (
    PluginMenuItem(
        link="plugins:netbox_plugin_voip:netbox_plugin_voip",
        link_text="Voice Plugin",
    ),
)
