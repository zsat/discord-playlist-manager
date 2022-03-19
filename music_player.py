import discord
from discord.ext import commands
import asyncio
import youtube_dl
from datetime import datetime





#
##
###
### MUSIC PLAYER FUNCTIONALITY BELOW
###
### Used this video (https://www.youtube.com/watch?v=jHZlvRr9KxM)
### to get minimum functionality, then built on this to create 
### a much more useful set of commands.
###
### PURPOSE:
###
### Since Rythm bot and others received cease and desists from 
### Youtube, we've no longer had a need to use this bot for its
### original intended purpose, which was to organize playlists
### of songs (using Youtube playlists) so that we can listen to
### music together.
###
### So, I've now written similar functionalities into this bot,
### giving users (my friends and I) a way to still listen to music
### together while building our own playlists from Discord, which
### has been super easy. Since this is a low profile bot, I don't 
### expect Youtube to send me a cease and desist (lol), so it'll
### hopefully work long enough for us to enjoy. Here's to hoping
### that Discord doesn't totally deprecate audio-playing in the 
### near future :)
###
##
#





class music_player(commands.Cog):
    
  ##
  # Initializes some instance variables that either
  #   1. are subject to change throughout the object (the song queue)
  #   2. don't change but are useful for every function (bot, youtube downloader) 
  #       and additions to the bot in the future
  #
  # Past classes in this bot used global variables which was bad practice
  ##
  def __init__(self, bot):
    self.bot = bot
    self.song_queue = []
    self.ydl = youtube_dl.YoutubeDL({'format':'bestaudio'})
    self.FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                            'options':'-vn',
                            'executable':'/usr/local/Cellar/ffmpeg/5.0/bin/ffmpeg'}





  ### Helper class(es)





  ##
  # Yt_song (Youtube Song) object
  # 
  # Stores data about a youtube video.
  # 
  # Goal is to improve readability, writability, and permanence
  # of the code below (permanence = e.g. not having a list of these
  # vars w/ hardcoded instances that would need to change in the future).
  ##
  class Yt_song:
    def __init__(self, title, url, mp3_url, thumbnail_url, duration):
      self.title = title
      self.url = url
      self.mp3_url = mp3_url
      self.thumbnail_url = thumbnail_url
      self.duration = duration





  ### Beginning of callable commands





  ##
  # Connect command
  # 
  # Dependencies:
  #   - needed to `pip install PyNaCl` to be able to connect to voice channels
  # 
  # Bot guaranteed to connect to user's channel, unless major issue
  # 
  # Bot joins vc if not connected, moves to user if in different 
  # channel, otherwise does nothing since already in user's channel
  ##
  @commands.command()
  async def connect(self, ctx):

    if ctx.author.voice is None:
      await ctx.send("you're not in a channel")
    
    voice_channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
      await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
      await ctx.voice_client.move_to(voice_channel)
  




  ##
  # Play command
  # 
  # Functionalities:
  #   - joins user's channel if not in it and start playing music
  #   - plays requested song regardless of queue, does not clear queue
  #   - auto-plays next song in queue if queue isn't empty
  # 
  # Dependencies: 
  #   - had to `brew install ffmpeg` to get the ffmpeg exectuable, whose path we see below. 
  #       manual static download didn't work, was like 74MB and the ffmpeg exe we want is like 400KB
  #   - had to `pip install PyNaCl` for bot to be able to join voice channel
  ##
  @commands.command()
  async def play(self, ctx, url=None):

    ### 1. if user passes no url and queue has songs, play what's in the queue ###

    if url is None:
      if len(self.song_queue) == 0:
        await ctx.reply("you'll need to pass a url or add something to the queue")
      else:
        await self.skip(ctx, index=0)
        return

    ### 2. ensure connected to channel, stop playing current music ###

    await self.connect(ctx)
    ctx.voice_client.stop()
    
    ### 3. start playing song, lots of possible exceptions/errors ###

    try:
      self.current_song = url
      song_info = self.ydl.extract_info(url, download=False)
      source = await discord.FFmpegOpusAudio.from_probe(source=song_info['formats'][0]['url'], **self.FFMPEG_OPTIONS)
      ctx.voice_client.play(source)
      await ctx.send(f"now playing `{song_info['title']}`")
    except Exception as e:
      print(e)
      await ctx.send(f"exception when trying to play: {e}")
      # probably want to try again but we'll code this later

    ### 4. wait until song is finished playing to auto-play the next ###

    while (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
      await asyncio.sleep(1)

    ### 5. autoplay: play next in queue if user hasn't skipped ###
    
    if url == self.current_song and len(self.song_queue) > 0:
      await self.skip(ctx, index=0)
    elif len(self.song_queue) == 0: 
      await ctx.send("nothing left in queue, all done for now.")
    # else user likely skipped to next song, do nothing, all done
  




  ##
  # Queue command
  # 
  # Adds song to the queue if given url, else prints the queue as a dicsord.Embed
  # Provides visual feedback if added song url to queue
  ##
  @commands.command()
  async def queue(self, ctx, url=None):
    
    ### 1. add Yt_song object to queue if given url ###

    if url is not None:
      try:
        song_info = self.ydl.extract_info(url, download=False)
        self.song_queue.append(self.Yt_song(
          title = song_info['title'], 
          url = url, 
          mp3_url = song_info['formats'][0]['url'], 
          thumbnail_url = song_info['thumbnail'], 
          duration = song_info['duration'])
        )
        await ctx.message.add_reaction("👍")
      except Exception as e:
        await ctx.reply(f"exception: {type(e)}")
      return
    
    ### 2. else if nothing in the queue, then do nothing ###

    elif len(self.song_queue) == 0:
      await ctx.reply("there's nothing in the queue")
      return

    ### 3. else queue has items, print queue as a discord.Embed ###

    song_list = ''
    for i, song in enumerate(self.song_queue):
      song_list += f"{i+1}: [{song.title}]({song.url})\n"

    embed = discord.Embed(title='Current song queue')
    embed.add_field(name=f"{len(self.song_queue)} songs", value=song_list)
    embed.set_thumbnail(url=self.song_queue[0].thumbnail_url)
    
    tt = 0 ## total time
    for song in self.song_queue:
      tt += int(song.duration)
    embed.set_footer(text=f"total time: {tt//3600:02d}:{tt//60:02d}:{tt%60:02d}")

    await ctx.reply(embed=embed)
  




  ##
  # Skip command
  # 
  # If queue isn't empty, play next song in queue, 
  # else just stop playing current song.
  #
  # This function is called by the Play command to implement
  # a rudimentary type of auto-play functionality.
  ##
  @commands.command()
  async def skip(self, ctx, index=0):
    
    if len(self.song_queue) == 0:
      ctx.voice_client.stop()
      return

    next_song = self.song_queue.pop(index)
    await self.play(ctx, next_song.url)
  




  ##
  # Disconnect command
  # 
  # Disconnects from voice channel, adds reaction for visual feedback.
  #
  # Bot also disconnects automatically after a few minutes when not running,
  # but it will stay connected as long as bot.py is running, regardless
  # of whether playing music or not.
  ##
  @commands.command()
  async def disconnect(self, ctx):
    await ctx.voice_client.disconnect()
    await ctx.message.add_reaction("👍")
  




  ##
  # Pause command
  # 
  # Pauses music, adds reaction for visual feedback
  ##
  @commands.command()
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.message.add_reaction("⏸️")
  




  ##
  # Resume command
  # 
  # Resumes music, adds reaction for visual feedback
  ##
  @commands.command()
  async def resume(self, ctx):
    ctx.voice_client.resume()
    await ctx.message.add_reaction("▶️")
  
