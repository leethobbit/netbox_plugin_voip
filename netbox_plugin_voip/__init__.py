from .extras.plugins import PluginConfig
from .version import __version__


class VoicePluginConfig(PluginConfig):
    name = 'netbox_plugin_voip'
    verbose_name = 'Voice'
    description = 'Voice plugin for NetBox'
    version = __version__
    author = 'Dan King'
    author_email = 'test@test.com'
    required_settings = []
    default_settings = {}


config = VoicePluginConfig # noqa
