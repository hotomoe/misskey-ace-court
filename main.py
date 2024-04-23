import json
import asyncio

from aiohttp import ClientWebSocketResponse
from mipac.models.notification import NotificationNote
from mipa.ext import commands

COGS = [
    "exts.render"
]

config = json.load(open("./config.json"))

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__()

    async def _connect_channel(self):
        await self.router.connect_channel(['main', 'global'])

    async def on_ready(self, ws: ClientWebSocketResponse):
        print(f'Connected to @{self.user.username}')
        await self._connect_channel()
        for cog in COGS:
            await self.load_extension(cog)

    async def on_reconnect(self, ws: ClientWebSocketResponse):
        print('Disconnected from server. Will try to reconnect.')
        await self._connect_channel()

    async def on_mention(self, notice: NotificationNote):
        print(f"{notice.note.author.username} requested {notice.note.content}")
        await self.progress_command(notice.note)


if __name__ == '__main__':
    bot = MyBot()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.start(config["origin"], config["token"]))