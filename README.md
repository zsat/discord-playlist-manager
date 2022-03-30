# discord-playlist-manager

> This Discord bot has 2 main funtionalities: (1) allowing you to manage the playlists of a Youtube channel straight from Discord, and (2) joining voice calls and playing requested music.

---

## Playlist Management Functionality

It functions like any other Discord bot, just type in these functions with a "~" in front to control your music:

- `addsong` : adds a song to a given playlist
- `connectyt` : enables read *and* write operations
- `createplaylist` : makes a new playlist
- `deleteplaylist` : deletes a given playlist
- `dumpplaylist` : copies songs from an external playlist to one of the bot's
- `getlink` : returns the link to specific playlist
- `getsongs` : returns the songs of a playlist
- `getplaylists` : returns all playlists
- `getyt` : returns link to channel page
- `movesong` : moves a song from one place in a playlist to another
- `removesong` : removes a song from a given playlist

***Argument formats are in music.py***

An example of `getplaylists` and `getsongs`, you'll notice that you can iterate over pages of songs/playlists by reacting with the arrows at the bottom. You might also notice the "No more reactions can be made here" footer, which pops up after 30 seconds indicating that the function isn't listening for reactions anymore.

<img src="/readmeimgs/getplaylists.png" width="35%">  <img src="/readmeimgs/getsongs.png" width="35%">

---

## Music Player Functionality

<img src="/readmeimgs/invc.png" width="15%">

You can play requested songs, or add them to the queue to be auto-played later. The bot will handle the rest. This functionality was added because Youtube had sent cease and desists to popular audio-playing bots (like Rythm) that forced them to shut down. This pretty much rendered the playlist management functionality useless, so I created this set of functions so that my friends and I could again listen to music together.

- `connect`: connects bot to user's voice channel
- `disconnect`: disconnects bot from user's voice channel
- `play`: auto-connects to channel, plays a song if passed a Youtube url, else tries to play next song in queue
- `queue`: adds a song to the queue if passed a url argument, else returns the current queue
- `skip`: skips current song, auto-plays next song in queue
- `pause`: pauses current song
- `resume`: resumes current song if paused

***Argument formats are in music_player.py***

An example of the most common `play` use case:

<img src="/readmeimgs/playsong.png" width="50%">

An example of `queue` and the auto-play output that is outputted when new songs start playing, also notice the total time counter in the queue:

<img src="/readmeimgs/queue.png" width="40%">

---

## How to set it up:
- Create a discord bot using Discord's API [here](https://discord.com/developers/applications) and obtain your "Build-A-Bot" token.
- Create a Google Application [here](https://console.developers.google.com/apis/credentials). [This](https://www.youtube.com/watch?v=-QMg39gK624) short series will help.
- Download all 3 .py files, read all comments, and replace all filepaths and keys as necessary.
- In your command line window, `pip install` the following:
    - `discord`
    - `google-auth-oauthlib`
    - `google-auth-python-client`
    - `PyNaCl` (for joinging vc's)
- Read through all the comments to make sure everything is good to go, add the bot to your server, then run `% python3 bot.py`.

---

## Q&A:

>What's its purpose?
- There are (were) many Discord bots that will play songs in voice channels, but there wasn't any easy way for my friends and I to organize what we want to play, so I created this bot.


>Why on Github and not on Discord's bot list?
- It's mostly just intended for me to use with my friends, and Youtube is sending cease and desists to bot creators that play their music
- So that anyone can use the code for their own bot / functions.
