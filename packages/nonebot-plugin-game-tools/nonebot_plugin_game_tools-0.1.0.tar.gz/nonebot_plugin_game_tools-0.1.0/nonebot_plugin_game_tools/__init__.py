from nonebot import get_plugin_config, on_command
from nonebot.plugin import PluginMetadata

from nonebot_plugin_game_tools.config import Config

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_game_tools",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

ping = on_command("ping")


@ping.handle()
async def _():
    await ping.send("pong v1.0.11")
