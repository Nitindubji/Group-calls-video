import os

import wget
import ytthumb
from pyrogram import Client, filters
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL
from lib.helpers.decorators import sudo_users
from pytgcalls.exceptions import NoActiveGroupCall

from .join import opengc
from .piped_stream import pstream

ydl_opts = {
    'format': 'best',
    'keepvideo': True,
    'prefer_ffmpeg': False,
    'geo_bypass': True,
    'outtmpl': '%(title)s.%(ext)s',
    'quite': True
}


@Client.on_message(filters.command("video"))
@sudo_users
async def video(client, message):
    query = " ".join(message.command[1:])
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        results[0]["url_suffix"]
    except Exception as e:
        print(e)
    try:
        video = message.text
        quality = "sd"
        thumbnail = ytthumb.thumbnail(
        video=video,
        quality=quality
        )
    except Exception as e: 
        print(e)
        msg = await message.reply_photo(photo=thumbnail)
    try:
        msg = await message.reply("```Downloading...```")
        with YoutubeDL(ydl_opts) as ytdl:
            ytdl_data = ytdl.extract_info(link, download=True)
            file_name = ytdl.prepare_filename(ytdl_data)
    except Exception as e:
        return await msg.edit(f'**Error:** {e}')
    try:
        preview = wget.download(thumbnail)
    except Exception:
        pass
    await msg.edit("```Uploading to telegram server...```")
    await message.reply_video(
        file_name,
        duration=int(ytdl_data["duration"]),
        thumb=preview,
        caption=ytdl_data['title'])
    try:
        os.remove(file_name)
        os.remove(preview)
        await msg.delete()
    except Exception as e:
        print(e)


@Client.on_message(filters.command("music"))
@sudo_users
async def music(client, message):
    user_mention = message.from_user.mention
    input = message.text.split(None, 2)[1:]
    msg = await message.reply("```Downloading...```")
    try:
       if input[0] == "stream":
           query = input[1]
       else:
           try:
              query = " ".join(message.command[1:])
           except BaseException:
              pass
    except BaseException:
       pass
    try:
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        results[0]["url_suffix"]
    except Exception as e:
        await msg.edit(f"**Error:** ```{e}```")
    preview = wget.download(thumbnail)
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=False)
        audio_file = ydl.prepare_filename(info_dict)
        ydl.process_info(info_dict)
    if input[0] == "stream":
        try:
           await pstream(message.chat.id, audio_file, True)
        except NoActiveGroupCall:
           await msg.edit("**No active call!**\n```Starting Group call...```")
           await opengc(client, message)
           await pstream(message.chat.id, audio_file, True)
        await msg.edit(f"**Streamed by: {user_mention}**\n**Title:** ```{title}```")
    else:
        await msg.edit("```Uploading to telegram server...```")
        await message.reply_audio(
            audio_file,
            duration=int(info_dict["duration"]),
            thumb=preview,
            caption=info_dict['title'])
        try:
            os.remove(audio_file)
            os.remove(preview)
            await msg.delete()
        except Exception as e:
            print(e)
