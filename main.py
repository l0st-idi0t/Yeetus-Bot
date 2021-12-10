import discord
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
from keep_alive import *

keep_alive()


token = os.environ['TOKEN']
client = commands.Bot(command_prefix = '.')


#join
@client.command()
async def join(ctx):
  if not ctx.message.author.voice:
    await ctx.send(f'**{ctx.message.author}** is not connected to a voice channel')
    return
  else:
    channel = ctx.message.author.voice.channel
    await channel.connect()

#play
@client.command()
async def play(ctx, *, search):
  ytdl_options = {'format': 'bestaudio', 'noplaylist': 'True', 'default_search': 'auto'}

  ytdl = youtube_dl.YoutubeDL(ytdl_options) 

  FFMPEG_OPTIONS = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

  voice = get(client.voice_clients, guild = ctx.guild)

  if not voice.is_playing():
    info = ytdl.extract_info(search, download = False)
    URL = info["entries"][0]["formats"][0]['url']
    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    voice.is_playing()
    await ctx.send(f'Playing **{info["entries"][0]["title"]}**')
  else:
    await ctx.send("Playing")
    return
    
#pause
@client.command()
async def pause(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)

  if not voice.is_paused():
      voice.pause()
      await ctx.send('Paused')
  else:
    await ctx.send('Nothing playing')

#resume
@client.command()
async def resume(ctx):
  voice = get(client.voice_clients, guild = ctx.guild)

  if voice.is_paused():
    voice.resume()
    await ctx.send("Resumed")
  else:
    await ctx.send("Nothing paused")

#stop
@client.command()
async def stop(ctx):
  voice = get(client.voice_clients, guild = ctx.guild)

  if voice.is_playing():
    voice.stop()
    await ctx.send("Stopped")

#leave
@client.command()
async def leave(ctx):
  voice = get(client.voice_clients, guild = ctx.guild)
  await voice.disconnect()
  await ctx.send("Yeetus bot has been **yeeted** out of the voice chat")

#on connect
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#log msg delete
@client.event
async def on_message_delete(message):
  if message.author.id != client.user.id:
      author = message.author
      content = message.content
      channel = message.channel
      logchannel = discord.utils.get(author.guild.channels, name = 'logs')
      if logchannel is None:
          logchannel = await author.guild.create_text_channel('logs')
      embed = discord.Embed(title = f'{author} deleted a message in {channel}', description = "", color = 0x4CBEF8)
      if message.attachments != []:
        embed.add_field(name = "Deleted Message", value = message.attachments[0], inline = True)
        embed.set_image(url = message.attachments[0])
      else:
        embed.add_field(name = "Deleted Message", value = content, inline = True)
      await logchannel.send(embed = embed)

#log edit
@client.event
async def on_message_edit(before, after):
  author = before.author
  channel = before.channel
  embed = discord.Embed(title = f'{author} edited a message in {channel}', description = "", color = 0xcc0e0e)
  if before.attachments != []: 
    embed.add_field(name = "Original Message: ", value = f'{before.content} {str(before.attachments[0])}', inline = True)
    embed.set_image(url = before.attachments[0])
  else:
    embed.add_field(name = "Original Message: ", value = before.content, inline = True)
  embed.add_field(name = "Edited Message: ", value = after.content, inline = True)
  logchannel = discord.utils.get(author.guild.channels, name = 'logs')
  if logchannel is None:
      logchannel = await author.guild.create_text_channel('logs')
  await logchannel.send(embed = embed)

#run
if __name__ == "__main__":
  client.run(token)