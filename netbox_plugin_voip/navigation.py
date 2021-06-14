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
        # This is looked up in urls.py
        link="plugins:netbox_plugin_voip:voice-main-page",
        link_text="Voice Plugin",
    ),
)
