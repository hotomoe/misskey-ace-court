import asyncio
import re
import os
from typing import List

from mipac import Note
from mipa.ext import commands
from mipa.ext.commands.bot import Bot
from mipa.ext.commands.context import Context
# from hatesonar import Sonar
from better_profanity import profanity
from objection_engine.renderer import render_comment_list
from objection_engine.beans.comment import Comment


class Render(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
#        self.sonar = Sonar()
        profanity.load_censor_words_from_file('./banlist.txt')
    
    async def async_note(self, notes: List[Note]) -> Note:
        for note in notes:
            yield note
            await asyncio.sleep(0)

    def filter_beginning_mentions(self, match):
        mentions = match[0].strip().split(' ')
        index = next((index for index,x in enumerate(mentions) if x in mentions[:index]), len(mentions))
        message = ' '.join(mentions[index:])
        return message + ' ' if len(message) > 0 else message

    async def render(self, note_id: str, comments: List[Comment]):
        render_comment_list(comment_list=comments, output_filename=f"{note_id}.mp4", music_code="RND", resolution_scale=3, adult_mode=True)

    async def fetch_thread(self, origin: Note) -> List[Note]:
        note = origin
        notes = []
        while note.reply_id is not None:
            note = await self.bot.client.note.action.get(note.reply_id)
            notes.append(note)
            if note.content is None and not note.file_ids:
                return
        notes.reverse()
        return notes
    
    async def fetch_users(self, mentions: List[str]) -> List[str]:
        users = []
        async for mention in self.async_note(mentions):
            user = await self.bot.client.user.action.get(user_id=mention)
            users.append(f"@{user.username}")
        return users
    
    async def sanitize_thread(self, notes: List[Note]) -> List[str]:
        note: Note
        comments = []
        sanitized = 0
        async for note in self.async_note(notes):
            current = note
            previous = None
            if notes.index(note) != 0:
                previous = notes[notes.index(note) - 1]

            try:
                user_mentions = set()
                mentions = await self.fetch_users(current._note["mentions"])

                if previous is not None:
                    user_mentions.update(mention.acct for mention in mentions)
                    user_mentions.add(previous.author.username)
            except:
                pass

            mentions_pattern = "|".join(user_mentions)
            content = re.sub(f'^(@({mentions_pattern}) )+', self.filter_beginning_mentions, note.content)
            content = re.sub(r'(https)\S*', '(링크)', content)

#            sonar_prediction = self.sonar.ping(content)
#            hate_classification = next((x for x in sonar_prediction['classes']  if x['class_name'] == 'hate_speech'), None)
#            if (hate_classification["confidence"] > 0.6):
#                content = '...'
#            content = profanity.censor(content)
#            if hate_classification["confidence"] > 0.8:
#                sanitized + 1
            comment = Comment(user_id=note.author.id, user_name=f"{note.author.name}", text_content=content)
            comments.append(comment)
        if sanitized >= 2:
            return False
        return comments
    
    @commands.mention_command(text="render")
    async def _render(self, ctx: Context) -> None:
        notes = await self.fetch_thread(ctx.message)
        if notes is None:
            return await ctx.message.api.action.reply(f"@{ctx.author.username} => There's followers only note or cannot be viewed on this server.")
        
        comments = await self.sanitize_thread(notes)
        await self.render(ctx.message.id, comments)
        try:
            result = await self.bot.client.drive.files.action.create(
                file=f"{ctx.message.id}.mp4",
                name=f"count-{ctx.message.id}.mp4",
                comment=f"Misskey Ace Court Render Result requested by @{ctx.author.username}",
                is_sensitive=False
            )
        except Exception as e:
            print(e)
            os.remove(f"./{ctx.message.id}.mp4")
            await ctx.message.api.action.reply(f"@{ctx.author.username} => 업로드에 실패했습니다...", visibility="home")
        else:
            os.remove(f"./{ctx.message.id}.mp4")
            await ctx.message.api.action.reply(f"@{ctx.author.username} => 요청하신 동영상이 준비되었습니다!", visibility="home", files=[result])


async def setup(bot: Bot):
    await bot.add_cog(Render(bot))