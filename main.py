import discord
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import youtube_dl
from keep_alive import *
import nacl
import random as rand
import requests


keep_alive()


token = os.environ['TOKEN']
client = commands.Bot(command_prefix = '.')


playlist = []
randoComplimentsList = ['Great choice!', 'Amazing song', 'Beautiful', 'Nice one!', 'This one sounds fabulous']
loop = False

ytdl_options = {'format': 'bestaudio', 'noplaylist': 'True', 'default_search': 'auto'}

ytdl = youtube_dl.YoutubeDL(ytdl_options) 

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# #join
# @client.command()
# async def join(ctx):
#   if not ctx.message.author.voice:
#     await ctx.send(f'**{ctx.message.author}** is not connected to a voice channel')
#     return
#   else:
#     channel = ctx.message.author.voice.channel
#     await channel.connect()

#loop
@client.command()
async def looped(ctx):
  global loop
  loop = not loop

  await ctx.send(f'Looped is now set to **{loop}**')

#play next
def play_next(ctx):
  global loop
  voice = get(client.voice_clients, guild = ctx.guild)

  if playlist:
    if loop:
      playlist.append(playlist[0])
    del playlist[0]
    voice.play(FFmpegPCMAudio(playlist[0][1], **FFMPEG_OPTIONS), after = lambda e: play_next(ctx))
    

#play
@client.command()
async def play(ctx, *, search):

  if not ctx.message.author.voice:
    await ctx.send(f'**{ctx.message.author}** is not connected to a voice channel')
    return
  else:
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    channel = ctx.message.author.voice.channel

    if voice_client == None:
      await channel.connect()
    else:
      await voice_client.move_to(channel)
    
    voice = get(client.voice_clients, guild = ctx.guild)

    if not voice.is_playing() and not voice.is_paused():
      info = ytdl.extract_info(search, download = False)
      try:
        response = requests.get(search)
        URL = info["formats"][0]['url']
        playlist.append((info["title"], URL))
      except Exception as e:
        URL = info["entries"][0]["formats"][0]['url']
        playlist.append((info["entries"][0]["title"], URL))

      voice.play(FFmpegPCMAudio(playlist[0][1], **FFMPEG_OPTIONS), after = lambda e: play_next(ctx))
      voice.is_playing()

      await ctx.send(f'Playing **{playlist[0][0]}**')
    else:
      info = ytdl.extract_info(search, download = False)
      try:
        response = requests.get(search)
        URL = info["formats"][0]['url']
        playlist.append((info["title"], URL))
        await ctx.send(f'**{info["title"]}** added to queue')
      except Exception as e:
        URL = info["entries"][0]["formats"][0]['url']
        playlist.append((info["entries"][0]["title"], URL))
        await ctx.send(f'**{info["entries"][0]["title"]}** added to queue')
      return

#remove from queue
@client.command()
async def remove(ctx, *, num):
  if playlist and num.isdigit() and int(num) > 0 and int(num) < len(playlist):
    await ctx.send(f'Removed **{playlist[int(num)][0]}** from the queue')
    del playlist[int(num)]
  else:
    await ctx.send('Not in range of queue')

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

#help
@client.command()
async def cmds(ctx):
  embed = discord.Embed(title = '**Commands**', descriptions = 'Here are the commands', color = 0xA828D2)
  embed.add_field(name = '.play <name or link>', value = 'Searches for matching song to play or plays from link', inline = False)
  embed.add_field(name = '.pause', value = 'Pauses music if currently playing', inline = False)
  embed.add_field(name = '.resume', value = 'Resumes music', inline = False)
  embed.add_field(name = '.looped', value = 'Enables/disables looped mode (will loop through queue if enabled)', inline = False)
  embed.add_field(name = '.queue', value = 'Shows songs in queue', inline = False)
  embed.add_field(name = '.stop', value = 'Stops playing current song and clears queue', inline = False)
  embed.add_field(name = '.remove <num>', value = 'Removes song at <num>\'s position in the queue', inline = False)
  embed.add_field(name = '.leave', value = '*Yeets* Yeetus Bot out of your voice channel', inline = False)
  embed.set_footer(text = f'Requested by {ctx.author.name}', icon_url = ctx.author.avatar_url)
  await ctx.send(embed = embed)

#stop
@client.command()
async def stop(ctx):
  voice = get(client.voice_clients, guild = ctx.guild)

  if voice.is_playing():
    voice.stop()
    playlist.clear()
    await ctx.send("Stopped")

#queue
@client.command()
async def queue(ctx):
  embed = discord.Embed(title = '**Queue**', description = "", color = 0x21c24c)
  if playlist:
    embed.add_field(name = f'Current: {playlist[0][0]}', value = rand.choice(randoComplimentsList), inline = False)
    for i in range(1, len(playlist)):
      embed.add_field(name = f'{i}. {playlist[i][0]}', value = rand.choice(randoComplimentsList), inline = False)
  else:
    embed.add_field(name = "No songs in queue", value = "Maybe you should add some", inline = True)
  
  embed.set_footer(text = f'Requested by {ctx.author.name}', icon_url = ctx.author.avatar_url)

  await ctx.send(embed = embed)

#leave
@client.command()
async def leave(ctx):
  if ctx.message.author.voice:
    voice = get(client.voice_clients, guild = ctx.guild)
    await voice.disconnect()
    await ctx.send("Yeetus bot has been **yeeted** out of the voice chat")
  else:
    await ctx.send("You have to be connected to the voice channel")

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